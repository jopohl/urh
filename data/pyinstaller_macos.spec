# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['src/urh/main.py'],
             pathex=[],
             binaries=[],
             datas=[('src/urh/plugins', 'urh/plugins')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=['matplotlib'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='data/icons/appicon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
app = BUNDLE(coll,
             name='main.app',
             icon='./data/icons/appicon.icns',
             bundle_identifier=None,
             info_plist={
            'NSRequiresAquaSystemAppearance': True,
            'NSMicrophoneUsageDescription': 'URH needs access to your microphone to capture signals via Soundcard.',
            'CFBundleDisplayName': 'URH',
            'CFBundleName': 'URH'
            },)
