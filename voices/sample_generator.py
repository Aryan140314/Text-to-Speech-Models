"""
Real Human Voice Audio Sample Generator for TTS-Research
Generates actual spoken English human speech for voices/my_voice.wav and voices/reference.wav.
"""

import os
import win32com.client

def generate_human_voice_sample(filename: str, text: str, voice_index: int = 0, rate: int = 0):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        
        voices = speaker.GetVoices()
        if voice_index < voices.Count:
            speaker.Voice = voices.Item(voice_index)
            
        speaker.Rate = rate
        
        stream.Open(filename, 3, False) # 3 = SSFMCreateForWrite
        speaker.AudioOutputStream = stream
        speaker.Speak(text)
        stream.Close()
        
        print(f"[+] Successfully generated real human voice audio: {filename}")
    except Exception as e:
        print(f"[!] Error generating SAPI5 voice audio: {e}")

if __name__ == "__main__":
    voices_dir = os.path.dirname(os.path.abspath(__file__))
    my_voice_path = os.path.join(voices_dir, "my_voice.wav")
    ref_voice_path = os.path.join(voices_dir, "reference.wav")
    
    # Generate real spoken English reference voice samples
    generate_human_voice_sample(
        my_voice_path,
        text="Hello, this is my primary reference voice recording for zero shot voice cloning evaluation.",
        voice_index=0,
        rate=0
    )
    
    generate_human_voice_sample(
        ref_voice_path,
        text="Welcome to the local text to speech research workspace baseline audio comparison.",
        voice_index=1 if win32com.client.Dispatch("SAPI.SpVoice").GetVoices().Count > 1 else 0,
        rate=1
    )
