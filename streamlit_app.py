import streamlit as st
import requests

# Backend API URL (replace with your actual backend URL)
BACKEND_URL = "http://127.0.0.1:8000/upload_event"

# Streamlit App
st.title("IIT Delhi Event Scheduler")

# Text input
st.subheader("Enter Event Details")
user_input = st.text_area("Paste the event description here:", height=200)

# Submit button
if st.button("Submit"):
    if user_input.strip():
        # Prepare the data payload
        payload = {"event_text": user_input}
        
        # Send to backend
        try:
            response = requests.post(BACKEND_URL, json=payload)
            
            if response.status_code == 200:
                st.success("Event successfully uploaded to the backend!")
            else:
                st.error(f"Failed to upload. Error: {response.text}")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
    else:
        st.warning("Please enter event details before submitting.")