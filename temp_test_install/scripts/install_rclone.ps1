# Rclone Setup
$Url = "https://downloads.rclone.org/v1.66.0/rclone-v1.66.0-windows-amd64.zip"
$Zip = "rclone.zip"
$Bin = "bin"

# 1. Prepare Directory
if (!(Test-Path $Bin)) { New-Item -ItemType Directory -Path $Bin -Force }

# 2. Download
Write-Host "Downloading Rclone..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $Url -OutFile $Zip

# 3. Unzip
Write-Host "Extracting..."
Expand-Archive -Path $Zip -DestinationPath "$Bin\temp" -Force

# 4. Move
$Src = Get-ChildItem -Path "$Bin\temp" -Directory | Select-Object -First 1
$Dest = "$Bin\rclone"
if (Test-Path $Dest) { Remove-Item $Dest -Recurse -Force }
Move-Item -Path $Src.FullName -Destination $Dest

# 5. Cleanup
Remove-Item $Zip -Force
Remove-Item "$Bin\temp" -Recurse -Force

Write-Host "Done."
.\bin\rclone\rclone.exe version
Write-Host "Next Step: .\bin\rclone\rclone.exe config"
