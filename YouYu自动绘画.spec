# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['modern_main.py'],
    pathex=[],
    binaries=[],
    datas=[('066fb186-3172-4c45-9c26-48873ea6665d.tmp.ico', '.'), ('IMG_4639.png', '.'), ('1763310716369.jpg', '.'), ('version_info.py', '.'), ('version.json', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'scipy', 'jupyter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='YouYu自动绘画',
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
    icon=['066fb186-3172-4c45-9c26-48873ea6665d.tmp.ico'],
)
