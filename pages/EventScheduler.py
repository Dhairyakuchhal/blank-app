import streamlit as st
from datetime import datetime
import functions
import json

# Set page config
st.set_page_config(
    layout="wide",
    page_title="EventConnect",
)

def load_events():
    with open('merged_events.json', 'r') as merged_file:
        merged_events = json.load(merged_file)
    return merged_events

def format_time(time_str):
    if time_str == "NULL":
        return "TBA"
    try:
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        return time_obj.strftime('%H:%M')
    except ValueError:
        try:
            time_obj = datetime.strptime(time_str, '%H:%M')
            return time_obj.strftime('%H:%M')
        except ValueError:
            return time_str

def display_event_card(event, is_unannounced=False):
    bg_color = "#4A4A4A" if is_unannounced else "#9D7FDB"
    with st.container():
        st.markdown(
            f"""
            <div style="
                background-color: {bg_color};
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
                color: white;
            ">
                <h3 style="margin: 0 0 10px 0; font-size: 1.3rem;">{event['event_name']}</h3>
                <p style="margin: 5px 0;">{event['event_location']}</p>
                <p style="margin: 5px 0;">{event['event_description']}</p>
                <p style="margin: 5px 0;">{event['type']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def main():
    # Page title
    st.title("Event Scheduler")
    
    # Load events
    events = load_events()
    
    # Separate events
    unannounced_events = []
    announced_events = {}
    
    for event_id, event in events.items():
        if event['event_date'] == "NULL" or event['event_time'] == "NULL":
            unannounced_events.append(event)
        else:
            date = event['event_date']
            if date not in announced_events:
                announced_events[date] = {}
            
            time = event['event_time']
            if time not in announced_events[date]:
                announced_events[date][time] = []
            announced_events[date][time].append(event)
    
    # Display unannounced events
    if unannounced_events:
        st.subheader("Unannounced Events", divider="orange")
        cols = st.columns(3)  # Adjust number based on desired cards per row
        for idx, event in enumerate(unannounced_events):
            with cols[idx % 3]:
                display_event_card(event, is_unannounced=True)
    
    # Display announced events
    for date in sorted(announced_events.keys()):
        st.subheader(date, divider="gray")
        
        for time in sorted(announced_events[date].keys()):
            time_display = format_time(time)
            st.text(time_display)
            
            cols = st.columns(3)  # Adjust number based on desired cards per row
            events_at_time = announced_events[date][time]
            for idx, event in enumerate(events_at_time):
                with cols[idx % 3]:
                    display_event_card(event)

if __name__ == "__main__":
    main()