# PyInstaller spec file for Desktop Billing Application
# -*- mode: python ; coding: utf-8 -*-

import os
from PyQt5 import QtCore

block_cipher = None

# Define the main script
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('venv/Lib/site-packages/escpos/capabilities.json', 'escpos'),
        ('data_base/database.py', 'data_base'),
        # Do NOT include billing.db here!
        ('data_base/images/ImageNotFound.png', 'data_base/images'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtWidgets', 
        'PyQt5.QtGui',
        'sqlite3',
        'PIL',
        'escpos',
        'escpos.printer',
        'csv',
        'datetime'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary modules to reduce file size
a.binaries = [x for x in a.binaries if not x[0].startswith('matplotlib')]
a.binaries = [x for x in a.binaries if not x[0].startswith('numpy')]
a.binaries = [x for x in a.binaries if not x[0].startswith('scipy')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QuickBill',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='quickbill_icon.ico'  # Add your icon file here
)