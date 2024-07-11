# Environment variables

$version = "3.6"

$portable = "Blender\portable"

$python = ("Blender\" + $version + "\python\bin\python.exe")



# Create portable folder 

echo "Creating portable folder..."

New-Item -ItemType Directory -Force -Path $portable | Out-Null



# Setup virtual environment

echo "Installing necessary python packages..."

& $python "-m" "pip" "install" "-r" "requirements.txt"



# Check for updates

# & .\update.ps1

echo "Installation finished!"