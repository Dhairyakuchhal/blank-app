import streamlit as st
import json
from pathlib import Path

# Path to store events
EVENTS_FILE = "events.json"

def load_events():
    """Load existing events from the JSON file."""
    if Path(EVENTS_FILE).exists():
        with open(EVENTS_FILE, "r") as file:
            return json.load(file)
    return []

# Load events
events = load_events()

# Event Scheduler Page
st.title("Event Scheduler")
st.write("Here are the scheduled events:")

if events:
    # Display events
    for i, event in enumerate(events, start=1):
        st.write(f"""
        **Event {i}**  
        **Post Text:** {event.get('post_text', 'N/A')}  
        """)
else:
    st.write("No events scheduled yet.")
