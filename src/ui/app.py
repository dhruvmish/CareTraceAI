"""
CareTrace AI - Streamlit UI
Production-grade interface for multi-agent healthcare system
Includes timeline editing (delete/edit events)
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.ingestion_agent import IngestionAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.safety_agent import SafetyAgent
from src.agents.pattern_agent import PatternAgent
from src.agents.population_agent import PopulationAgent
from src.config import AUDIO_DIR, PRESCRIPTIONS_DIR
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="CareTrace AI",
    page_icon="🏥",
    layout="wide"
)

# Initialize agents (cached)
@st.cache_resource
def init_agents():
    """Initialize all agents once"""
    memory = MemoryAgent()
    ingestion = IngestionAgent()
    safety = SafetyAgent(memory)
    pattern = PatternAgent(memory)
    population = PopulationAgent(memory)

    return {
        "memory": memory,
        "ingestion": ingestion,
        "safety": safety,
        "pattern": pattern,
        "population": population
    }

try:
    agents = init_agents()
except Exception as e:
    st.error(f"❌ Failed to initialize system: {str(e)}")
    st.info("Please ensure Qdrant is running and .env is configured correctly.")
    st.stop()

# Header
st.title("🏥 CareTrace AI")
st.caption("Multi-Agent Healthcare Safety System | Powered by Qdrant")

st.markdown("---")

# Sidebar: Patient Selection
st.sidebar.header("Patient Selection")

demo_patients = {
    "patient_001": "Sarah Johnson (Age 54, Diabetes + Hypertension)",
    "patient_002": "Rajesh Kumar (Age 62, Heart Disease)",
    "patient_003": "Maria Garcia (Age 45, Asthma)",
    "patient_004": "Ahmed Ali (Age 58, Chronic Pain)",
    "patient_005": "Li Wei (Age 51, Depression)"
}

selected_patient = st.sidebar.selectbox(
    "Select Patient",
    options=list(demo_patients.keys()),
    format_func=lambda x: demo_patients[x]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Demo Features:**
- 📤 Upload audio/prescriptions
- 🔍 Check medication safety
- 📊 View symptom patterns
- 👥 Find similar patients
- ✏️ **Edit/Delete timeline events**
""")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Patient Timeline",
    "📤 Upload Data",
    "⚠️ Safety Check",
    "📊 Pattern Analysis",
    "👥 Population Insights"
])

# TAB 1: Patient Timeline (with Edit/Delete)
with tab1:
    st.header("Patient History Timeline")

    # Add refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_timeline"):
            st.cache_resource.clear()
            st.rerun()

    history = agents["memory"].get_patient_history(selected_patient, limit=50)

    if not history:
        st.warning("No history recorded for this patient yet.")
        st.info("Use the 'Upload Data' tab to add symptom reports or prescriptions.")
    else:
        st.success(f"**{len(history)} events** in timeline")

        # Display as timeline with edit/delete options
        for idx, event in enumerate(history):
            event_type = event.get("event_type", "unknown")
            timestamp = event.get("timestamp", "")
            text = event.get("text", "")
            point_id = event.get("point_id", f"event_{idx}")  # Fallback to index if no point_id

            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = timestamp

            # Create expandable event card
            if event_type == "symptom":
                with st.expander(f"🗣️ **Symptom Report** - {date_str}", expanded=(idx < 3)):
                    st.write(text)

                    # Only show edit/delete if point_id exists
                    if point_id and not point_id.startswith("event_"):
                        # Edit/Delete buttons
                        col1, col2, col3 = st.columns([1, 1, 8])
                        with col1:
                            if st.button("✏️ Edit", key=f"edit_{point_id}_{idx}"):
                                st.session_state[f"editing_{point_id}"] = True
                        with col2:
                            if st.button("🗑️ Delete", key=f"delete_{point_id}_{idx}"):
                                if agents["memory"].delete_event(point_id):
                                    st.success("Event deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete event")

                        # Edit form (if editing)
                        if st.session_state.get(f"editing_{point_id}", False):
                            st.markdown("---")
                            new_text = st.text_area(
                                "Edit symptom description",
                                value=text,
                                key=f"edit_text_{point_id}_{idx}"
                            )

                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.button("💾 Save", key=f"save_{point_id}_{idx}"):
                                    updated_event = event.copy()
                                    updated_event["text"] = new_text
                                    updated_event.pop("point_id", None)  # Remove point_id from payload

                                    if agents["memory"].update_event(point_id, updated_event):
                                        st.success("Event updated!")
                                        st.session_state[f"editing_{point_id}"] = False
                                        st.rerun()
                                    else:
                                        st.error("Failed to update event")

                            with col_cancel:
                                if st.button("❌ Cancel", key=f"cancel_{point_id}_{idx}"):
                                    st.session_state[f"editing_{point_id}"] = False
                                    st.rerun()
                    else:
                        st.caption("⚠️ Legacy event - cannot edit/delete")

            elif event_type == "prescription":
                drugs = event.get("drugs", [])
                drugs_str = ", ".join(drugs) if drugs else "None extracted"

                with st.expander(f"💊 **Prescription** - {date_str}", expanded=(idx < 3)):
                    st.write(f"**Drugs:** {drugs_str}")
                    st.write(f"**Details:** {text[:200]}{'...' if len(text) > 200 else ''}")

                    # Only show edit/delete if point_id exists
                    if point_id and not point_id.startswith("event_"):
                        # Edit/Delete buttons
                        col1, col2, col3 = st.columns([1, 1, 8])
                        with col1:
                            if st.button("✏️ Edit", key=f"edit_{point_id}_{idx}"):
                                st.session_state[f"editing_{point_id}"] = True
                        with col2:
                            if st.button("🗑️ Delete", key=f"delete_{point_id}_{idx}"):
                                if agents["memory"].delete_event(point_id):
                                    st.success("Event deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete event")

                        # Edit form (if editing)
                        if st.session_state.get(f"editing_{point_id}", False):
                            st.markdown("---")
                            new_text = st.text_area(
                                "Edit prescription text",
                                value=text,
                                key=f"edit_text_{point_id}_{idx}"
                            )
                            new_drugs = st.text_input(
                                "Edit drugs (comma-separated)",
                                value=", ".join(drugs),
                                key=f"edit_drugs_{point_id}_{idx}"
                            )

                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.button("💾 Save", key=f"save_{point_id}_{idx}"):
                                    updated_event = event.copy()
                                    updated_event["text"] = new_text
                                    updated_event["drugs"] = [d.strip() for d in new_drugs.split(",") if d.strip()]
                                    updated_event.pop("point_id", None)  # Remove point_id from payload

                                    if agents["memory"].update_event(point_id, updated_event):
                                        st.success("Event updated!")
                                        st.session_state[f"editing_{point_id}"] = False
                                        st.rerun()
                                    else:
                                        st.error("Failed to update event")

                            with col_cancel:
                                if st.button("❌ Cancel", key=f"cancel_{point_id}_{idx}"):
                                    st.session_state[f"editing_{point_id}"] = False
                                    st.rerun()
                    else:
                        st.caption("⚠️ Legacy event - cannot edit/delete")

# TAB 2: Upload Data
with tab2:
    st.header("Upload Patient Data")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎤 Upload Audio (Symptom Report)")

        audio_files = list(AUDIO_DIR.glob("*.wav")) + list(AUDIO_DIR.glob("*.mp3"))

        if not audio_files:
            st.warning("No audio files found in data/audio/")
            st.info("🧑 **HUMAN ACTION REQUIRED:** Please add audio files to data/audio/")
        else:
            selected_audio = st.selectbox(
                "Select audio file",
                options=audio_files,
                format_func=lambda x: x.name
            )

            if st.button("Process Audio", key="process_audio"):
                with st.spinner("Transcribing audio..."):
                    try:
                        event = agents["ingestion"].process_audio(selected_audio, selected_patient)
                        point_id = agents["memory"].store_event(event)
                        st.success(f"✅ Audio processed and stored!\n\nTranscription: {event['text']}")
                        st.info("Go to 'Patient Timeline' tab to see the new entry")
                    except Exception as e:
                        st.error(f"❌ Failed: {str(e)}")

    with col2:
        st.subheader("📄 Upload Prescription Image")

        rx_files = list(PRESCRIPTIONS_DIR.glob("*.jpg")) + list(PRESCRIPTIONS_DIR.glob("*.png"))

        if not rx_files:
            st.warning("No prescription images found in data/prescriptions/")
            st.info("🧑 **HUMAN ACTION REQUIRED:** Please add prescription images to data/prescriptions/")
        else:
            selected_rx = st.selectbox(
                "Select prescription image",
                options=rx_files,
                format_func=lambda x: x.name
            )

            if st.button("Process Prescription", key="process_rx"):
                with st.spinner("Running OCR..."):
                    try:
                        event = agents["ingestion"].process_prescription(selected_rx, selected_patient)
                        point_id = agents["memory"].store_event(event)
                        st.success(f"✅ Prescription processed!\n\n**Drugs Found:** {', '.join(event['drugs'])}")
                        st.info("Go to 'Patient Timeline' tab to see the new entry")
                    except Exception as e:
                        st.error(f"❌ Failed: {str(e)}")

    st.markdown("---")
    st.subheader("✍️ Manual Entry")

    manual_type = st.radio("Entry Type", ["Symptom", "Prescription"])
    manual_text = st.text_area("Enter text")

    if manual_type == "Prescription":
        manual_drugs = st.text_input("Drug names (comma-separated)")
        drugs_list = [d.strip() for d in manual_drugs.split(",")] if manual_drugs else []
    else:
        drugs_list = []

    if st.button("Submit Manual Entry"):
        if manual_text:
            event = agents["ingestion"].create_manual_event(
                patient_id=selected_patient,
                event_type=manual_type.lower(),
                text=manual_text,
                drugs=drugs_list
            )
            agents["memory"].store_event(event)
            st.success("✅ Entry saved!")
            st.info("Go to 'Patient Timeline' tab to see the new entry")

# TAB 3: Safety Check
with tab3:
    st.header("⚠️ Medication Safety Check")
    
    new_drug = st.text_input("Enter new medication to check", placeholder="e.g., Aspirin")
    
    if st.button("Run Safety Check"):
        if not new_drug:
            st.warning("Please enter a medication name")
        else:
            with st.spinner("Checking interactions..."):
                result = agents["safety"].check_new_medication(selected_patient, new_drug)
                
                if result["safe"]:
                    st.success(f"✅ {result['message']}")
                    if result["current_drugs"]:
                        st.info(f"**Current medications:** {', '.join(result['current_drugs'])}")
                else:
                    st.error(f"⚠️ {result['message']}")
                    
                    st.subheader("Interaction Details")
                    for interaction in result["interactions"]:
                        severity = interaction["severity"].upper()
                        color = {"MILD": "🟡", "MODERATE": "🟠", "SEVERE": "🔴"}.get(severity, "⚪")
                        
                        st.warning(f"""
{color} **{severity} Interaction**

**Drugs:** {interaction['drug_a']} ↔ {interaction['drug_b']}

**Explanation:** {interaction['explanation']}

**Evidence:** {interaction.get('evidence', 'N/A')}
                        """)

# TAB 4: Pattern Analysis
with tab4:
    st.header("📊 Symptom Pattern Detection")
    
    if st.button("Analyze Patterns"):
        with st.spinner("Detecting patterns..."):
            result = agents["pattern"].detect_recurring_symptoms(selected_patient)
            
            if not result.get("has_patterns"):
                st.info(result["message"])
            else:
                st.warning(result["message"])
                
                for pattern in result["recurring_symptoms"]:
                    with st.expander(f"🔁 '{pattern['symptom_keyword']}' - {pattern['occurrence_count']} occurrences"):
                        st.write("**Dates:**")
                        for date in pattern["dates"]:
                            try:
                                dt = datetime.fromisoformat(date)
                                st.write(f"- {dt.strftime('%Y-%m-%d %H:%M')}")
                            except:
                                st.write(f"- {date}")
                        
                        st.write("\n**Full Reports:**")
                        for report in pattern["reports"]:
                            st.text(f"• {report}")

# TAB 5: Population Insights
with tab5:
    st.header("👥 Similar Patient Analysis")
    
    if st.button("Find Similar Patients"):
        with st.spinner("Searching population..."):
            result = agents["population"].find_similar_patients(selected_patient, limit=3)
            
            if not result.get("found_similar"):
                st.info(result["message"])
            else:
                st.success(result["message"])
                
                for similar in result["similar_patients"]:
                    score = similar.get("similarity_score", 0)
                    
                    with st.expander(f"Patient {similar['patient_id']} (Similarity: {score:.2%})"):
                        st.write(f"**Age:** {similar.get('age', 'N/A')}")
                        st.write(f"**Conditions:** {', '.join(similar.get('conditions', []))}")
                        st.write(f"**Medications:** {', '.join(similar.get('medications', []))}")
                        st.write(f"**Symptoms:** {', '.join(similar.get('symptoms', []))}")

# Footer
st.markdown("---")
st.caption("CareTrace AI | Multi-Agent Healthcare Safety System | NOT a diagnostic tool")