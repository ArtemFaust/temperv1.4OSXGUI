# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['/Users/artem/PycharmProjects/TemperV1.4Gui'],
             binaries=[],
             datas=[('ui', 'ui'), ('icons', 'icons')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='TemperV1.4',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='TemperV1.4')
app = BUNDLE(coll,
             name='TemperV1.4.app',
             icon=None,
             bundle_identifier=None)
