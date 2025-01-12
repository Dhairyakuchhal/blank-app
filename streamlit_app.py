import streamlit as st
import json
from pathlib import Path

# Path to store events and club priorities
EVENTS_FILE = "events.json"
PRIORITIES_FILE = "club_priorities.json"
KERBEROS_FILE = 'kerberos.json'

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

def remove_event(event_index):
    """Remove an event by index."""
    events = load_events()
    if 0 <= event_index < len(events):
        events.pop(event_index)
        save_events(events)

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


with st.form(key="kerberos_post_form"):
    kerberos_id = st.text_area("Kerberos ID for Classes Data", placeholder="Please enter here")
    kerberos_id_submit_button = st.form_submit_button(label="Save")
if kerberos_id_submit_button:
    if kerberos_id:
        kb_id = {
            "kerberos_id": kerberos_id,
        }
        
        with open(KERBEROS_FILE, "w") as file:
            json.dump(kb_id, file, indent=4)

        st.success("Kerberos has been added successfully!")
    else:
        st.error("Please paste the text of the Instagram post.")
# Display existing events and option to remove them
st.subheader("Scheduled Events")
if existing_events:
    for i, event in enumerate(existing_events, start=1):
        st.write(f"**Event {i}:** {event['post_text']}")
        
        # Button to remove the event
        if st.button(f"Remove Event {i}", key=f"remove_{i}"):
            remove_event(i - 1)  # Remove the event at the given index
            st.rerun()  # Rerun the app to refresh the event list

else:
    st.write("No events scheduled yet.")

# Section for setting club priorities
st.subheader("Set Club Priorities")
clubs = [
    "CLASS", "LAB", "TUT", "DEBSOC", "QC", "SM", "DRAMA", "DANCE",
    "HS", "MUSIC", "LITRARY", "DESIGN", "PFC", "FACC", "RDV"
]

# Input fields for priorities
priorities = {}
for club in clubs:
    priorities[club] = st.slider(f"Priority for {club}", 1, 14, 5)

# Save priorities button
if st.button("Save Priorities"):
    save_priorities(priorities)
    st.success("Club priorities have been saved successfully!")
    st.json(priorities)
