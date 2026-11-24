#define AppName "Password Manager"
#define AppVersion "1.1.2"
#define AppPublisher "MCnima"
#define AppExeName "PasswordManager-v1.1.2.exe"

[Setup]
AppId={{C4D4A4A9-2A2B-4B2D-9F42-52C51A95AE31}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=..\dist
OutputBaseFilename=PasswordManager-Setup-v1.1.2
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\media\app_icon.ico

[Files]
Source: "..\dist\PasswordManager-v1.1.2.exe"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
