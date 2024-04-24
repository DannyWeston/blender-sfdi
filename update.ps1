$version = "3.6"

$appdata = $env:APPDATA

$addon = "sfdi_addon"

$blender_addons = ("Blender\" + $version + "\scripts\addons\")

# Remove already installed addon
if (Test-Path ($blender_addons + $addon)) {
	Remove-Item ($blender_addons + $addon) -Recurse -Force
}

# Copy files across to new directory
Copy-Item $addon $blender_addons -Recurse