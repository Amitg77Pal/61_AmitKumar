import streamlit as st
import os
import tempfile
from faster_whisper import WhisperModel
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Configuration
st.set_page_config(page_title="SOAPNote AI", page_icon="🩺", layout="wide")

st.title("🩺 SOAPNote AI")
st.markdown("### Doctor Dictation to Structured Clinical Notes")

# Sidebar for Config
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Required for SOAP structuring step.")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
model_size = st.sidebar.selectbox("Whisper Model Size", ["tiny", "base", "small", "medium", "large-v2"], index=1)
device = st.sidebar.selectbox("Device", ["cpu", "cuda"], index=0)
use_mock_llm = st.sidebar.checkbox("Enable Mock LLM (No API Key required)", value=False, help="Use dummy data for testing UI without OpenAI API.")

# Caching the Whisper model to avoid reloading
@st.cache_resource
def load_model(size, device):
    return WhisperModel(size, device=device, compute_type="int8")

# Transcription Function
def transcribe_audio(model, audio_path):
    segments, info = model.transcribe(audio_path, beam_size=5)
    transcript = ""
    for segment in segments:
        transcript += segment.text + " "
    return transcript.strip()

# SOAP Schema
class SOAPNote(BaseModel):
    Subjective: str = Field(description="Patient's subjective report of symptoms, history, and complaints.")
    Objective: str = Field(description="Objective findings, vital signs, physical exam results, labs.")
    Assessment: str = Field(description="Diagnosis or differential diagnosis based on findings.")
    Plan: str = Field(description="Treatment plan, medications, follow-up, and further testing.")

# Structuring Function
def structure_soap(transcript, model_name="gpt-3.5-turbo", use_mock=False):
    if use_mock:
        return {
            "Subjective": "Patient describes symptoms consistent with the transcript (Mock Data). No acute distress reported.",
            "Objective": "Vitals within normal limits. Physical exam reveals no significant abnormalities (Mock Data).",
            "Assessment": " likely viral upper respiratory infection vs allergies (Mock Data).",
            "Plan": "Supportive care, hydration, rest. Follow up if symptoms worsen (Mock Data)."
        }

    if not os.environ.get("OPENAI_API_KEY"):
        st.error("Please enter your OpenAI API Key in the sidebar.")
        return None
    
    try:
        llm = ChatOpenAI(model=model_name, temperature=0)
        parser = JsonOutputParser(pydantic_object=SOAPNote)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful medical assistant. Extract a structured SOAP note from the dictation.\n{format_instructions}\nDisclaimer: For clinical documentation assistance only."),
            ("user", "Dictation: {transcript}")
        ])
        chain = prompt | llm | parser
        return chain.invoke({"transcript": transcript, "format_instructions": parser.get_format_instructions()})
    except Exception as e:
        st.error(f"Error in LLM processing: {e}")
        return None

# Main UI
uploaded_file = st.file_uploader("Upload Doctor Dictation (MP3, WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")
    
    if st.button("Generate SOAP Note"):
        with st.spinner("Loading Whisper model..."):
            model = load_model(model_size, device)
            
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
            
        try:
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio(model, tmp_path)
            
            st.subheader("📝 Transcript")
            st.write(transcript)
            
            with st.spinner("Structuring SOAP Note (LLM)..."):
                soap_note = structure_soap(transcript, use_mock=use_mock_llm)
                
            if soap_note:
                st.subheader("📋 Structured SOAP Note")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Subjective**")
                    st.info(soap_note.get("Subjective", ""))
                    st.markdown("**Assessment**")
                    st.info(soap_note.get("Assessment", ""))
                with col2:
                    st.markdown("**Objective**")
                    st.info(soap_note.get("Objective", ""))
                    st.markdown("**Plan**")
                    st.info(soap_note.get("Plan", ""))
                
                with st.expander("View Raw JSON"):
                    st.json(soap_note)
                    
        finally:
            os.remove(tmp_path)
