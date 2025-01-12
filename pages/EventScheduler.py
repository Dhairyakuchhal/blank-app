import streamlit as st
from datetime import datetime

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Event Scheduler",
)

def load_events():
    return {
    "event_1": {
        "event_name": "LIT - QC THINGY",
        "event_date": "2025-01-12",
        "event_time": "10:00:00",
        "event_location": "Lecture Hall Complex",
        "event_description": "A literary quizzing event with word games, literary puzzles, and quizzing challenges. Teams of 3.",
        "type": "QC",
        "priority": 4
    },
    "event_2": {
        "event_name": "Symphony of Words and Melodies",
        "event_date": "2025-01-12",
        "event_time": "17:00:00",
        "event_location": "Red Square Area (Near Central Library), IIT Delhi",
        "event_description": "An evening of musical performances and poetry presented by Music Club, Literary Club, and Hindi Samiti in collaboration with Literati.  Includes chai.",
        "type": "MUSIC",
        "priority": 9
    },
    "event_3": {
        "event_name": "19th Edition of IITPD",
        "event_date": "2025-03-08",
        "event_time": "NULL",
        "event_location": "IIT Delhi Campus",
        "event_description": "19th edition of IITPD, an Asian Parliamentary Debate tournament during the annual Tryst fest at IIT Delhi.  The event includes fun activities and concerts.",
        "type": "DEBSOC",
        "priority": 3
    },
    "event_4": {
        "event_name": "Bounce Softly, or Carry a Big CHIMP",
        "event_date": "2025-01-11",
        "event_time": "09:00:00",
        "event_location": "LHC, IITD",
        "event_description": "A quiz covering Crime, History, Internet, Media, and Politics.  Team size up to 3 members; IITD students only.  Related to POL100.",
        "type": "QC",
        "priority": 4
    },
    "event_5": {
        "event_name": "Ghazal Writing Workshop",
        "event_date": "2025-01-17",
        "event_time": "15:00:00",
        "event_location": "NULL",
        "event_description": "A workshop on Ghazal writing, exploring Urdu poetry, led by Mr. Mahender Kumar.",
        "type": "LITRARY",
        "priority": 10
    },
    "event_6": {
        "event_name": "Literati '25 Presents: Two Quizzes",
        "event_date": "2025-01-12",
        "event_time": "09:00:00",
        "event_location": "Room C01, Old Academic Block, IIIT Delhi",
        "event_description": "Two quizzes: Credible India Quiz (India-focused) and Veni Vidi Quizzi (History and Mythology with Alt History).  Open to participants under 25.",
        "type": "QC",
        "priority": 4
    }
}

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