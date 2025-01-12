import streamlit as st
import json
from datetime import datetime
import pandas as pd

# Set page config
st.set_page_config(layout="wide")

# Custom CSS to style the events
st.markdown("""
<style>
    .event-container {
        background-color: #9D7FDB;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    .date-header {
        font-size: 24px;
        font-weight: bold;
        margin: 20px 0 10px 0;
    }
    .time-header {
        font-size: 18px;
        color: #333;
        margin: 10px 0;
    }
    .stButton button {
        background-color: transparent;
        border: 1px solid #9D7FDB;
        color: #9D7FDB;
    }
</style>
""", unsafe_allow_html=True)

def load_events():
    # Sample event data
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

def display_event(event):
    html = f"""
        <div class="event-container">
            <h3>{event['event_name']}</h3>
            <p>{event['event_location']}</p>
            <p>{event['event_description']}</p>
            <p>{event['type']}</p>
        </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def main():
    st.title("Event Scheduler")
    
    # Load events
    events = load_events()
    
    # Group events by date
    events_by_date = {}
    for event_id, event in events.items():
        date = event['event_date']
        if date not in events_by_date:
            events_by_date[date] = []
        events_by_date[date].append(event)
    
    # Sort dates
    sorted_dates = sorted(events_by_date.keys())
    
    # Display events grouped by date
    for date in sorted_dates:
        # Display date header
        st.markdown(f'<div class="date-header">{date}</div>', unsafe_allow_html=True)
        
        # Group events by time for this date
        events_by_time = {}
        for event in events_by_date[date]:
            time = event['event_time']
            if time not in events_by_time:
                events_by_time[time] = []
            events_by_time[time].append(event)
        
        # Sort times
        sorted_times = sorted(events_by_time.keys())
        
        for time in sorted_times:
            # Display time header
            formatted_time = datetime.strptime(time, '%H:%M:%S').strftime('%H:%M')
            st.markdown(f'<div class="time-header">{formatted_time}</div>', unsafe_allow_html=True)
            
            # Create columns for events at this time
            cols = st.columns(len(events_by_time[time]))
            for idx, event in enumerate(events_by_time[time]):
                with cols[idx]:
                    display_event(event)

    # Add event button
    st.markdown("[Go to Event Adder](streamlit_app)")

if __name__ == "__main__":
    main()