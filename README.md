# Blender addon for SFDI

## Overview

This repository consists of the source code for a hard-addon for Blender 3.6. 

In here you can add different camera and projector configurations for fringe projection (and eventually photogrammetry) and run simulations to generate near-real outputs (depending on your scene configuration).

It is currently managed by Daniel Weston, University of Nottingham, Optics and Photonics. Any questions please contact by email (psydw2@nottingham.ac.uk). 

### Workaround

The reason why this is a hard-addon as it requires its own copy of Blender to install and it is strongly suggested not to do it on any main-install of Blender.

This is because Blender does not currently provide a mechanism for using third-party pip packages with addons. To work around this, this addon provides Blender with its own virtual environment which contains Python with the pip packages installed.

Eventually once Blender does provide this functionality, this addon will be updated to not be as "hacky".

## Examples

TODO: Add some examples

## Installation

### Requirements

For the installation of this addon you will need a few things. These are:

- Windows-based operating system
- A copy of this repository
- Blender 3.6 portable found [here](https://www.blender.org/download/release/Blender3.6/blender-3.6.11-windows-x64.zip)

### Steps

1. First download a copy of this repository into a place of your choice.

2. Extract the downloaded Blender version, it will output a folder. 

3. Rename the extracted folder to "Blender".

4. Place this directory into the root of your reopsitory copy.

5. Run the "Install" shortcut in order to install the addon and its features.

6. Run the "Blender" shortcut and the application should load successfully.

Navigating to "Edit > Preferences > Addons" should now show you that the addon is installed and enabled.

### Extending the codebase

If you wish to install the codebase for the addon, you will need to use the "Update" shortcut in the repository root in order to tell Blender that you have updated the addon. This simply clears out the existing addon files, and replaces them with a copy of the new ones.

If you have Blender open you will need to click the icon at the top right, then click "System > Reload Scripts". If you have no compilation errors then it should work fine, otherwise check the shell for any error messages, fix them in your software, and redo this process.

### Notes

Theoretically this should work on Linux, but you will need to tweak the installation script to work on Linux systems which shouldn't be too hard.

You can use this addon with a non-portable version of Blender, but it is not recommended as the setup involves changing some of the Blender-specific setup and is non-reversible (i.e: to revert you will need to reinstall).