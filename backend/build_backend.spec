# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Exclude unnecessary heavy packages to speed up compilation from 25m -> 1m
excluded_pkgs = [
    'spacy', 'thinc', 'sklearn', 'scikit-learn', 'boto3', 'botocore',
    'lxml', 'matplotlib', 'plotly', 'altair', 'jsonschema', 'timm',
    'onnxruntime', 'av', 'notebook', 'IPython', 'PIL', 'tkinter',
    'pandas', 'openpyxl', 'bokeh', 'seaborn', 'sympy'
]

a = Analysis(
    ['app/main.py'],
    pathex=['..'],
    binaries=[],
    datas=[
        ('../configs', 'configs'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'pydantic',
        'soundfile',
        'scipy',
        'pydub',
        'librosa',
        'torch',
        'torchaudio',
        'f5_tts',
        'transformers',
        'gtts',
        'win32com',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_pkgs,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tts_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Set UPX to False to prevent DLL compression hang
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='tts_backend',
)
