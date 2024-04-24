$version = "3.6"

$venv = ".venv\"

$python = ("Blender\" + $version + "\python")



echo "Setting up virtual environment"

# Activate venv
& ($venv + "\Scripts\activate.ps1")



echo "Replacing python path"

# Rename python dir to stop Blender from using it
if (Test-Path $python){
	Rename-Item -Path $python -NewName "_python"
}



echo "Installing addon"

# Install addon to correct directory
& .\update.ps1

# Finished!
echo "Finished"