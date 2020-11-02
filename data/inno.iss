[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{8A0E36A6-DE56-46B8-BCC3-C16D1BC759CC}
AppName=Universal Radio Hacker
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayName=Universal Radio Hacker
AppPublisher=Johannes Pohl
AppPublisherURL=https://github.com/jopohl/urh
AppSupportURL=https://github.com/jopohl/urh
AppUpdatesURL=https://github.com/jopohl/urh
DefaultDirName={commonpf}\Universal Radio Hacker
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=Universal.Radio.Hacker-{#MyAppVersion}-{#Arch}
Compression=lzma2/ultra
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\pyinstaller\urh\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{commonprograms}\Universal Radio Hacker"; Filename: "{app}\urh.exe"
Name: "{commondesktop}\Universal Radio Hacker"; Filename: "{app}\urh.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\urh.exe"; Description: "{cm:LaunchProgram,Universal Radio Hacker}"; Flags: nowait postinstall skipifsilent
