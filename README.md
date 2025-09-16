# pmlstk DDS AutoComposer
![banner](https://i.ibb.co/v45GpVhT/v1sp-addon-0-5x.png)
## Overview

pmlstk DDS AutoComposer is a Substance Painter plugin designed to automate the conversion of exported TGA textures to DDS format, specifically tailored for Baldur's Gate 3 (BG3) modding workflows. This plugin is a fork of the original Starfield DDS Exporter Plugin developed by Emil Eldstål in 2023, with enhancements including customizable suffix management, JSON-based import/export of settings, and an improved user interface for greater flexibility in texture processing.

## Features

- Automatic conversion of TGA files to DDS using TexConv (from the Baldur's Gate 3 Toolkit).
- Customizable suffix mappings for DDS compression formats (e.g., BC1_UNORM, BC3_UNORM).
- Enable/disable suffixes via a user-friendly table interface.
- Support for adding custom suffixes with optional comments.
- Import and export suffix settings as JSON files.
- Configurable TexConv path with persistent settings stored in an INI file.
- Logging panel for monitoring export and conversion processes.
- Options to toggle DDS export and overwrite existing files.

## Installation

1. **Prerequisites**:
   - Substance Painter (compatible with PySide2).
   - TexConv executable from the Baldur's Gate 3 Toolkit (typically located in `\SteamLibrary\steamapps\common\Baldurs Gate 3 Toolkit`).

2. **Download and Setup**:
   - Clone or download this repository.
   - Place the `pmlstk_dds_autocomposer.py` file in your Substance Painter plugins directory (e.g., `Documents\Adobe\Adobe Substance 3D Painter\python\plugins`).
   - Ensure the `LICENSE` file is included in the repository root for GPL compliance.

3. **Loading the Plugin**:
   - Launch Substance Painter.
   - Navigate to `Python > Plugins > Reload All Plugins` if necessary.
   - The plugin will appear as a dockable panel titled "pmlstk BG3 DDS AutoComposer".

## Usage

1. **Configuration**:
   - Open the plugin panel.
   - Set the TexConv path if not already configured (prompted on first use).
   - Customize suffix settings in the "Suffix Settings" group: Enable/disable suffixes, add new ones, or import/export configurations.

2. **Exporting Textures**:
   - In Substance Painter, export textures as TGA files.
   - The plugin automatically detects the export event and converts files to DDS based on active suffix mappings.
   - Monitor the process in the "Log" group.

3. **Manual Conversion**:
   - Not directly supported in this version; conversions are triggered on export.

For detailed code-level documentation, refer to the source file comments.

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program (see the `LICENSE` file in the repository root). If not, see <https://www.gnu.org/licenses/>.

## Acknowledgements

- Original plugin: Starfield DDS Exporter by Emil Eldstål (2023).
- This fork includes modifications for enhanced customization and usability by pmlstk (2025).

If you encounter issues or have suggestions, please open an issue on GitHub.
