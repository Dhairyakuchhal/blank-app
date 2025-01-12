import streamlit as st
import json
import datetime
from datetime import datetime as dt
import pandas as pd

# Set page config
st.set_page_config(layout="wide", page_title="Event Scheduler", initial_sidebar_state="collapsed")

# Custom CSS for styling
st.markdown("""
<style>
    .event-card {
        background-color: #9d7fdb;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        color: white;
        width: 280px !important;
        display: inline-block;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .date-header {
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 10px 0;
        color: white;
    }
    .time-header {
        font-size: 16px;
        color: #999;
        margin: 10px 0;
    }
    .events-container {
        display: flex;
        gap: 20px;
    }
    /* Custom styling for dark theme */
    .stApp {
        background-color: #1E1E1E;
    }
    .stSlider {
        margin-bottom: 2rem;
    }
    /* Adjust column gaps */
    .row-widget.stHorizontalBlock {
        gap: 1rem !important;
        padding: 0.5rem 0;
    }
    /* Hide Streamlit's default padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_events():
    # Your JSON data
    events_data = {
        "event_1": {
            "event_name": "Event 1",
            "event_date": "2020-01-01",
            "event_time": "12:00:00",
            "event_location": "Location 1",
            "event_description": "Description 1",
            "type": "club"
        },
        "event_3": {
            "event_name": "Event 3",
            "event_date": "2020-01-01",
            "event_time": "12:00:00",
            "event_location": "Location 1",
            "event_description": "Description 1",
            "type": "club"
        },
        "event_4": {
            "event_name": "Event 4",
            "event_date": "2020-01-01",
            "event_time": "12:00:00",
            "event_location": "Location 4",
            "event_description": "Description 1",
            "type": "club"
        },
        "event_5": {
            "event_name": "Event 5",
            "event_date": "2020-01-01",
            "event_time": "12:00:00",
            "event_location": "Location 4",
            "event_description": "Description 1",
            "type": "club"
        },
        "event_2": {
            "event_name": "Event 2",
            "event_date": "2020-01-02",
            "event_time": "12:00:00",
            "event_location": "Location 2",
            "event_description": "Description 2",
            "type": "club 2"
        }
    }
    return events_data

def create_event_card(event):
    return {
        "name": event['event_name'],
        "location": event['event_location'],
        "description": event['event_description'],
        "type": event['type']
    }

def display_event_cards(events_list, selected_index, visible_cards=3):
    total_events = len(events_list)
    
    # Calculate which events to show based on slider position
    start_idx = selected_index
    end_idx = min(start_idx + visible_cards, total_events)
    
    # Create columns for visible events
    cols = st.columns(visible_cards)
    
    # Display visible events
    for i, col in enumerate(cols):
        idx = start_idx + i
        if idx < total_events:
            event = events_list[idx]
            with col:
                st.markdown(f"""
                    <div class="event-card">
                        <h2 style="margin-top: 0; font-size: 1.5rem; margin-bottom: 1rem;">{event['name']}</h2>
                        <p style="margin-bottom: 0.5rem;">{event['location']}</p>
                        <p style="margin-bottom: 0.5rem;">{event['description']}</p>
                        <p style="margin-bottom: 0;">{event['type']}</p>
                    </div>
                """, unsafe_allow_html=True)

def main():
    st.title("Event Scheduler")
    
    # Load events
    events = load_events()
    
    # Convert events to DataFrame for easier manipulation
    events_df = pd.DataFrame.from_dict(events, orient='index')
    events_df['datetime'] = pd.to_datetime(events_df['event_date'] + ' ' + events_df['event_time'])
    
    # Sort events by date and time
    events_df = events_df.sort_values('datetime')
    
    # Group events by date
    grouped_events = events_df.groupby(events_df['event_date'])
    
    # Number of visible cards at once
    visible_cards = 3
    
    # Display events grouped by date
    for date, group in grouped_events:
        # Format date header
        date_obj = dt.strptime(date, '%Y-%m-%d')
        st.markdown(f"<div class='date-header'>{date_obj.strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)
        
        # Group events by time within each date
        time_grouped = group.groupby('event_time')
        
        for time, events_at_time in time_grouped:
            st.markdown(f"<div class='time-header'>{time}</div>", unsafe_allow_html=True)
            
            # Convert events to list for easier handling
            events_list = [create_event_card(event) for _, event in events_at_time.iterrows()]
            total_events = len(events_list)
            
            # Only show slider if there are more events than visible cards
            if total_events > visible_cards:
                selected_index = st.slider(
                    f"Navigate events for {time}",
                    0,
                    max(0, total_events - visible_cards),
                    0,
                    1,
                    key=f"slider_{date}_{time}".replace(" ", "_").replace(":", "_")
                )
            else:
                selected_index = 0
            
            # Display the events
            display_event_cards(events_list, selected_index, visible_cards)

if __name__ == "__main__":
    main()