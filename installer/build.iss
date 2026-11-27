; 星空汉化 · Substance 3D Painter 中文插件 安装脚本
; 构建：先运行根目录 build.bat 生成 dist\xingkong_zh，再运行本目录 build.bat
; 直接编译：ISCC.exe build.iss（可用 ISCC 环境变量指定编译器路径）
#define MyAppName "星空汉化 · SP 中文插件"
#define MyAppVersion "0.1.3"
#define MyPublisher "星空汉化"
#define MyUrl "https://space.bilibili.com/177308205"
#define SrcDir AddBackslash(SourcePath) + "..\dist\xingkong_zh"
#define ProjectDir AddBackslash(SourcePath) + ".."
#define PluginDirName "xingkong_zh"

[Setup]
AppId={{6F1B2C74-8E52-4C7B-9E0A-3F5B1D2A7C91}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyPublisher}
AppPublisherURL={#MyUrl}
AppSupportURL={#MyUrl}
AppUpdatesURL={#MyUrl}
VersionInfoVersion=0.1.3.0
VersionInfoCompany={#MyPublisher}
VersionInfoDescription={#MyAppName}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion=0.1.3.0
DefaultDirName={userdocs}\Adobe\Adobe Substance 3D Painter\python\plugins\{#PluginDirName}
; 用户浏览选择目录时，不要把 DefaultDirName 的最后一段拼上去
AppendDefaultDirName=no
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=no
AlwaysShowDirOnReadyPage=yes
DirExistsWarning=no
DisableWelcomePage=yes
UsePreviousAppDir=no
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
InfoBeforeFile={#ProjectDir}\installer\安装说明.txt
OutputDir={#ProjectDir}\dist
OutputBaseFilename=SP_zh-CN_v{#MyAppVersion}_Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=no
RestartApplications=no
UninstallDisplayName={#MyAppName}
Uninstallable=yes
CreateUninstallRegKey=yes
AllowNoIcons=yes
ShowLanguageDialog=no
SetupLogging=yes

[Languages]
; 自定义中文文案，不用 Inno 自带语言文件
Name: "chinesesimplified"; MessagesFile: "Chinese_Star.isl"

[Files]
; 插件本体：Python 入口、原生引擎、词库
Source: "{#SrcDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; 清掉旧版本生成的 Python 缓存，避免加载到过期字节码
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\xingkong_zh\__pycache__"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\xingkong_zh\__pycache__"

[Registry]
; 让插件默认随 Painter 启动（等同在 Python > Plugins 菜单里勾选）；卸载时移除
Root: HKCU; Subkey: "Software\Adobe\Adobe Substance 3D Painter\python_plugins\{#PluginDirName}"; ValueType: string; ValueName: "launch_at_start"; ValueData: "on"; Flags: uninsdeletekey

[Run]
Filename: "{code:GetPainterExe}"; WorkingDir: "{code:GetPainterDir}"; Description: "启动 Substance 3D Painter"; Flags: postinstall nowait skipifsilent; Check: PainterFound
Filename: "{app}"; Description: "打开插件目录"; Flags: postinstall shellexec nowait skipifsilent unchecked

[Code]
// 白色主题约定：安装开始前点取消/关闭不弹确认
procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
begin
  if CurPageID < wpInstalling then
    Confirm := False;
end;

// 宿主运行中时插件 DLL 被占用，直接提示退出，避免装出半套文件
procedure CurStepChanged(CurStep: TSetupStep);
var
  Target, Probe: String;
begin
  if CurStep = ssInstall then
  begin
    Target := ExpandConstant('{app}\native\xingkong_zh_qt6.dll');
    if FileExists(Target) then
    begin
      Probe := Target + '.locktest';
      if not RenameFile(Target, Probe) then
      begin
        MsgBox('请先完全退出 Substance 3D Painter，再运行本安装程序。', mbError, MB_OK);
        Abort;
      end;
      RenameFile(Probe, Target);
    end;
  end;
end;

// 定位 Painter 安装路径：优先读 Windows App Paths，其次常见安装目录
function GetPainterExe(Param: String): String;
var
  Value: String;
  Candidates: array[0..2] of String;
  I: Integer;
begin
  if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Adobe Substance 3D Painter.exe', '', Value) and FileExists(Value) then
  begin
    Result := Value;
    Exit;
  end;
  if RegQueryStringValue(HKCU, 'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Adobe Substance 3D Painter.exe', '', Value) and FileExists(Value) then
  begin
    Result := Value;
    Exit;
  end;
  Candidates[0] := ExpandConstant('{pf}\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe');
  Candidates[1] := ExpandConstant('{pf32}\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe');
  Candidates[2] := ExpandConstant('{sd}\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe');
  for I := 0 to 2 do
    if FileExists(Candidates[I]) then
    begin
      Result := Candidates[I];
      Exit;
    end;
  Result := '';
end;

function GetPainterDir(Param: String): String;
begin
  Result := ExtractFileDir(GetPainterExe(''));
end;

function PainterFound: Boolean;
begin
  Result := GetPainterExe('') <> '';
end;
