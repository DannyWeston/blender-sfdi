$version = "3.6"

$venv = ".venv\"

# Activate venv
& ($venv + "\Scripts\activate.ps1")

# Rename python dir to stop Blender from using it
Rename-Item -Path ("Blender\" + $version + "\python") -NewName "_python"

# Install addon to correct directory
& update_addon.ps1

# Finished!
echo "Finished installing addon!"