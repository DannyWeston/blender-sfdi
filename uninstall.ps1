# Environment variables

$version = "3.6"

$python = ("Blender\" + $version + "\python\bin\python.exe")



# Setup virtual environment

& $python "-m" "pip" "uninstall" "-r" "requirements.txt" "-y"



# Check for updates

# & .\update.ps1

echo "Uninstalled"