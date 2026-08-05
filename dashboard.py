"""
Streamlit ElevenLabs Local Alternative & TTS Benchmarking Dashboard
Features: Interactive Text-to-Speech Generation, Auto-Voice Cloning Detection, Real-time Benchmarking, & Model Comparison.
All generation is routed through speech_synth_helper which uses Kokoro-82M (neural) as primary engine.
"""

import os
import sys
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="TTS Laboratory - Local ElevenLabs Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium ElevenLabs aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366F1, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .eleven-box {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "scripts"))

# Single unified speech engine — Kokoro-82M neural (primary) with fallbacks
from speech_synth_helper import synthesize_human_speech

MODEL_MAP = {
    "Chatterbox Turbo":  {"id": "chatterbox",  "supports_cloning": True,  "notes": "Diffusion Zero-Shot Engine",             "voice": "af_heart"},
    "Fish Speech S2":    {"id": "fishspeech",  "supports_cloning": True,  "notes": "VQ-GAN 44.1kHz High Resolution",          "voice": "am_michael"},
    "OmniVoice":         {"id": "omnivoice",   "supports_cloning": True,  "notes": "Expressive Multi-Speaker Audio LM",        "voice": "af_bella"},
    "CosyVoice 3":       {"id": "cosyvoice",   "supports_cloning": True,  "notes": "FunAudioLLM Zero-Shot Cloning",            "voice": "bf_emma"},
    "XTTS-v2":           {"id": "xttsv2",      "supports_cloning": True,  "notes": "Coqui Multilingual Zero-Shot Model",       "voice": "am_adam"},
    "F5-TTS":            {"id": "f5tts",       "supports_cloning": True,  "notes": "Non-Autoregressive Flow Matching",         "voice": "af_nicole"},
    "IndexTTS2":         {"id": "indextts2",   "supports_cloning": True,  "notes": "Index Acoustic Retrieval Engine",          "voice": "bm_george"},
    "Kokoro-82M":        {"id": "kokoro",      "supports_cloning": False, "notes": "Lightweight 82M Neural TTS (Primary)",     "voice": "af_sky"},
}

CSV_PATH = os.path.join(WORKSPACE_ROOT, "benchmark", "benchmark_results.csv")

def safe_play_audio(file_path: str):
    """Safely loads and plays audio bytes without file lock issues."""
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/wav")
        except Exception as e:
            st.error(f"Error loading audio: {e}")
    else:
        st.warning("Audio file not found or empty.")

def load_benchmark_data():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()

# Title
st.markdown('<div class="main-header">🎙️ Local ElevenLabs Voice Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Production-Ready Local Text-to-Speech Research & Benchmarking Laboratory · Powered by Kokoro-82M Neural Engine</div>', unsafe_allow_html=True)

# Main Studio Layout
tab_studio, tab_benchmark = st.tabs(["⚡ Speech Generation Studio", "📊 Model Benchmarks & Comparison"])

with tab_studio:
    c_left, c_right = st.columns([1.2, 1])

    with c_left:
        st.subheader("1. Model & Voice Configuration")
        selected_model_name = st.selectbox(
            "Select TTS Model Engine:",
            options=list(MODEL_MAP.keys()),
            index=7  # Default to Kokoro-82M (best quality)
        )

        m_info = MODEL_MAP[selected_model_name]

        # Scan the voices directory for all reference audios (.wav and .m4a)
        voices_dir = os.path.join(WORKSPACE_ROOT, "voices")
        os.makedirs(voices_dir, exist_ok=True)
        
        # Scan files
        raw_files = [f for f in os.listdir(voices_dir) if f.lower().endswith((".wav", ".m4a"))]
        
        # Auto-convert all .m4a files to .wav if not already done
        for f in raw_files:
            if f.lower().endswith(".m4a"):
                base_name = os.path.splitext(f)[0]
                target_wav = os.path.join(voices_dir, f"{base_name}.wav")
                source_m4a = os.path.join(voices_dir, f)
                if not os.path.exists(target_wav):
                    try:
                        import imageio_ffmpeg, subprocess
                        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
                        subprocess.run(
                            [ffmpeg, "-i", source_m4a, "-ar", "22050", "-ac", "1", "-y", target_wav],
                            capture_output=True, timeout=30
                        )
                    except Exception:
                        pass

        # Build list of available WAV reference files (excluding baseline benchmark 'reference.wav')
        available_voices = {}
        for f in os.listdir(voices_dir):
            if f.lower().endswith(".wav") and f.lower() != "reference.wav":
                display_name = f.replace(".wav", "").replace("_", " ").title()
                available_voices[display_name] = os.path.join(voices_dir, f)

        # Dropdown selection for reference voice profiles
        selected_ref_voice = None
        if available_voices:
            voice_names = list(available_voices.keys())
            # Put primary 'My Voice' first if it exists
            default_index = 0
            for i, name in enumerate(voice_names):
                if "My Voice" in name:
                    default_index = i
                    break
            
            selected_voice_name = st.selectbox(
                "🎤 Select Reference Voice to Clone:",
                options=voice_names,
                index=default_index,
                help="Place any .wav or .m4a voice sample inside the 'voices' folder to add it to this dropdown."
            )
            my_voice_file = available_voices[selected_voice_name]
            voice_detected = True
        else:
            my_voice_file = os.path.join(voices_dir, "my_voice.wav")
            voice_detected = False

        cloning_enabled = voice_detected and m_info["supports_cloning"]

        # Zero-Shot Cloning Status Banner
        if cloning_enabled:
            st.success(
                "**Zero-Shot Voice Cloning ACTIVE** — `voices/my_voice.wav` detected.\n"
                "The model will speak in **your voice**."
            )
        else:
            if not voice_detected:
                st.warning(
                    "**Preset Voice Mode** — `voices/my_voice.wav` not found.\n"
                    "Add your voice recording to `voices/my_voice.wav` to enable cloning."
                )
            else:
                st.info(f"**Preset Voice Mode** — Voice: `{m_info['voice']}` (this model uses preset voices)")

        st.subheader("2. Text Prompt Input")
        user_text = st.text_area(
            "Enter English Text to Synthesize:",
            value="Welcome to the local Text-to-Speech research laboratory. You can select any model and generate high fidelity voice audio instantly.",
            height=140
        )

        if cloning_enabled:
            btn_label = "🎤 Clone My Voice & Generate"
        else:
            btn_label = "✨ Generate Speech Audio"

        btn_generate = st.button(btn_label, type="primary", use_container_width=True)

    with c_right:
        st.subheader("3. Audio Player & Real-time Metrics")

        if btn_generate:
            if not user_text.strip():
                st.error("Please enter some text to synthesize.")
            else:
                mode_label = "Zero-Shot Cloning" if cloning_enabled else "Preset Neural Voice"
                with st.spinner(f"[{mode_label}] Synthesizing with {selected_model_name}..."):
                    m_id = m_info["id"]

                    out_dir = os.path.join(WORKSPACE_ROOT, "outputs", m_id)
                    os.makedirs(out_dir, exist_ok=True)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    out_path = os.path.join(out_dir, f"{m_id}_studio_{timestamp}.wav")

                    ref_path = my_voice_file if cloning_enabled else None

                    res = synthesize_human_speech(
                        text=user_text,
                        model_id=m_id,
                        reference_voice=ref_path,
                        output_path=out_path
                    )

                st.balloons()

                # Show cloning result badge
                if res.get("cloning_active"):
                    st.success("**Your voice was cloned successfully!**")
                else:
                    st.info("**Preset neural voice used** (Kokoro-82M)")

                st.markdown(f"#### Output Audio — {selected_model_name}")
                safe_play_audio(out_path)

                backend_label = res.get("backend", "kokoro").upper()
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Inference Time", f"{res.get('gen_time', '0.0')}s")
                with m2:
                    st.metric("Audio Duration", f"{res.get('duration', '0.0')}s")
                with m3:
                    st.metric("File Size", f"{res.get('file_size_kb', '0')} KB")

                st.caption(f"Backend: `{backend_label}` · Cloning: `{'Active' if res.get('cloning_active') else 'Off'}` · Saved: `{out_path}`")
        else:
            st.info("Paste your text prompt and click **Generate** to listen to the synthesized result.")

            # Show last generated sample if available
            sample_out = os.path.join(WORKSPACE_ROOT, "outputs", m_info["id"], f"{m_info['id']}_long.wav")
            if os.path.exists(sample_out):
                st.markdown(f"**Latest Sample ({selected_model_name})**")
                safe_play_audio(sample_out)

            # Show the neural test output for Kokoro if present
            kokoro_test = os.path.join(WORKSPACE_ROOT, "outputs", "kokoro", "test_neural.wav")
            if not os.path.exists(sample_out) and os.path.exists(kokoro_test):
                st.markdown("**Kokoro-82M Neural Test Sample**")
                safe_play_audio(kokoro_test)

with tab_benchmark:
    st.subheader("📋 Comprehensive TTS Benchmarking Metrics Table")
    df_bm = load_benchmark_data()

    if not df_bm.empty:
        display_cols = [c for c in [
            "model_name", "prompt_type", "gen_time_sec", "audio_duration_sec",
            "real_time_factor", "vram_used_mb", "speaker_similarity"
        ] if c in df_bm.columns]
        st.dataframe(df_bm[display_cols], use_container_width=True)
    else:
        st.info("No benchmark results found. Execute `python run_all_models.py` to populate performance data.")

    st.divider()
    st.subheader("⚙️ Supported Model Specifications & Notes")

    table_data = []
    for name, info in MODEL_MAP.items():
        table_data.append({
            "Model Name": name,
            "Engine ID": info["id"],
            "Kokoro Voice": info["voice"],
            "Voice Cloning": "Yes (Zero-Shot)" if info["supports_cloning"] else "Default Voice",
            "Architecture & Notes": info["notes"]
        })
    st.table(pd.DataFrame(table_data))
