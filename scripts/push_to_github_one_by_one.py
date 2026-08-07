#!/usr/bin/env python3
"""
push_to_github_one_by_one.py
============================
Pushes every audio file in models_all_voices/ to GitHub
with ONE SEPARATE COMMIT per file.

Repo  : https://github.com/Aryan140314/Text-to-Speech-Models
Branch: main
"""

import os
import sys
import subprocess
import urllib.parse

REPO_ROOT      = r"D:\Saurav\TTS"
MODELS_DIR     = os.path.join(REPO_ROOT, "models_all_voices")
GITHUB_USER    = "Aryan140314"
GITHUB_REPO    = "Text-to-Speech-Models"
BRANCH         = "main"

sep = "-" * 70

def run(cmd, cwd=REPO_ROOT):
    """Run a git command and return stdout, raising on error."""
    result = subprocess.run(
        cmd, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        print(f"[WARN] cmd={' '.join(cmd)}")
        print(f"       stdout: {result.stdout.strip()}")
        print(f"       stderr: {result.stderr.strip()}")
    return result.stdout.strip()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print(sep)
    print("  GitHub Push — One Commit Per File")
    print(f"  Repo  : https://github.com/{GITHUB_USER}/{GITHUB_REPO}")
    print(f"  Source: {MODELS_DIR}")
    print(sep)

    # Collect all wav files sorted by model folder then filename
    all_files = []
    for folder in sorted(os.listdir(MODELS_DIR)):
        folder_path = os.path.join(MODELS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for fname in sorted(os.listdir(folder_path)):
            if fname.endswith(".wav"):
                rel_path = os.path.join("models_all_voices", folder, fname)
                all_files.append((folder, fname, rel_path))

    print(f"[>>] Found {len(all_files)} audio files to push\n")

    total = len(all_files)
    pushed = 0
    skipped = 0

    for i, (folder, fname, rel_path) in enumerate(all_files, 1):
        full_path = os.path.join(REPO_ROOT, rel_path)

        # Check if file already committed (git ls-files)
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel_path],
            cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        already_tracked = (result.returncode == 0)

        # Check if it's modified or untracked
        status_result = subprocess.run(
            ["git", "status", "--porcelain", rel_path],
            cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        status = status_result.stdout.strip()

        if already_tracked and not status:
            print(f"  [{i:02d}/{total}] SKIP (already up to date) : {folder}/{fname}")
            skipped += 1
            continue

        # Stage the single file
        run(["git", "add", rel_path])

        # Commit message
        # Parse genre from filename e.g. [Audiobook] ENG_US_M_BrianR.wav
        genre = "General"
        vname = os.path.splitext(fname)[0]
        if fname.startswith("[") and "]" in fname:
            genre = fname[1:fname.find("]")]
            vname = fname[fname.find("]") + 2:-4]

        model_label = folder.strip("[] ")
        commit_msg = f"Add [{genre}] {vname} — {model_label}"

        run(["git", "commit", "-m", commit_msg])

        # Push after each commit
        push_result = subprocess.run(
            ["git", "push", "origin", BRANCH],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if push_result.returncode == 0:
            print(f"  [{i:02d}/{total}] ✓ PUSHED : {folder}/{fname}")
            pushed += 1
        else:
            print(f"  [{i:02d}/{total}] ✗ FAILED : {folder}/{fname}")
            print(f"             {push_result.stderr.strip()[:120]}")

    print()
    print(sep)
    print(f"  DONE  — Pushed: {pushed}  |  Skipped (already up to date): {skipped}")
    print(sep)

    # ----------------------------------------------------------------
    # Build lightweight HTML pointing to raw GitHub URLs
    # ----------------------------------------------------------------
    print(f"\n[>>] Building GitHub-URL HTML showcase ...")
    build_html(all_files)


# -------------------------------------------------------------------
# HTML Builder — uses raw.githubusercontent.com URLs
# -------------------------------------------------------------------
MODEL_META = {
    "Chatterbox Turbo":   {"key": "chatterbox", "color": "#6366f1", "type": "Zero-Shot Diffusion Cloner"},
    "F5-TTS":             {"key": "f5tts",       "color": "#ec4899", "type": "Non-Autoregressive Flow Matching"},
    "Fish Speech S2":     {"key": "fishspeech",  "color": "#10b981", "type": "44.1kHz VQ-GAN Codec LLM"},
    "OmniVoice":          {"key": "omnivoice",   "color": "#f59e0b", "type": "Expressive Audio LM Cloner"},
    "CosyVoice 3":        {"key": "cosyvoice",   "color": "#8b5cf6", "type": "FunAudioLLM Long-Form Cloner"},
    "XTTS-v2":            {"key": "xttsv2",      "color": "#3b82f6", "type": "Multilingual Zero-Shot Engine"},
    "IndexTTS2":          {"key": "indextts2",   "color": "#06b6d4", "type": "Index Retrieval Timbre Fidelity"},
    "Audio8-TTS-Preview": {"key": "audio8",      "color": "#14b8a6", "type": "ArkTTS Transformer Zero-Shot"},
    "Kokoro-82M":         {"key": "kokoro",      "color": "#ef4444", "type": "Lightweight Neural Preset (82M)"},
}

def get_model_key(folder_name):
    label = folder_name.strip("[] ")
    for k in MODEL_META:
        if k.lower() in folder_name.lower():
            return label, MODEL_META[k]
    return label, {"key": "other", "color": "#6366f1", "type": "Neural Model"}


def build_html(all_files):
    REPO_ROOT_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}"

    cards = []
    for folder, fname, rel_path in all_files:
        m_label, m_meta = get_model_key(folder)
        genre = "General"
        vname = os.path.splitext(fname)[0]
        if fname.startswith("[") and "]" in fname:
            genre = fname[1:fname.find("]")]
            vname = fname[fname.find("]") + 2:-4]

        # URL-encode the path for raw GitHub
        encoded_path = "/".join(
            urllib.parse.quote(part, safe="") 
            for part in rel_path.replace("\\", "/").split("/")
        )
        audio_url = f"{REPO_ROOT_URL}/{encoded_path}"

        cards.append(
            f'<div class="card" data-model="{m_meta["key"]}" data-genre="{genre}">'
            f'<div class="ch">'
            f'<span class="mb" style="background:{m_meta["color"]};">{m_label}</span>'
            f'<span class="gb">{genre}</span>'
            f'</div>'
            f'<div class="vt">{vname}</div>'
            f'<div class="at">{m_meta["type"]}</div>'
            f'<audio controls preload="none" src="{audio_url}"></audio>'
            f'</div>'
        )

    total = len(cards)
    html_out = os.path.join(REPO_ROOT, "TTS_Voice_Showcase.html")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TTS Voice Showcase — 9 AI Models</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;background:#0b0f19;color:#f1f5f9;padding-bottom:60px}}
header{{background:linear-gradient(135deg,#0f172a,#1e1b4b,#0f172a);border-bottom:1px solid #232d42;padding:36px 20px;text-align:center}}
.ht{{font-family:'Outfit',sans-serif;font-size:clamp(1.5rem,3vw,2.3rem);font-weight:800;background:linear-gradient(90deg,#818cf8,#c084fc,#38bdf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}}
.hs{{color:#94a3b8;font-size:0.95rem;margin-bottom:16px}}
.sb{{display:flex;justify-content:center;gap:12px;flex-wrap:wrap}}
.sbg{{background:rgba(255,255,255,.05);border:1px solid #232d42;padding:5px 14px;border-radius:20px;font-size:0.83rem;color:#e2e8f0}}
.sbg strong{{color:#818cf8}}
.ctrl{{max-width:1400px;margin:22px auto 0;padding:0 20px}}
input{{width:100%;padding:12px 16px;background:#101624;border:1px solid #232d42;border-radius:10px;color:#fff;font-size:0.95rem;outline:none;margin-bottom:16px;transition:border-color .2s}}
input:focus{{border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.2)}}
.fl{{margin-bottom:12px}}
.flb{{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin-bottom:8px}}
.pl{{display:flex;flex-wrap:wrap;gap:7px}}
.p{{background:#1e293b;border:1px solid #334155;color:#cbd5e1;padding:5px 13px;border-radius:18px;font-size:.82rem;cursor:pointer;user-select:none;transition:all .18s}}
.p:hover{{background:#334155;color:#fff}}
.p.on{{background:#6366f1;border-color:#6366f1;color:#fff;font-weight:600;box-shadow:0 2px 10px rgba(99,102,241,.3)}}
.wrap{{max-width:1400px;margin:16px auto 0;padding:0 20px}}
.rc{{color:#64748b;font-size:.85rem;margin-bottom:12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:15px}}
.card{{background:#151c2c;border:1px solid #232d42;border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:9px;transition:transform .18s,border-color .18s,box-shadow .18s}}
.card:hover{{transform:translateY(-2px);border-color:#3b4f6a;box-shadow:0 6px 20px rgba(0,0,0,.35)}}
.ch{{display:flex;justify-content:space-between;align-items:center;gap:8px}}
.mb{{font-size:.7rem;font-weight:700;padding:4px 10px;border-radius:6px;text-transform:uppercase;letter-spacing:.04em;color:#fff;white-space:nowrap}}
.gb{{background:#0f172a;border:1px solid #334155;color:#38bdf8;font-size:.7rem;font-weight:600;padding:4px 9px;border-radius:6px;white-space:nowrap}}
.vt{{font-family:'Outfit',sans-serif;font-size:1rem;font-weight:700;color:#f8fafc}}
.at{{font-size:.76rem;color:#64748b}}
audio{{width:100%;height:36px;border-radius:8px;outline:none}}
footer{{text-align:center;color:#475569;font-size:.8rem;margin-top:44px;padding:16px;border-top:1px solid #1e293b}}
</style>
</head>
<body>
<header>
  <div class="ht">&#127897;&#65039; TTS Voice Studio &mdash; 9 AI Models Showcase</div>
  <div class="hs">Click &#9654; Play on any card to stream the audio sample directly from GitHub.</div>
  <div class="sb">
    <div class="sbg">Models: <strong>9 AI Engines</strong></div>
    <div class="sbg">Voice Profiles: <strong>10 Samples</strong></div>
    <div class="sbg">Total Clips: <strong>{total} Files</strong></div>
    <div class="sbg">GPU: <strong>NVIDIA RTX 3060 CUDA</strong></div>
  </div>
</header>
<div class="ctrl">
  <input id="si" type="text" placeholder="&#128269;  Search by model, genre or voice name..." oninput="fc()">
  <div class="fl">
    <div class="flb">Filter by Model</div>
    <div class="pl" id="mp">
      <div class="p on" onclick="sm('all',this)">All Models</div>
      <div class="p" onclick="sm('chatterbox',this)">Chatterbox Turbo</div>
      <div class="p" onclick="sm('f5tts',this)">F5-TTS</div>
      <div class="p" onclick="sm('fishspeech',this)">Fish Speech S2</div>
      <div class="p" onclick="sm('omnivoice',this)">OmniVoice</div>
      <div class="p" onclick="sm('cosyvoice',this)">CosyVoice 3</div>
      <div class="p" onclick="sm('xttsv2',this)">XTTS-v2</div>
      <div class="p" onclick="sm('indextts2',this)">IndexTTS2</div>
      <div class="p" onclick="sm('audio8',this)">Audio8-TTS</div>
      <div class="p" onclick="sm('kokoro',this)">Kokoro-82M</div>
    </div>
  </div>
  <div class="fl">
    <div class="flb">Filter by Genre</div>
    <div class="pl" id="gp">
      <div class="p on" onclick="sg('all',this)">All Genres</div>
      <div class="p" onclick="sg('Announcement',this)">&#128226; Announcement</div>
      <div class="p" onclick="sg('Audiobook',this)">&#128218; Audiobook</div>
      <div class="p" onclick="sg('Motivational',this)">&#128293; Motivational</div>
      <div class="p" onclick="sg('Narration',this)">&#127897; Narration</div>
      <div class="p" onclick="sg('Podcast',this)">&#127911; Podcast</div>
      <div class="p" onclick="sg('Presentation',this)">&#128202; Presentation</div>
      <div class="p" onclick="sg('Social Media',this)">&#128241; Social Media</div>
      <div class="p" onclick="sg('Storytelling',this)">&#128214; Storytelling</div>
    </div>
  </div>
</div>
<div class="wrap">
  <div class="rc" id="rc">Showing all {total} clips</div>
  <div class="grid" id="grid">
{"".join(cards)}
  </div>
</div>
<footer>TTS Laboratory Pipeline &bull; Hosted on GitHub &bull; Audio streams directly from raw.githubusercontent.com</footer>
<script>
let am='all',ag='all';
function sm(m,el){{am=m;document.querySelectorAll('#mp .p').forEach(p=>p.classList.remove('on'));el.classList.add('on');fc();}}
function sg(g,el){{ag=g;document.querySelectorAll('#gp .p').forEach(p=>p.classList.remove('on'));el.classList.add('on');fc();}}
function fc(){{
  const q=document.getElementById('si').value.toLowerCase();
  let v=0;
  document.querySelectorAll('.card').forEach(c=>{{
    const show=(am==='all'||c.dataset.model===am)&&(ag==='all'||c.dataset.genre===ag)&&(q===''||c.textContent.toLowerCase().includes(q));
    c.style.display=show?'flex':'none';
    if(show)v++;
  }});
  document.getElementById('rc').textContent='Showing '+v+' of {total} clips';
}}
</script>
</body>
</html>"""

    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(html_out) / 1024
    print(sep)
    print(f"  HTML saved : {html_out}")
    print(f"  Size       : {size_kb:.1f} KB  (tiny! audio streams from GitHub)")
    print(sep)
    print()
    print("  NOW PUSH THE HTML FILE TOO:")
    print(f"    git add TTS_Voice_Showcase.html")
    print(f'    git commit -m "Add TTS Voice Showcase HTML"')
    print(f"    git push origin main")
    print(sep)


if __name__ == "__main__":
    main()
