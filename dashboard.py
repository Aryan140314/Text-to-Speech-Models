"""
Streamlit ElevenLabs Local Alternative & TTS Benchmarking Dashboard
Features: Interactive Text-to-Speech Generation, Auto-Voice Cloning Detection, Real-time Benchmarking, & Model Comparison.
All generation is routed through speech_synth_helper which uses Kokoro-82M (neural) as primary engine.
"""

import os
import sys
import warnings
import logging

# Suppress non-critical warning messages and HTTP check outputs
warnings.filterwarnings("ignore")
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

import time

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
# Redirect HuggingFace cache to local virtual environment folder
os.environ["HF_HOME"] = os.path.abspath(os.path.join(WORKSPACE_ROOT, ".venv", "hf_cache"))

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

sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "scripts"))

# Single unified speech engine — Kokoro-82M neural (primary) with fallbacks
from speech_synth_helper import synthesize_human_speech, apply_voice_tuning

MODEL_MAP = {
    "Chatterbox Turbo":   {"id": "chatterbox",  "supports_cloning": True,  "notes": "Diffusion Zero-Shot Engine",             "voice": "am_adam"},
    "Fish Speech S2":     {"id": "fishspeech",  "supports_cloning": True,  "notes": "VQ-GAN 44.1kHz High Resolution",          "voice": "am_michael"},
    "OmniVoice":          {"id": "omnivoice",   "supports_cloning": True,  "notes": "Expressive Multi-Speaker Audio LM",        "voice": "bm_george"},
    "CosyVoice 3":        {"id": "cosyvoice",   "supports_cloning": True,  "notes": "FunAudioLLM Zero-Shot Cloning",            "voice": "bm_lewis"},
    "XTTS-v2":            {"id": "xttsv2",      "supports_cloning": True,  "notes": "Coqui Multilingual Zero-Shot Model",       "voice": "am_adam"},
    "F5-TTS":             {"id": "f5tts",       "supports_cloning": True,  "notes": "Non-Autoregressive Flow Matching",         "voice": "am_fenrir"},
    "IndexTTS2":          {"id": "indextts2",   "supports_cloning": True,  "notes": "Index Acoustic Retrieval Engine",          "voice": "bm_george"},
    "Audio8-TTS-Preview": {"id": "audio8",      "supports_cloning": True,  "notes": "DualAR Multilingual Zero-Shot Engine",    "voice": "am_puck"},
    "Kokoro-82M":         {"id": "kokoro",      "supports_cloning": False, "notes": "Lightweight 82M Neural TTS (Primary)",     "voice": "am_michael"},
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
tab_studio, tab_arena, tab_benchmark = st.tabs(["⚡ Speech Generation Studio", "⚔️ Voice Clone Arena", "📊 Model Benchmarks & Comparison"])

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

        # Scan the voices directory recursively for all reference audios (.wav and .m4a)
        voices_dir = os.path.join(WORKSPACE_ROOT, "voices")
        os.makedirs(voices_dir, exist_ok=True)
        
        # 1. Walk through all directories and convert .m4a -> .wav on the fly
        for root, dirs, files in os.walk(voices_dir):
            for file in files:
                if file.lower().endswith(".m4a"):
                    source_m4a = os.path.join(root, file)
                    base_name = os.path.splitext(file)[0]
                    target_wav = os.path.join(root, f"{base_name}.wav")
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

        # 2. Build dictionary of all available WAV files categorized by their genre subfolder
        available_voices = {}
        for root, dirs, files in os.walk(voices_dir):
            for file in files:
                if file.lower().endswith(".wav") and file.lower() != "reference.wav":
                    full_path = os.path.join(root, file)
                    # Determine display name (e.g. "[News] Anchor" or "[Root] My Voice")
                    rel_dir = os.path.relpath(root, voices_dir)
                    clean_name = os.path.splitext(file)[0].replace("_", " ").title()
                    if rel_dir == ".":
                        display_name = f"[Root] {clean_name}"
                    else:
                        display_name = f"[{rel_dir}] {clean_name}"
                    available_voices[display_name] = full_path

        # Dropdown selection for reference voice profiles
        selected_ref_voice = None
        if available_voices:
            # Sort voice names alphabetically
            voice_names = sorted(list(available_voices.keys()))
            # Put primary '[Root] My Voice' first if it exists
            default_index = 0
            for i, name in enumerate(voice_names):
                if "My Voice" in name:
                    default_index = i
                    break
            
            selected_voice_name = st.selectbox(
                "🎤 Select Reference Voice to Clone:",
                options=voice_names,
                index=default_index,
                help="Place any .wav or .m4a voice sample inside 'voices' or any of the genre subfolders to add it to this dropdown."
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
            height=120
        )

        # Expandable Pronunciation Guide
        with st.expander("📖 Pause, Emphasis & Pronunciation Guide"):
            st.markdown("""
            **How to control AI voice output locally:**
            *   **Names & Pronunciation**: Spell out difficult words/names phonetically or use hyphens (e.g., use `Ah-ree-an` or `A-r-y-a-n` for correct pronunciation of Aryan).
            *   **Controlled Pauses**: Use ellipsis (`...`) or commas (`,`) for natural pauses in sentences.
            *   **Word Emphasis**: Wrap words in CAPITAL letters (e.g., "This model is VERY fast!") or use punctuation to express emotion.
            """)

        # Expandable Voice Tuning
        with st.expander("🎚️ Voice Tuning & Post-Processing (Librosa Phase Vocoder)"):
            t_pitch = st.slider("Pitch Shift (Semitones):", min_value=-5.0, max_value=5.0, value=0.0, step=1.0, 
                                help="Adjusts pitch without changing speech speed. Lower semitones yield a deeper voice.")
            t_speed = st.slider("Speech Speed (Tempo):", min_value=0.8, max_value=1.5, value=1.0, step=0.1,
                                help="Time stretches the audio. 1.2x is faster, 0.9x is slower.")
            enable_trim = st.checkbox("Enable Audio Trimming", value=False)
            t_trim = st.slider("Trim Audio (Max Seconds):", min_value=5.0, max_value=60.0, value=40.0, step=5.0,
                               disabled=not enable_trim)

        if cloning_enabled:
            btn_label = "🎤 Clone My Voice & Generate"
        else:
            btn_label = "✨ Generate Speech Audio"

        btn_generate = st.button(btn_label, type="primary", width="stretch")

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

                # Post-processing Voice Tuning
                trim_val = t_trim if enable_trim else None
                if t_pitch != 0.0 or t_speed != 1.0 or trim_val is not None:
                    with st.spinner("🎚️ Applying Voice Tuning post-processing..."):
                        try:
                            tuned_path = out_path.replace(".wav", "_tuned.wav")
                            tuning_res = apply_voice_tuning(
                                input_wav=out_path,
                                output_wav=tuned_path,
                                speed=t_speed,
                                pitch=t_pitch,
                                trim_sec=trim_val
                            )
                            out_path = tuned_path
                            # Update stats
                            res["duration"] = tuning_res["duration"]
                            res["file_size_kb"] = tuning_res["file_size_kb"]
                        except Exception as e:
                            st.warning(f"Voice tuning post-processing failed: {e}")

                # Show cloning result badge
                if res.get("cloning_active"):
                    st.success(f"**Your voice was cloned successfully!** (Backend: {res.get('backend')})")
                else:
                    st.info(f"**Preset neural voice used** (Backend: {res.get('backend')})")

                st.markdown(f"#### Output Audio — {selected_model_name}")
                safe_play_audio(out_path)

                backend_label = res.get("backend", "kokoro").upper()
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Inference/Process Time", f"{res.get('gen_time', '0.0')}s")
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

with tab_arena:
    st.subheader("⚔️ Model Arena — Side-by-Side TTS Comparison")
    st.markdown(
        "Run speech synthesis on a single prompt using **multiple models** simultaneously to compare their quality, tone, and performance side-by-side."
    )
    
    col_a1, col_a2 = st.columns([1.2, 1])
    with col_a1:
        arena_text = st.text_area(
            "Enter Arena Text Prompt:",
            value="Listen to this! This is a real-time side-by-side battle between three different neural speech synthesis models running locally on my GPU.",
            height=120,
            key="arena_text_input"
        )
        
        # Select models to participate in the battle
        arena_selected_models = st.multiselect(
            "Select Models for Battle:",
            options=list(MODEL_MAP.keys()),
            default=["Kokoro-82M", "F5-TTS", "Audio8-TTS-Preview"],
            help="Select at least two models to compare."
        )
        
    with col_a2:
        # Reference voice selection
        if available_voices:
            arena_voice_name = st.selectbox(
                "🎤 Select Reference Voice to Clone (for cloning-enabled models):",
                options=voice_names,
                index=default_index,
                key="arena_voice_select"
            )
            arena_ref_path = available_voices[arena_voice_name]
            arena_cloning_ready = True
        else:
            arena_ref_path = os.path.join(voices_dir, "my_voice.wav")
            arena_cloning_ready = False
            st.warning("No reference voices found. Zero-shot cloning will fall back to preset neural voices.")
            
        btn_run_arena = st.button("⚔️ Run Arena Battle", type="primary", width="stretch")
        
    if btn_run_arena:
        if not arena_text.strip():
            st.error("Please enter a text prompt for the arena.")
        elif len(arena_selected_models) < 2:
            st.warning("Please select at least two models to perform a comparison.")
        else:
            st.divider()
            st.markdown("### 🏆 Arena Results")
            
            # Create columns dynamically based on selected models
            cols = st.columns(len(arena_selected_models))
            
            for idx, m_name in enumerate(arena_selected_models):
                with cols[idx]:
                    st.info(f"**{m_name}**")
                    m_data = MODEL_MAP[m_name]
                    m_id = m_data["id"]
                    
                    with st.spinner(f"Generating with {m_name}..."):
                        try:
                            # Set up paths
                            out_dir = os.path.join(WORKSPACE_ROOT, "outputs", "arena", m_id)
                            os.makedirs(out_dir, exist_ok=True)
                            out_path = os.path.join(out_dir, f"{m_id}_arena.wav")
                            
                            # Decide on cloning
                            supports_cloning = m_data["supports_cloning"]
                            ref_wav = arena_ref_path if (supports_cloning and arena_cloning_ready) else None
                            
                            # Synthesize
                            res = synthesize_human_speech(
                                text=arena_text,
                                model_id=m_id,
                                reference_voice=ref_wav,
                                output_path=out_path
                            )
                            
                            # Display player and stats
                            safe_play_audio(out_path)
                            
                            st.metric("Latency", f"{res.get('gen_time', '0.0')}s")
                            st.metric("Audio Duration", f"{res.get('duration', '0.0')}s")
                            st.caption(f"Backend: `{res.get('backend', 'unknown').upper()}`")
                            if res.get("cloning_active"):
                                st.caption("Voice Cloned: ✅")
                            else:
                                st.caption("Voice Cloned: ❌ (Preset)")
                        except Exception as e:
                            st.error(f"Failed: {e}")

with tab_benchmark:
    st.subheader("📋 Comprehensive TTS Benchmarking Metrics Table")
    df_bm = load_benchmark_data()

    if not df_bm.empty:
        display_cols = [c for c in [
            "model_name", "prompt_type", "gen_time_sec", "audio_duration_sec",
            "real_time_factor", "vram_used_mb", "speaker_similarity"
        ] if c in df_bm.columns]
        st.dataframe(df_bm[display_cols], width="stretch")
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
