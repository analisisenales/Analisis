# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['fractales.py'],
    pathex=['.'],  # Asegura que esté en la ruta actual
    binaries=[],
    datas=[
        ('img/car2.png', 'img'),
        ('img/cua.png', 'img'),
        ('img/cuar.png', 'img'),
        ('img/cuav.png', 'img'),
        ('img/gom.png', 'img'),
        ('img/gua.png', 'img'),
        ('img/lup.png', 'img'),
        ('img/tri.png', 'img'),
        ('img/tria.png', 'img')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Fractales',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Oculta la consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='car2.png'  # Icono de la aplicación
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Fractales'
)
