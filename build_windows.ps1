$ErrorActionPreference = 'Stop'
$PROJECT_DIR = "$HOME\itp_sniper_gui"
Set-Location $PROJECT_DIR

Remove-Item -Recurse -Force .\build, .\dist, .\itp_sniper_gui.spec -ErrorAction SilentlyContinue

python -m PyInstaller --noconfirm --onefile --windowed itp_sniper_gui.py

Write-Host "Build done: $PROJECT_DIR\dist\itp_sniper_gui.exe"

# 可选 NSIS 打包 (需要提前安装 NSIS)
# & "C:\Program Files (x86)\NSIS\makensis.exe" -V2 "installer.nsi"
