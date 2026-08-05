@echo off
echo ========================================================
echo Installing IndexTTS2 Environment...
echo ========================================================
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
echo ========================================================
echo IndexTTS2 installation completed successfully!
echo ========================================================
pause
