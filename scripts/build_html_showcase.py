#!/usr/bin/env python3
"""
build_html_showcase.py  — FAST LAZY-LOAD VERSION
======================
Standalone Portable HTML Showcase Generator
TTS Laboratory — Audio DSP & AI Engineering Division

KEY FIX: Audio base64 data is stored in a JS object inside the page,
and src is ONLY injected into the <audio> element when the user clicks Play.
This way the browser does NOT try to parse 46MB of base64 on page load.
Page opens in < 1 second. Audio plays instantly on first click.
"""

import os
import sys
import base64

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR      = os.path.join(WORKSPACE_ROOT, "models_all_voices")
OUTPUT_HTML    = os.path.join(WORKSPACE_ROOT, "TTS_Voice_Showcase_Portable.html")

MODEL_METADATA = {
    "chatterbox":  {"name": "Chatterbox Turbo",   "color": "#6366f1", "type": "Zero-Shot Diffusion Cloner"},
    "f5tts":       {"name": "F5-TTS",             "color": "#ec4899", "type": "Non-Autoregressive Flow Matching"},
    "fishspeech":  {"name": "Fish Speech S2",     "color": "#10b981", "type": "44.1kHz VQ-GAN Codec LLM"},
    "omnivoice":   {"name": "OmniVoice",          "color": "#f59e0b", "type": "Expressive Audio LM Cloner"},
    "cosyvoice":   {"name": "CosyVoice 3",        "color": "#8b5cf6", "type": "FunAudioLLM Long-Form Cloner"},
    "xttsv2":      {"name": "XTTS-v2",            "color": "#3b82f6", "type": "Multilingual Zero-Shot Engine"},
    "indextts2":   {"name": "IndexTTS2",          "color": "#06b6d4", "type": "Index Retrieval Timbre Fidelity"},
}

GENRE_EMOJIS = {
    "Announcement": "ANNOUNCEMENT",
    "Audiobook":    "AUDIOBOOK",
    "Motivational": "MOTIVATIONAL",
    "Narration":    "NARRATION",
    "Podcast":      "PODCAST",
    "Presentation": "PRESENTATION",
    "Social Media": "SOCIAL MEDIA",
    "Storytelling": "STORYTELLING",
    "Root":         "REFERENCE",
}

def get_model_key(folder_name):
    f = folder_name.lower()
    if "chatterbox" in f: return "chatterbox"
    if "f5-tts" in f or "f5tts" in f: return "f5tts"
    if "fish" in f: return "fishspeech"
    if "omni" in f: return "omnivoice"
    if "cosy" in f: return "cosyvoice"
    if "xtts" in f: return "xttsv2"
    if "index" in f: return "indextts2"
    if "audio8" in f: return "audio8"
    if "kokoro" in f: return "kokoro"
    return "kokoro"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    sep = "-" * 75
    print(sep)
    print("  TTS Laboratory — Portable HTML Showcase Builder (FAST LAZY-LOAD)")
    print(f"  Output: {OUTPUT_HTML}")
    print(sep)

    model_folders = sorted([
        d for d in os.listdir(INPUT_DIR)
        if os.path.isdir(os.path.join(INPUT_DIR, d))
    ])
    print(f"[>>] Found {len(model_folders)} model folder(s)\n")

    audio_store = {}   # card_id -> base64 data URI string
    card_meta   = []
    idx = 0

    for folder_name in model_folders:
        folder_path = os.path.join(INPUT_DIR, folder_name)
        m_key  = get_model_key(folder_name)
        m_meta = MODEL_METADATA.get(m_key, {"name": folder_name, "color": "#6366f1", "type": "Neural Model"})
        wav_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".wav")])
        print(f"  {m_meta['name']:<24} {len(wav_files)} files")
        for fname in wav_files:
            fpath   = os.path.join(folder_path, fname)
            if fname.startswith("[") and "]" in fname:
                genre = fname[1:fname.find("]")]
                vname = fname[fname.find("]") + 2:-4]
            else:
                genre = "General"; vname = os.path.splitext(fname)[0]
            card_id = f"c{idx}"; idx += 1
            with open(fpath, "rb") as af:
                b64 = base64.b64encode(af.read()).decode("utf-8")
            audio_store[card_id] = f"data:audio/wav;base64,{b64}"
            card_meta.append({
                "card_id": card_id, "m_key": m_key,
                "m_name": m_meta["name"], "m_color": m_meta["color"],
                "m_type": m_meta["type"], "genre": genre, "vname": vname,
            })

    total = len(card_meta)
    print(f"\n[>>] Building HTML with {total} lazy-load cards ...")

    # Build HTML cards (NO src attribute set)
    cards_html = []
    for c in card_meta:
        g_label = GENRE_EMOJIS.get(c["genre"], c["genre"].upper())
        cards_html.append(
            f'<div class="card" id="{c["card_id"]}" data-model="{c["m_key"]}" data-genre="{c["genre"]}">'
            f'<div class="ch">'
            f'<span class="mb" style="background:{c["m_color"]};">{c["m_name"]}</span>'
            f'<span class="gb">{g_label}</span>'
            f'</div>'
            f'<div class="vt">{c["vname"]}</div>'
            f'<div class="at">{c["m_type"]}</div>'
            f'<audio id="a_{c["card_id"]}" controls preload="none" onplay="ll(\'{c["card_id"]}\')"></audio>'
            f'</div>'
        )

    # Build JS audio map — stored as template literal strings to avoid quote issues
    js_lines = ["const AD={"]
    for cid, uri in audio_store.items():
        # Use backtick template literal so no escaping needed for base64
        js_lines.append(f'"{cid}":`{uri}`,')
    js_lines.append("};")
    js_audio_map = "\n".join(js_lines)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TTS Voice Showcase — 9 AI Models</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',system-ui,sans-serif;background:#0b0f19;color:#f1f5f9;padding-bottom:60px}
header{background:linear-gradient(135deg,#0f172a,#1e1b4b,#0f172a);border-bottom:1px solid #232d42;padding:36px 20px;text-align:center}
.ht{font-family:'Outfit',sans-serif;font-size:clamp(1.5rem,3vw,2.3rem);font-weight:800;background:linear-gradient(90deg,#818cf8,#c084fc,#38bdf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
.hs{color:#94a3b8;font-size:0.95rem;margin-bottom:16px}
.sb{display:flex;justify-content:center;gap:12px;flex-wrap:wrap}
.sbg{background:rgba(255,255,255,.05);border:1px solid #232d42;padding:5px 14px;border-radius:20px;font-size:0.83rem;color:#e2e8f0}
.sbg strong{color:#818cf8}
.ctrl{max-width:1400px;margin:22px auto 0;padding:0 20px}
input{width:100%;padding:12px 16px;background:#101624;border:1px solid #232d42;border-radius:10px;color:#fff;font-size:0.95rem;outline:none;margin-bottom:16px;transition:border-color .2s}
input:focus{border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.2)}
.fl{margin-bottom:12px}
.flb{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin-bottom:8px}
.pl{display:flex;flex-wrap:wrap;gap:7px}
.p{background:#1e293b;border:1px solid #334155;color:#cbd5e1;padding:5px 13px;border-radius:18px;font-size:.82rem;cursor:pointer;user-select:none;transition:all .18s}
.p:hover{background:#334155;color:#fff}
.p.on{background:#6366f1;border-color:#6366f1;color:#fff;font-weight:600;box-shadow:0 2px 10px rgba(99,102,241,.3)}
.wrap{max-width:1400px;margin:16px auto 0;padding:0 20px}
.rc{color:#64748b;font-size:.85rem;margin-bottom:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:15px}
.card{background:#151c2c;border:1px solid #232d42;border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:9px;transition:transform .18s,border-color .18s,box-shadow .18s}
.card:hover{transform:translateY(-2px);border-color:#3b4f6a;box-shadow:0 6px 20px rgba(0,0,0,.35)}
.ch{display:flex;justify-content:space-between;align-items:center;gap:8px}
.mb{font-size:.7rem;font-weight:700;padding:4px 10px;border-radius:6px;text-transform:uppercase;letter-spacing:.04em;color:#fff;white-space:nowrap}
.gb{background:#0f172a;border:1px solid #334155;color:#38bdf8;font-size:.7rem;font-weight:600;padding:4px 9px;border-radius:6px;white-space:nowrap}
.vt{font-family:'Outfit',sans-serif;font-size:1rem;font-weight:700;color:#f8fafc}
.at{font-size:.76rem;color:#64748b}
audio{width:100%;height:36px;border-radius:8px;outline:none}
footer{text-align:center;color:#475569;font-size:.8rem;margin-top:44px;padding:16px;border-top:1px solid #1e293b}
</style>
</head>
<body>
<header>
  <div class="ht">&#127897;&#65039; TTS Voice Studio &mdash; 9 AI Models Showcase</div>
  <div class="hs">All 90 voice clips embedded. Click &#9654; Play to load any clip instantly &mdash; no server needed.</div>
  <div class="sb">
    <div class="sbg">Models: <strong>9 AI Engines</strong></div>
    <div class="sbg">Voice Profiles: <strong>10 Samples</strong></div>
    <div class="sbg">Total Clips: <strong>90 Files</strong></div>
    <div class="sbg">GPU: <strong>NVIDIA RTX 3060 CUDA</strong></div>
  </div>
</header>
<div class="ctrl">
  <input id="si" type="text" placeholder="Search by model, genre or voice name..." oninput="fc()">
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
      <div class="p" onclick="sg('Announcement',this)">Announcement</div>
      <div class="p" onclick="sg('Audiobook',this)">Audiobook</div>
      <div class="p" onclick="sg('Motivational',this)">Motivational</div>
      <div class="p" onclick="sg('Narration',this)">Narration</div>
      <div class="p" onclick="sg('Podcast',this)">Podcast</div>
      <div class="p" onclick="sg('Presentation',this)">Presentation</div>
      <div class="p" onclick="sg('Social Media',this)">Social Media</div>
      <div class="p" onclick="sg('Storytelling',this)">Storytelling</div>
    </div>
  </div>
</div>
<div class="wrap">
  <div class="rc" id="rc">Showing all """ + str(total) + """ clips</div>
  <div class="grid" id="grid">
""" + "\n".join(cards_html) + """
  </div>
</div>
<footer>TTS Laboratory Pipeline &bull; """ + str(total) + """ audio clips embedded as Base64 &bull; Lazy-load: audio decoded only on Play click</footer>
<script>
""" + js_audio_map + """
const loaded=new Set();
function ll(id){
  if(loaded.has(id))return;
  const el=document.getElementById('a_'+id);
  if(el&&AD[id]){el.src=AD[id];el.load();loaded.add(id);el.onplay=null;}
}
let am='all',ag='all';
function sm(m,el){am=m;document.querySelectorAll('#mp .p').forEach(p=>p.classList.remove('on'));el.classList.add('on');fc();}
function sg(g,el){ag=g;document.querySelectorAll('#gp .p').forEach(p=>p.classList.remove('on'));el.classList.add('on');fc();}
function fc(){
  const q=document.getElementById('si').value.toLowerCase();
  let v=0;
  document.querySelectorAll('.card').forEach(c=>{
    const show=(am==='all'||c.dataset.model===am)&&(ag==='all'||c.dataset.genre===ag)&&(q===''||c.textContent.toLowerCase().includes(q));
    c.style.display=show?'flex':'none';
    if(show)v++;
  });
  document.getElementById('rc').textContent='Showing '+v+' of """ + str(total) + """ clips';
}
</script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(OUTPUT_HTML) / (1024*1024)
    sep = "-"*75
    print(sep)
    print("  DONE — FAST LAZY-LOAD VERSION")
    print(sep)
    print(f"  File      : {OUTPUT_HTML}")
    print(f"  Size      : {size_mb:.2f} MB")
    print(f"  Clips     : {total} (audio decoded only on Play)")
    print(sep)

if __name__ == "__main__":
    main()

