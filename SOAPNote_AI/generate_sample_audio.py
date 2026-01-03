from gtts import gTTS
import os

text = """
Patient is a 45-year-old male presenting with a 3-day history of productive cough and fever. 
He reports green sputum and shortness of breath upon exertion. 
Vitals: Temperature 101.2 F, BP 130/85, HR 92, RR 20. 
Lungs: Crackles in the right lower base. 
Assessment: Suspected community-acquired pneumonia. 
Plan: Start Azithromycin 500mg daily for 3 days, CXR ordered, follow up in 1 week.
"""

output_path = os.path.join(os.path.dirname(__file__), "data", "sample_dictation.mp3")
tts = gTTS(text, lang='en')
tts.save(output_path)
print(f"Sample audio saved to {output_path}")
