# Blender addon for SFDI

## Overview

This repository consists of the source code for a extension for Blender 4.2. 

In here you can add different camera and projector configurations for fringe projection (and eventually photogrammetry) and run simulations to generate near-real outputs (depending on your scene configuration).

It is currently managed by Daniel Weston, University of Nottingham, Optics and Photonics. For any questions please contact by email (psydw2@nottingham.ac.uk). 

## Examples

TODO: Add some examples

### Requirements

For the installation of this addon you will need a Windows or Linux based operating system, and Blender version 4.2 which can be found [here](https://www.blender.org/download/release/Blender4.2/). All versions of the addon can be found [here](), and instructions to install local addons can be found on the [Blender website](https://docs.blender.org/manual/en/latest/editors/preferences/extensions.html#install).

Version 4.2 is used because the extension makes use of third-party Python packages and this functionality is only available in version 4.2 or greater of Blender.

This package has the dependency on my other repository which contains all of the underlying functionality for how SFDI works, and can be found [here](https://github.com/DannyWeston/sfdi).

If you wish to fork and compile your own version of the add-on, download the source code from this repository, and compile the extension using the CLI instruction found [here](https://docs.blender.org/manual/en/dev/advanced/extensions/command_line_arguments.html#subcommand-build). Note that if you use any other third-party packages in your fork of the addon you will need to add them to the "wheels" section in the "blender_manifest.toml" file.

It is recommended to use a portable version of Blender for development as it can become cumbersome for managing application preferences across different versions.