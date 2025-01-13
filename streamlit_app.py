import streamlit as st
import json
from pathlib import Path
import functions
import pandas as pd
import google.generativeai as genai
from PIL import Image
import os
import logging
from datetime import datetime, timedelta
import logging
import os
import re
import time


# Path to store events and club priorities
EVENTS_FILE = "posts.json"
PRIORITIES_FILE = "club_priorities.json"
KERBEROS_FILE = 'kerberos.json'

def load_events():
    """Load existing events from the JSON file."""
    try:
        if Path(EVENTS_FILE).exists():
            with open(EVENTS_FILE, "r") as file:
                return json.load(file)
    except json.JSONDecodeError:
        # Log error and/or delete corrupted file
        if Path(EVENTS_FILE).exists():
            Path(EVENTS_FILE).unlink()  # Delete corrupted file
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
    return functions.remove_event_and_regenerate(event_index)

def load_kerberos():
    """Load existing kerberos ID from the JSON file."""
    if Path(KERBEROS_FILE).exists():
        try:
            with open(KERBEROS_FILE, "r") as file:
                data = json.load(file)
                return data.get("kerberos_id", "")
        except json.JSONDecodeError:
            return ""
    return ""

# Load existing events
existing_events = load_events()
# Streamlit app layout
st.title("EventConnect")
st.write("Paste the text of the event post below:")

# Navigation link to event scheduler page
st.markdown("[Go to Event Scheduler](./EventScheduler)")


current_kerberos = load_kerberos()

with st.form(key="kerberos_post_form"):
    st.subheader("Kerberos ID Management")
    
    if current_kerberos:
        st.info(f"Current Kerberos ID: {current_kerberos}")
        kerberos_id = st.text_input("Enter new Kerberos ID to replace current one:", key="new_kerberos")
    else:
        kerberos_id = st.text_input("Enter Kerberos ID (Compulsory):", key="new_kerberos")
    
    col1, col2 = st.columns(2)
    with col1:
        submit_button = st.form_submit_button(label="Save Kerberos ID")
    with col2:
        remove_button = st.form_submit_button(label="Remove Kerberos ID", type="secondary")

if submit_button:
    if kerberos_id:
        # Save new kerberos ID
        kb_id = {
            "kerberos_id": kerberos_id,
        }
        
        with open(KERBEROS_FILE, "w") as file:
            json.dump(kb_id, file, indent=4)

        st.success("Kerberos ID has been saved successfully!")
        st.rerun()
    else:
        st.error("Please enter a Kerberos ID")

if remove_button:
    if functions.remove_kerberos_and_classes():
        st.success("Kerberos ID and associated classes have been removed successfully!")
        st.rerun()
    else:
        st.error("Failed to remove Kerberos ID and classes")

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
    functions.generate_csv()
    functions.create_sorted_data()
    functions.get_class_schedule()
    functions.get_merged_events()




st.subheader("Scheduled Events")
if existing_events:
    for i, event in enumerate(existing_events, start=1):
        st.write(f"**Event {i}:** {event['post_text']}")
        
        # Button to remove the event
        if st.button(f"Remove Event {i}", key=f"remove_{i}"):
            success = remove_event(i - 1)
            if success:
                st.success(f"Event {i} removed successfully!")
                st.rerun()
            else:
                st.error(f"Failed to remove Event {i}")
else:
    st.write("No events scheduled yet.")

# Section for setting club priorities
st.subheader("Set Club Priorities")
clubs = [
    "CLASS", "DEBSOC", "QC", "SM", "DRAMA", "DANCE",
    "HS", "MUSIC", "LITRARY", "DESIGN", "PFC", "FACC", "RDV"
]

# Input fields for priorities
priorities = {}
for club in clubs:
    priorities[club] = st.slider(f"Priority for {club}", 1, 12, 6)

# Save priorities button
if st.button("Save Priorities"):
    save_priorities(priorities)
    st.success("Club priorities have been saved successfully!")
    st.json(priorities)
