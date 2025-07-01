 # -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Recoger todo lo necesario de mne
mne_datas, mne_binaries, mne_hiddenimports = collect_all('mne')

# Recoger todo lo necesario de datashader
ds_datas, ds_binaries, ds_hiddenimports = collect_all('datashader')

a = Analysis(
    ['Lunas.py'],
    pathex=['.'],
    binaries=mne_binaries + ds_binaries,
    datas=[
        ('img/carpeta.png', 'img'),
        ('img/check.png', 'img'),
        ('img/gom.png', 'img'),
        ('img/lunaico.png', 'img'),
        ('img/send.png', 'img'),
        *mne_datas,
        *ds_datas
    ],
    hiddenimports=[
        'notebook.services.shutdown',
        *mne_hiddenimports,
        *ds_hiddenimports
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,  # <= Se fuerza la inclusión de archivos sin comprimir
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Lunas',
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
    icon='lunaico.png'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Lunas'
)