import google.generativeai as genai
from PIL import Image
import json
import logging
import os
import re
import pandas as pd
from datetime import datetime, timedelta

def generate_csv():
    def process_single_json(file_path):
        """
        Process a single JSON file containing a list of posts.

        Parameters:
        file_path: str - Path to the JSON file to process

        Returns:
        DataFrame containing 'text' and 'image_path'
        """
        data = []

        # Read and parse the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                json_content = json.load(f)

                # Iterate over each post in the list
                for post in json_content:
                    if 'post_text' in post:
                        data.append({
                            'text': post['post_text'].strip(),
                            'image_path': ''  # No image path is provided in this format
                        })

            except json.JSONDecodeError:
                print(f"Error decoding JSON file: {file_path}")

        return pd.DataFrame(data)

    JSON_FILE_PATH = "./posts.json"  # Path to your JSON file
    OUTPUT_CSV_PATH = "./simple_events_database.csv"

    # Process the JSON file
    events_df = process_single_json(JSON_FILE_PATH)

    # Save the DataFrame to a CSV file
    events_df.to_csv(OUTPUT_CSV_PATH, index=False)

    print(f"Processed {len(events_df)} posts and saved to {OUTPUT_CSV_PATH}")
    print("\nSample Output:")
    print(events_df.head())



def create_sorted_data():

    # Set up logging with more detail
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    def load_event_types():
        """Load event types from the JSON file."""
        try:
            with open('./club_priorities.json', 'r') as f:
                event_types = json.load(f)
            logger.info("Loaded event types from club_priorities.json")
            return event_types
        except Exception as e:
            logger.error(f"Failed to load event types: {str(e)}")
            raise

    def setup_gemini():
        """Configure Gemini API with the stored key."""
        try:
            api_key = 'AIzaSyDzkfskUX-YeZTlE7FugNr1xLPOQEGNQ8M'
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Test the connection
            test_response = model.generate_content("Test connection")
            if not test_response:
                raise ValueError("Failed to get response from Gemini API")

            return model
        except Exception as e:
            logger.error(f"Failed to setup Gemini: {str(e)}")
            raise

    def load_image(image_path):
        """Load and validate image file."""
        try:
            if pd.isna(image_path) or not isinstance(image_path, str):
                return None

            # Define allowed extensions
            allowed_extensions = ['.jpg', '.jpeg']

            # Try different potential paths
            potential_paths = [
                image_path,
                f"./{image_path}",
                f"./{image_path}"
            ]

            for path in potential_paths:
                # Check if the file exists and has an allowed extension
                if os.path.exists(path) and any(path.lower().endswith(ext) for ext in allowed_extensions):
                    logger.info(f"Loading image from: {path}")
                    return Image.open(path)

            logger.warning(f"Could not find image at any expected location: {potential_paths}")
            return None

        except Exception as e:
            logger.warning(f"Failed to load image {image_path}: {str(e)}")
            return None

    def analyze_event(model, text, image_path, event_types):
        """Extract event information using Gemini API."""
        logger.info(f"Analyzing event with text: {text[:100]}...")

        prompt = """Analyze this event information and extract the following details. If information is not available, respond with NULL.
        You must respond in EXACTLY this format, with the exact numbering and labels:

        1. Name: [extract or generate a clear event name]
        2. Date: [date in YYYY-MM-DD format]
        3. Time: [time in HH:MM:SS format]
        4. Location: [venue or location]
        5. Description: [brief event description]
        6. Type: [one of: CLASS, LAB, TUT, DEBSOC, QC, SM, DRAMA, DANCE, HS, MUSIC, LITRARY, DESIGN, PFC, FACC, RDV]

        BE SURE TO RESPOND WITH EXACTLY THIS FORMAT, using the numbers 1-6 and exact labels as shown above.
        """

        try:
            # Create messages array
            messages = [prompt, f"\nText content to analyze:\n{text}"]

            # Add image if available
            image = load_image(image_path)
            if image:
                logger.info("Including image in analysis")
                response = model.generate_content([prompt, image, text])
            else:
                logger.info("No image available, analyzing text only")
                response = model.generate_content(messages)

            if not response or not response.text:
                raise ValueError("Empty response from Gemini")

            logger.info(f"Raw Gemini response:\n{response.text}")
            return parse_response(response.text, event_types)

        except Exception as e:
            logger.error(f"Error in analyze_event: {str(e)}")
            return {
                "event_name": "NULL",
                "event_date": "NULL",
                "event_time": "NULL",
                "event_location": "NULL",
                "event_description": "NULL",
                "type": "NULL",
                "priority": None
            }

    def parse_response(response_text, event_types):
        """Parse Gemini's response into structured data."""
        info = {
            "event_name": "NULL",
            "event_date": "NULL",
            "event_time": "NULL",
            "event_location": "NULL",
            "event_description": "NULL",
            "type": "NULL",
            "priority": None
        }

        try:
            logger.debug(f"Parsing response:\n{response_text}")

            lines = [line.strip() for line in response_text.split('\n') if line.strip()]

            for line in lines:
                if ':' not in line:
                    continue

                key, value = [part.strip() for part in line.split(':', 1)]
                value = value.replace('[', '').replace(']', '').strip()

                if not value or value.lower() == 'null':
                    continue

                if '1.' in key:  # Name
                    info['event_name'] = value
                elif '2.' in key:  # Date
                    try:
                        date_obj = datetime.strptime(value, '%Y-%m-%d')
                        info['event_date'] = '2025-' + date_obj.strftime('%m-%d')
                    except:
                        # Try to parse other date formats
                        try:
                            for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y']:
                                try:
                                    date_obj = datetime.strptime(value, fmt)
                                    info['event_date'] = '2025-' + date_obj.strftime('%m-%d')
                                    break
                                except:
                                    continue
                        except:
                            pass
                elif '3.' in key:  # Time
                    try:
                        # Try multiple time formats
                        for fmt in ['%H:%M:%S', '%H:%M', '%I:%M %p', '%I:%M%p']:
                            try:
                                time_obj = datetime.strptime(value, fmt)
                                info['event_time'] = time_obj.strftime('%H:%M:%S')
                                break
                            except:
                                continue
                    except:
                        pass
                elif '4.' in key:  # Location
                    info['event_location'] = value
                elif '5.' in key:  # Description
                    info['event_description'] = value
                elif '6.' in key:  # Type
                    event_type = value.upper()
                    if event_type in event_types:
                        info['type'] = event_type
                        info['priority'] = event_types[event_type]
                    else:
                        info['type'] = 'NULL'
                        info['priority'] = None

            logger.info(f"Parsed information: {json.dumps(info, indent=2)}")
            return info

        except Exception as e:
            logger.error(f"Failed to parse response: {str(e)}")
            return info

    def process_events():
        """Main function to process events and create JSON file."""
        try:
            # Load event types from the JSON file
            event_types = load_event_types()

            # Initialize Gemini
            model = setup_gemini()

            # Read CSV file
            csv_path = './simple_events_database.csv'
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV file not found at {csv_path}")

            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} events from CSV")

            if len(df) == 0:
                raise ValueError("CSV file is empty")

            # Process events
            events_dict = {}
            for idx, row in df.iterrows():
                logger.info(f"\nProcessing event {idx + 1}/{len(df)}")

                if pd.isna(row['text']):
                    logger.warning(f"Skipping event {idx + 1}: No text content")
                    continue

                # Analyze event
                event_info = analyze_event(model, row['text'], row.get('image_path'), event_types)

                # Add to dictionary if we got any non-NULL values
                if any(value != "NULL" for value in event_info.values()):
                    events_dict[f"event_{idx + 1}"] = event_info
                else:
                    logger.warning(f"Event {idx + 1} produced all NULL values, but adding to output anyway")
                    events_dict[f"event_{idx + 1}"] = event_info

            # Verify we have data before saving
            if not events_dict:
                raise ValueError("No events were successfully processed")

            # Save to JSON file
            output_path = './sorted_data.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(events_dict, f, indent=4, ensure_ascii=False)

            logger.info(f"Successfully created {output_path} with {len(events_dict)} events")
            return events_dict

        except Exception as e:
            logger.error(f"Failed to process events: {str(e)}")
            raise


    try:
        processed_events = process_events()
        print("\nSample of processed events:")
        print(json.dumps(dict(list(processed_events.items())[:2]), indent=4))
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        print(f"\nError details: {str(e)}")



def get_class_schedule():

    # Directory containing the downloaded files
    search_dir = "./"

    # Load the Kerberos ID from the JSON file
    kerberos_file = "kerberos.json"
    with open(kerberos_file, "r", encoding="utf-8") as file:
        kerberos_data = json.load(file)
        search_string = kerberos_data["kerberos_id"]

    # File extensions to include in the search (optional)
    valid_extensions = [".html", ".shtml", ".txt"]  # Add or modify extensions as needed

    list_of_enrolled_courses = []
    pattern = r"2402-([A-Z]+\d+[A-Z]?)"

    # Perform the search
    for root, _, files in os.walk(search_dir):
        for file_name in files:
            if any(file_name.endswith(ext) for ext in valid_extensions):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        if search_string in content:
                            list_of_enrolled_courses.append(re.search(pattern, file_name).group(1))
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    def filter_course_codes(course_codes):
        course_dict = {}
        for code in course_codes:
            base_code = code[:6]
            third_block = code[6:]
            if base_code not in course_dict or len(third_block) > len(course_dict[base_code][6:]):
                course_dict[base_code] = code
        return list(course_dict.values())

    list_of_enrolled_courses = filter_course_codes(list_of_enrolled_courses)

    def get_course_timing(course_name, file_path):

        for index, row in df.iterrows():

            if str(row['Course Name']).split('-')[-1] == course_name:
                return row['Timing']
            if str(row['Course Name']).split('-')[-1] + 'A' == course_name:
                return row['Timing']
            if str(row['Course Name']).split('-')[-1] + 'B' == course_name:
                next_row = df.iloc[index + 1]
                return next_row['Timing']

        return "Course not found."

    def convert_schedule(schedule):
        day_map = {
            "M": "Monday",
            "T": "Tuesday",
            "W": "Wednesday",
            "Th": "Thursday",
            "F": "Friday",
            "Sa": "Saturday",
            "Su": "Sunday"
        }
        sessions = schedule.split(",")
        expanded_schedule = []
        for session in sessions:
            parts = session.strip().split(" ")
            days_part = parts[0]
            time_part = " ".join(parts[1:])
            i = 0
            while i < len(days_part):
                if i + 1 < len(days_part) and days_part[i:i+2] == "Th":
                    expanded_schedule.append((day_map['Th'], time_part))
                    i += 2
                else:
                    expanded_schedule.append((day_map[days_part[i]], time_part))
                    i += 1
        return expanded_schedule

    # Generate JSON events for the next month
    events = {}
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    event_id = 1

    for course_name in list_of_enrolled_courses:
        # Skip courses if the third character is not 'L'
        if len(course_name) < 3 or course_name[2] != 'L':
            continue

        file_path = "Courses_Offered.csv"
        df = pd.read_csv(file_path)
        timing = get_course_timing(course_name, file_path)
        if timing == "Course not found.":
            continue
        if str(timing) != 'nan':
            schedule = convert_schedule(timing)

            # Generate events for the next month
            for day_name, time_range in schedule:
                current_date = start_date
                while current_date <= end_date:
                    if current_date.strftime("%A") == day_name:
                        start_time = time_range.split("-")[0]  # Use only the start time
                        events[f"event_{event_id}"] = {
                            "event_name": course_name,
                            "event_date": current_date.strftime("%Y-%m-%d"),
                            "event_time": f"{start_time.strip()}:00",
                            "event_location": "LHC",
                            "event_description": "",
                            "type": "class",
                            "priority": 0
                        }
                        event_id += 1
                    current_date += timedelta(days=1)
        if str(timing) == 'nan':
            events[f"event_{event_id}"] = {
                "event_name": course_name,
                "event_date": "NULL",
                "event_time": "NULL",
                "event_location": "LHC",
                "event_description": "",
                "type": "class",
                "priority": 0
            }
            event_id += 1

    # Save to a JSON file
    output_file = "class_events.json"
    with open(output_file, "w") as json_file:
        json.dump(events, json_file, indent=4)

    print(f"Class events for the next month have been saved to {output_file}.")



def get_merged_events():

    # Load data from both JSON files
    with open('class_events.json', 'r') as class_file:
        class_events = json.load(class_file)

    with open('sorted_data.json', 'r') as sorted_file:
        sorted_events = json.load(sorted_file)

    # Merge the events from both dictionaries
    merged_events = {}
    all_events = list(sorted_events.values()) + list(class_events.values())

    # Rename events sequentially
    for idx, event in enumerate(all_events, start=1):
        merged_events[f"event_{idx}"] = event

    # Save the merged data into a new JSON file
    with open('merged_events.json', 'w') as merged_file:
        json.dump(merged_events, merged_file, indent=4)

    print("Events merged and saved as 'merged_events.json'.")
