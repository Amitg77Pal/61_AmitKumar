import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from faster_whisper import WhisperModel
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Configuration
MODEL_SIZE = "tiny"
AUDIO_PATH = "SOAPNote_AI/data/sample_dictation.mp3"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"

def transcribe_audio(audio_path, model_size="tiny", device="cpu", compute_type="int8"):
    print(f"Loading Whisper model: {model_size}...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    
    print(f"Transcribing {audio_path}...")
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    transcript = ""
    for segment in segments:
        print(f"Segment: {segment.text}")
        transcript += segment.text + " "
    
    return transcript.strip()

class SOAPNote(BaseModel):
    Subjective: str = Field(description="Patient's subjective report of symptoms, history, and complaints.")
    Objective: str = Field(description="Objective findings, vital signs, physical exam results, labs.")
    Assessment: str = Field(description="Diagnosis or differential diagnosis based on findings.")
    Plan: str = Field(description="Treatment plan, medications, follow-up, and further testing.")

def structure_soap_note(transcript, model_name="gpt-3.5-turbo"):
    # Check for API Key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n[WARN] OPENAI_API_KEY not set. Skipping LLM step.")
        return None

    llm = ChatOpenAI(model=model_name, temperature=0)
    parser = JsonOutputParser(pydantic_object=SOAPNote)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful medical assistant. Extract a structured SOAP note from the dictation.\n{format_instructions}"),
        ("user", "Dictation: {transcript}")
    ])
    
    chain = prompt | llm | parser
    return chain.invoke({"transcript": transcript, "format_instructions": parser.get_format_instructions()})

def main():
    if not os.path.exists(AUDIO_PATH):
        print(f"Audio file not found at {AUDIO_PATH}. Please run generate_sample_audio.py first.")
        return

    try:
        transcript = transcribe_audio(AUDIO_PATH, MODEL_SIZE, DEVICE, COMPUTE_TYPE)
        print(f"\nFull Transcript: {transcript}")
        
        soap = structure_soap_note(transcript)
        if soap:
            print("\nSOAP Note JSON:")
            print(soap)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
