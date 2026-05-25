# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for SuperShot

import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hidden_imports = (
    collect_submodules("mss")
    + collect_submodules("PIL")
    + [
        "win32clipboard",
        "win32api",
        "win32con",
        "keyboard",
    ]
)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("icon.ico", "."),
        ("icon.png", "."),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "PySide6",
        "PyQt5",
        "IPython",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="SuperShot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                 # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icon.ico",
    uac_admin=False,
    onefile=True,
)
