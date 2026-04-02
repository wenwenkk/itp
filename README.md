# ITP 抢票 GUI 程序 - 打包与发行说明

本仓库包含一个可运行的 ITP 抢票桌面程序（PySimpleGUI + requests），以及完整的打包发行流程。你可以按需在 macOS/Windows 上运行、打包、生产安装包。

---

## 1. 环境准备

- Python 3.8+
- Git（可选）

### 1.1 安装依赖

macOS / Linux / Windows：

```bash
python3 -m pip install --user requests PySimpleGUI pyinstaller
```

> 如果你使用 `python` 命令不是 Python 3，请使用 `python3`。

### 1.2 增加 PATH（当命令不可用时）

macOS/Linux：

```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
```

Windows（PowerShell）：

```powershell
$env:Path += ";$HOME\AppData\Roaming\Python\Python39\Scripts"
```

---

## 2. 直接运行（调试）

```bash
cd ~/itp_sniper_gui
python3 itp_sniper_gui.py
```

1. 填写用户名、密码
2. 填写活动 ID、座位档位
3. 填写 API URL（登录/库存查询/下单）
4. 可选代理、重试、间隔选项
5. 点击 `开始抢票`

---

## 3. 一键打包脚本（macOS + Windows）

### 3.1 macOS 一键脚本：`build_macos.sh`

```bash
#!/bin/bash
set -e

PROJECT_DIR="$HOME/itp_sniper_gui"
cd "$PROJECT_DIR"

# 清理旧构建
rm -rf build dist itp_sniper_gui.spec

# PyInstaller 生成 onedir（避免 onefile 与 windowed 的 macOS 冲突）
python3 -m PyInstaller --noconfirm --onedir --windowed itp_sniper_gui.py

echo "Build done: $PROJECT_DIR/dist/itp_sniper_gui" 

# 可选打包dmg
hdiutil create -volname itp_sniper_gui -srcfolder "$PROJECT_DIR/dist" -ov -format UDZO "$PROJECT_DIR/itp_sniper_gui.dmg"

echo "DMG done: $PROJECT_DIR/itp_sniper_gui.dmg"
```

### 3.2 Windows 一键脚本：`build_windows.ps1`

```powershell
$PROJECT_DIR = "$HOME\itp_sniper_gui"
Set-Location $PROJECT_DIR

Remove-Item -Recurse -Force .\build, .\dist, .\itp_sniper_gui.spec -ErrorAction SilentlyContinue

python -m PyInstaller --noconfirm --onefile --windowed itp_sniper_gui.py

Write-Host "Build done: $PROJECT_DIR\dist\itp_sniper_gui.exe"

# 可选 NSIS 使用样例（需要安装 NSIS）
# & "C:\Program Files (x86)\NSIS\makensis.exe" -V2 "installer.nsi"
```

以上脚本直接放在项目目录，执行：

macOS：

```bash
chmod +x ~/itp_sniper_gui/build_macos.sh
~/itp_sniper_gui/build_macos.sh
```

Windows：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
cd $HOME\itp_sniper_gui
.\build_windows.ps1
```

---

## 4. 生成安装包（可选）

### 4.1 macOS DMG

```bash
cd ~/itp_sniper_gui
hdiutil create -volname itp_sniper_gui -srcfolder dist -ov -format UDZO itp_sniper_gui.dmg
```

### 4.2 Windows NSIS 安装包（要求已安装 NSIS）

创建 `installer.nsi`：

```nsis
!include "MUI2.nsh"
Name "ITP 抢票 GUI"
OutFile "itp_sniper_gui_installer.exe"
InstallDir "$PROGRAMFILES\itp_sniper_gui"
Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  File "dist\itp_sniper_gui.exe"
  CreateShortCut "$SMPROGRAMS\itp_sniper_gui.lnk" "$INSTDIR\itp_sniper_gui.exe"
SectionEnd
```

执行：

```powershell
makensis installer.nsi
```

---

## 5. 发行所需文本信息

请在 release Notes 中注明：

- 目标平台：macOS 13+/ARM + x64（根据宿主环境）
- Windows 10+/11
- 依赖：Python、requests、PySimpleGUI
- 风险声明：仅作学习用途，禁止违法抢票，遵守服务条款

---

## 6. 合规与风险提示

- 本工具仅作测试/学习，请先征得目标平台授权。未经授权的自动抢票存在封号与法律风险。
- 频率控制、随机 UA、代理只是减轻检测概率，不能“绕监管”。
- 遇到验证码/滑动验证应暂停并人工输入。

---

## 7. 常见问题

- `pyinstaller` 命令找不到：请使用 `python3 -m PyInstaller` 或调整 PATH；
- 运行 GUI 但不响应：检查网络、接口及 token/cookies；
- 经常被封：降低频率，使用独立账号和代理，避免短时间爆发请求。
