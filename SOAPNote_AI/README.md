# SOAPNote AI

## Project Overview
SOAPNote AI is an automated system that converts doctor dictations into structured SOAP (Subjective, Objective, Assessment, Plan) clinical notes. It utilizes OpenAI's Whisper (via `faster-whisper`) for state-of-the-art speech recognition and an LLM (via LangChain) to extract and format the clinical information.

## Problem
Medical professionals spend a significant amount of time documenting patient encounters. Converting unstructured voice dictations into standard SOAP format is manual and time-consuming.

## Approach
1.  **Audio Ingestion**: Accepts audio files (mp3, wav).
2.  **Transcription**: Uses `faster-whisper` to transcribe audio to text with high accuracy.
3.  **Structuring**: Uses `LangChain` and `ChatOpenAI` with a Pydantic schema to parse the raw transcript into JSON fields corresponding to SOAP sections.
4.  **Validation**: Ensures the output adheres to the defined schema.

## Usage
### Prerequisites
- Python 3.8+
- `ffmpeg` installed on the system (`brew install ffmpeg` on Mac).
- OpenAI API Key (for the LLM structuring step).

### Installation
```bash
pip install -r requirements.txt
```

### Running the Demo
1.  Generate sample audio (if not present):
    ```bash
    python SOAPNote_AI/generate_sample_audio.py
    ```
2.  Open the notebook:
    ```bash
    jupyter notebook SOAPNote_AI/notebooks/SOAPNote_AI.ipynb
    ```
3.  Run all cells.

## Evaluation
- **Transcription**: Verified using sample medical dictations. Whisper handles medical terminology reasonably well but may require fine-tuning for specialized fields.
- **Structuring**: The LLM accurately segments the text into S-O-A-P categories based on context.

## Limitations
- **Privacy**: Sending patient data to external APIs (OpenAI) requires HIPAA compliance considerations. This demo is for non-PHI data only.
- **Accuracy**: Hallucinations are possible; the output must be reviewed by a clinician.
- **Latency**: Transcription and LLM inference can take a few seconds depending on hardware and network.

## Disclaimer
**For clinical documentation assistance only. Not a medical decision system.**
