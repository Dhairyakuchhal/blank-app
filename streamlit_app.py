import streamlit as st
import json
from pathlib import Path

# Path to store events and club priorities
EVENTS_FILE = "events.json"
PRIORITIES_FILE = "club_priorities.json"

def load_events():
    """Load existing events from the JSON file."""
    if Path(EVENTS_FILE).exists():
        with open(EVENTS_FILE, "r") as file:
            return json.load(file)
    return []

def save_events(events):
    """Save events to the JSON file."""
    with open(EVENTS_FILE, "w") as file:
        json.dump(events, file, indent=4)

def save_priorities(priorities):
    """Save club priorities to the JSON file."""
    with open(PRIORITIES_FILE, "w") as file:
        json.dump(priorities, file, indent=4)

# Load existing events
existing_events = load_events()

# Streamlit app layout
st.title("IIT Delhi Event Scheduler")
st.write("Paste the text of the Instagram post below:")

# Navigation link to event scheduler page
st.markdown("[Go to Event Scheduler](./EventScheduler)")

# Input form for Instagram post text
with st.form(key="insta_post_form"):
    insta_post_text = st.text_area("Instagram Post Text:", placeholder="Paste the text of the post here")
    submit_button = st.form_submit_button(label="Add Event")

if submit_button:
    if insta_post_text:
        new_event = {
            "post_text": insta_post_text,
        }
        existing_events.append(new_event)
        save_events(existing_events)

        st.success("Event has been added successfully!")
    else:
        st.error("Please paste the text of the Instagram post.")

# Display existing events
st.subheader("Scheduled Events")
if existing_events:
    for i, event in enumerate(existing_events, start=1):
        st.write(f"**Event {i}:** {event['post_text']}")
else:
    st.write("No events scheduled yet.")

# Section for setting club priorities
st.subheader("Set Club Priorities")
st.write("The higher the priority, the more important the event")
clubs = [
    "CLASS", "DEBSOC", "QC", "SPIC MACAY", "DRAMA", "DANCE",
    "HINDI SAMITI", "MUSIC", "LITRARY", "DESIGN", "PFC", "FACC", "RDV"
]

# Input fields for priorities
priorities = {}
for club in clubs:
    priorities[club] = st.slider(f"Priority for {club}", 1, 13, 6)

# Save priorities button
if st.button("Save Priorities"):
    save_priorities(priorities)
    st.success("Club priorities have been saved successfully!")
    st.json(priorities)
