# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['poincare.py'],
    pathex=['.'],  # Asegura que esté en la ruta actual
    binaries=[],
    datas=[
        ('img/elipse.png', 'img'),
        ('img/gom.png', 'img'),
        ('img/gua.png', 'img'),
        ('img/lup.png', 'img'),
        ('img/open.png', 'img'),
        ('img/pcr.png', 'img'),
        ('img/stadistics.png', 'img'),
        ('img/topo.png', 'img'),
        ('img/staisticss.png', 'img'),
        ('statistics_1.py', '.')  # Agregado como módulo
    ],
    hiddenimports=[
        'scipy.special._cdflib',
        'statistics_1'  # Se especifica como hiddenimport también
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Poincare',
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
    icon='pcr.png'  # Icono de la aplicación
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Poincare'
)
