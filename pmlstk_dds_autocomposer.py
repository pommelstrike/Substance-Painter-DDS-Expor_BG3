# BG3 DDS Exporter Plugin
# Copyright (C) 2023 Emil Eldstål
# Copyright (C) 2025 pmlstk
# This add-on is a fork of the BG3 DDS Exporter Plugin originally developed by Emil Eldstål (2023). It has been modified to support specific output formats.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = "pmlstk"
__version__ = "2.1.31"

from PySide2 import QtWidgets
from PySide2.QtCore import Qt
import substance_painter.ui
import substance_painter.event
import os
import configparser
import subprocess
from pathlib import Path

def config_ini(overwrite):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ini_file_path = os.path.join(script_dir, "BG3-DDS-Exporter-PluginSettings.ini")
    config = configparser.ConfigParser()
    if os.path.exists(ini_file_path):
        config.read(ini_file_path)
        if 'General' in config and 'TexConvDirectory' in config['General']:
            if not config['General']['TexConvDirectory'] or overwrite:
                config['General']['TexConvDirectory'] = choose_texconv_folder()
            TexConvPath = config['General']['TexConvDirectory']
        else:
            TexConvPath = choose_texconv_folder()
            config['General'] = {}
            config['General']['TexConvDirectory'] = TexConvPath
        with open(ini_file_path, 'w') as configfile:
            config.write(configfile)
    else:
        TexConvPath = choose_texconv_folder()
        with open(ini_file_path, 'w') as configfile:
            config['General'] = {}
            config['General']['TexConvDirectory'] = TexConvPath
            config.write(configfile)
    return TexConvPath

def choose_texconv_folder():
    path = QtWidgets.QFileDialog.getExistingDirectory(
        substance_painter.ui.get_main_window(), "Choose Texconv directory")
    return path + "/texconv.exe"

def convert_tga_to_dds(texconvPath, sourceTGA, overwrite):
    texconvPath = texconvPath.replace('\\', '/')
    sourceFolder = os.path.dirname(sourceTGA)
    outputFolder = sourceFolder.replace('\\', '/')
    os.makedirs(outputFolder, exist_ok=True)
    filename = sourceTGA
    if filename.endswith(".tga"):
        sourceFile = os.path.splitext(filename)[0]
        suffix = sourceFile.split('_')[-1].rstrip('_')
        # Map suffix to format
        format_options = {
            "PM": "BC1_UNORM",
            "MSK": "BC1_UNORM", #same setting on both msk labels
            "MSKcloth": "BC1_UNORM",
            "BM": "BC1_UNORM", #full or empty opacity/does not alphablend, i use to mask stuff out, gogo desirefeathers
            "NM": "BC3_UNORM",
            "BMA": "BC3_UNORM", #note for alphablending gradient / game used bma labels prior vt it seems, IT NOT THAT SERIES DUDE
            "CLEA": "BC3_UNORM",
            "HMVY": "BC3_UNORM",
        }
        format_option = format_options.get(suffix, "BC1_UNORM") #if you have some other suffix than mention, it default to BC1
        overwrite_option = "-y" if overwrite else ""
        outputFile = f"{sourceFile}.dds"
        texconv_cmd = [
            texconvPath,
            "-nologo",
            overwrite_option,
            "-o", outputFolder,
            "-f", format_option,
            os.path.join(sourceFolder, filename)
        ]
        try:
            # Run the command without showing a console window
            subprocess.run(texconv_cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print(f"Successfully converted {filename} to {outputFile}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert {filename}: {e}")

def convert_to_DDS(file):
    path = Path(file)
    if path.name[-3:] == "dds":
        path.rename(path.with_suffix('.DDS'))

def delete_tga(file):
    path = Path(file)
    if path.name[-3:] == "tga":
        path.unlink()

class BG3DDSPlugin:
    def __init__(self):
        self.export = True
        self.overwrite = True
        self.version = "0.1.1"
        self.log = QtWidgets.QTextEdit()
        self.window = QtWidgets.QWidget()
        self.TexConvPath = config_ini(False)
        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        # Settings group
        settings_group = QtWidgets.QGroupBox("Export Settings")
        settings_layout = QtWidgets.QHBoxLayout()
        settings_layout.setSpacing(10)
        checkbox = QtWidgets.QCheckBox("Export DDS files")
        checkbox.setChecked(True)
        checkbox_overwrite = QtWidgets.QCheckBox("Overwrite DDS files")
        checkbox_overwrite.setChecked(True)
        settings_layout.addWidget(checkbox)
        settings_layout.addWidget(checkbox_overwrite)
        settings_group.setLayout(settings_layout)
        # TexConv configuration group
        texconv_group = QtWidgets.QGroupBox("TexConv Configuration")
        texconv_layout = QtWidgets.QVBoxLayout()
        texconv_layout.setSpacing(10)
        self.texconv_path_label = QtWidgets.QLabel(f"TexConv Path: {self.TexConvPath}")
        self.texconv_path_label.setWordWrap(True)
        button_texconv = QtWidgets.QPushButton("Choose Texconv Location")
        button_convert = QtWidgets.QPushButton("Manually Convert TGA to DDS")
        texconv_layout.addWidget(self.texconv_path_label)
        texconv_layout.addWidget(button_texconv)
        texconv_layout.addWidget(button_convert)
        texconv_group.setLayout(texconv_layout)
        # Log group
        log_group = QtWidgets.QGroupBox("Log")
        log_layout = QtWidgets.QVBoxLayout()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(150)
        button_clear = QtWidgets.QPushButton("Clear Log")
        log_layout.addWidget(self.log)
        log_layout.addWidget(button_clear)
        log_group.setLayout(log_layout)
        # Version label
        version_label = QtWidgets.QLabel("Version: {}".format(self.version))
        version_label.setAlignment(Qt.AlignRight)
        # Add all to main layout
        main_layout.addWidget(settings_group)
        main_layout.addWidget(texconv_group)
        main_layout.addWidget(log_group)
        main_layout.addWidget(version_label)
        main_layout.addStretch()
        self.window.setLayout(main_layout)
        self.window.setWindowTitle("BG3 DDS Auto Converter")
        # Apply basic styling
        self.window.setStyleSheet("""
            QGroupBox { font-weight: bold; }
            QTextEdit { font-family: Consolas, monospace; }
            QPushButton { padding: 5px; }
        """)
        # Connect signals
        checkbox.stateChanged.connect(self.checkbox_export_change)
        checkbox_overwrite.stateChanged.connect(self.checkbox_overwrite_change)
        button_texconv.clicked.connect(self.button_texconv_clicked)
        button_clear.clicked.connect(self.button_clear_clicked)
        button_convert.clicked.connect(self.button_convert_clicked)
        substance_painter.ui.add_dock_widget(self.window)
        self.log.append("TexConv Path: {}".format(self.TexConvPath))
        connections = {
            substance_painter.event.ExportTexturesEnded: self.on_export_finished
        }
        for event, callback in connections.items():
            substance_painter.event.DISPATCHER.connect(event, callback)
    
    def button_texconv_clicked(self):
        self.TexConvPath = config_ini(True)
        self.texconv_path_label.setText(f"TexConv Path: {self.TexConvPath}")
        self.log.append("New TexConv Path: {}".format(self.TexConvPath))
    
    def button_clear_clicked(self):
        self.log.clear()
    
    def checkbox_export_change(self, state):
        self.export = state == Qt.Checked
    
    def checkbox_overwrite_change(self, state):
        self.overwrite = state == Qt.Checked
    
    def button_convert_clicked(self):
        # Allow user to select a TGA file for manual conversion
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            substance_painter.ui.get_main_window(), "Select TGA file", "", "TGA Files (*.tga)")
        if file_path:
            self.log.append(f"Manually converting: {file_path}")
            convert_tga_to_dds(self.TexConvPath, file_path, self.overwrite)
            convert_to_DDS(file_path[:-3] + "dds")
            delete_tga(file_path)
            self.log.append(f"Converted to: {file_path[:-3] + 'DDS'}")
    
    def __del__(self):
        substance_painter.ui.delete_ui_element(self.log)
        substance_painter.ui.delete_ui_element(self.window)
    
    def on_export_finished(self, res):
        if self.export:
            self.log.append(res.message)
            self.log.append("Exported files:")
            for file_list in res.textures.values():
                for file_path in file_list:
                    self.log.append(" {}".format(file_path))
            self.log.append("Converting to DDS files:")
            for file_list in res.textures.values():
                for file_path in file_list:
                    convert_tga_to_dds(self.TexConvPath, file_path, self.overwrite)
                    convert_to_DDS(file_path[:-3] + "dds")
                    delete_tga(file_path)
                    file_path = file_path[:-3] + "DDS"
                    self.log.append(" {}".format(file_path))
    
    def on_export_error(self, err):
        self.log.append("Export failed.")
        self.log.append(repr(err))

BG3_DDS_PLUGIN = None

def start_plugin():
    print("BG3 DDS Exporter Plugin Initialized")
    global BG3_DDS_PLUGIN
    BG3_DDS_PLUGIN = BG3DDSPlugin()

def close_plugin():
    print("BG3 DDS Exporter Plugin Shutdown")
    global BG3_DDS_PLUGIN
    del BG3_DDS_PLUGIN

if __name__ == "__main__":
    start_plugin()
__author__ = "pmlstk"
__version__ = "2.1.31"

from PySide2 import QtWidgets
from PySide2.QtCore import Qt
import substance_painter.ui
import substance_painter.event
import os
import configparser
import subprocess
from pathlib import Path
import json

def config_ini(overwrite):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ini_file_path = os.path.join(script_dir, "pmlstk-DDS-AutoComposer-PluginSettings.ini")
    config = configparser.ConfigParser()

    if os.path.exists(ini_file_path):
        config.read(ini_file_path)
        if 'General' in config and 'TexConvDirectory' in config['General']:
            if not config['General']['TexConvDirectory'] or overwrite:
                config['General']['TexConvDirectory'] = choose_texconv_folder()
            TexConvPath = config['General']['TexConvDirectory']
        else:
            TexConvPath = choose_texconv_folder()
            config['General'] = {}
            config['General']['TexConvDirectory'] = TexConvPath
        with open(ini_file_path, 'w') as configfile:
            config.write(configfile)
    else:
        TexConvPath = choose_texconv_folder()
        with open(ini_file_path, 'w') as configfile:
            config['General'] = {}
            config['General']['TexConvDirectory'] = TexConvPath
            config.write(configfile)

    return TexConvPath

def choose_texconv_folder():
    path = QtWidgets.QFileDialog.getExistingDirectory(
        substance_painter.ui.get_main_window(), 
        r"Texconv is located within your \SteamLibrary\steamapps\common\Baldurs Gate 3 Toolkit folder")
    return path + "/texconv.exe"

def convert_tga_to_dds(texconvPath, sourceTGA, overwrite, active_suffixes):
    texconvPath = texconvPath.replace('\\', '/')
    sourceFolder = os.path.dirname(sourceTGA)
    outputFolder = sourceFolder.replace('\\', '/')

    os.makedirs(outputFolder, exist_ok=True)

    filename = sourceTGA
    if filename.endswith(".tga"):
        sourceFile = os.path.splitext(filename)[0]
        suffix = sourceFile.split('_')[-1].rstrip('_')

        # Map suffix to format
        format_options = {
            "PM": {"format": "BC1_UNORM", "comment": "", "active": True},
            "MSK": {"format": "BC1_UNORM", "comment": "same setting on both msk labels", "active": True},
            "MSKcloth": {"format": "BC1_UNORM", "comment": "", "active": True},
            "BM": {"format": "BC1_UNORM", "comment": "full or empty opacity/does not alphablend, i use to mask stuff out, gogo desirefeathers", "active": True},
            "NM": {"format": "BC3_UNORM", "comment": "", "active": True},
            "BMA": {"format": "BC3_UNORM", "comment": "note for alphablending gradient / game used bma labels prior vt it seems, IT NOT THAT SERIES DUDE", "active": True},
            "CLEA": {"format": "BC3_UNORM", "comment": "", "active": True},
            "HMVY": {"format": "BC3_UNORM", "comment": "", "active": True},
        }
        #if you have some other suffix than mention, it default to BC1
        if suffix in active_suffixes and active_suffixes[suffix]["active"]:
            format_option = format_options.get(suffix, {"format": "BC1_UNORM"})["format"]
        else:
            format_option = "BC1_UNORM"
        overwrite_option = "-y" if overwrite else ""

        outputFile = f"{sourceFile}.dds"

        texconv_cmd = [
            texconvPath,
            "-nologo",
            overwrite_option,
            "-o", outputFolder,
            "-f", format_option,
            os.path.join(sourceFolder, filename)
        ]

        try:
            # Run the command without showing a console window
            subprocess.run(texconv_cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print(f"Successfully converted {filename} to {outputFile}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert {filename}: {e}")

def convert_to_DDS(file):
    path = Path(file)
    if path.name[-3:] == "dds":
        path.rename(path.with_suffix('.DDS'))

def delete_tga(file):
    path = Path(file)
    if path.name[-3:] == "tga":
        path.unlink()

class PmlstkDDSAutoComposerPlugin:
    def __init__(self):
        self.export = True
        self.overwrite = True
        self.version = "0.1.1"
        self.suffix_settings = {
            "PM": {"format": "BC1_UNORM", "comment": "", "active": True},
            "MSK": {"format": "BC1_UNORM", "comment": "same setting on both msk labels", "active": True},
            "MSKcloth": {"format": "BC1_UNORM", "comment": "", "active": True},
            "BM": {"format": "BC1_UNORM", "comment": "full or empty opacity/does not alphablend, i use to mask stuff out, gogo desirefeathers", "active": True},
            "NM": {"format": "BC3_UNORM", "comment": "", "active": True},
            "BMA": {"format": "BC3_UNORM", "comment": "note for alphablending gradient / game used bma labels prior vt it seems, IT NOT THAT SERIES DUDE", "active": True},
            "CLEA": {"format": "BC3_UNORM", "comment": "", "active": True},
            "HMVY": {"format": "BC3_UNORM", "comment": "", "active": True},
        }

        self.log = QtWidgets.QTextEdit()
        self.window = QtWidgets.QWidget()
        self.TexConvPath = config_ini(False)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Suffix Settings group
        suffix_group = QtWidgets.QGroupBox("Suffix Settings")
        suffix_layout = QtWidgets.QVBoxLayout()
        suffix_layout.setContentsMargins(10, 10, 10, 10)
        suffix_layout.setSpacing(15)

        # Import/Export buttons (outside scroll area)
        io_layout = QtWidgets.QHBoxLayout()
        import_button = QtWidgets.QPushButton("Import Suffix Settings")
        export_button = QtWidgets.QPushButton("Export Suffix Settings")
        io_layout.addWidget(import_button)
        io_layout.addWidget(export_button)
        suffix_layout.addLayout(io_layout)

        # Scroll area for suffix table
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        # Suffix table
        self.suffix_table = QtWidgets.QTableWidget()
        self.suffix_table.setColumnCount(2)
        self.suffix_table.setHorizontalHeaderLabels(["Suffix", "Format"])
        self.suffix_table.setRowCount(len(self.suffix_settings))
        self.suffix_table.horizontalHeader().setStretchLastSection(True)
        self.suffix_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.suffix_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.update_suffix_table()
        scroll_layout.addWidget(self.suffix_table)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        suffix_layout.addWidget(scroll_area)
        suffix_group.setLayout(suffix_layout)

        # TexConv Configuration group
        texconv_group = QtWidgets.QGroupBox("TexConv Configuration")
        texconv_layout = QtWidgets.QVBoxLayout()
        texconv_layout.setSpacing(10)
        self.texconv_path_label = QtWidgets.QLabel(f"TexConv Path: {self.TexConvPath}")
        self.texconv_path_label.setWordWrap(True)
        button_texconv = QtWidgets.QPushButton("Choose Texconv Location")
        texconv_layout.addWidget(self.texconv_path_label)
        texconv_layout.addWidget(button_texconv)
        texconv_group.setLayout(texconv_layout)

        # Log group
        log_group = QtWidgets.QGroupBox("Log")
        log_layout = QtWidgets.QVBoxLayout()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(150)
        button_clear = QtWidgets.QPushButton("Clear Log")
        log_layout.addWidget(self.log)
        log_layout.addWidget(button_clear)
        log_group.setLayout(log_layout)

        # Export Settings group
        settings_group = QtWidgets.QGroupBox("Export Settings")
        settings_layout = QtWidgets.QHBoxLayout()
        settings_layout.setSpacing(10)
        self.checkbox_export = QtWidgets.QCheckBox("Export DDS files")
        self.checkbox_export.setChecked(True)
        self.checkbox_overwrite = QtWidgets.QCheckBox("Overwrite DDS files")
        self.checkbox_overwrite.setChecked(True)
        settings_layout.addWidget(self.checkbox_export)
        settings_layout.addWidget(self.checkbox_overwrite)
        settings_group.setLayout(settings_layout)

        # Custom Suffix group
        custom_group = QtWidgets.QGroupBox("Custom Suffix")
        custom_layout = QtWidgets.QHBoxLayout()
        self.suffix_input = QtWidgets.QLineEdit()
        self.suffix_input.setPlaceholderText("Enter new suffix (e.g., NEW)")
        self.suffix_input.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.format_input = QtWidgets.QComboBox()
        self.format_input.addItems(["BC1_UNORM", "BC3_UNORM", "BC7_UNORM"])
        self.format_input.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.comment_input = QtWidgets.QLineEdit()
        self.comment_input.setPlaceholderText("Optional comment")
        self.comment_input.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        add_suffix_button = QtWidgets.QPushButton("Add Suffix")
        custom_layout.addWidget(self.suffix_input)
        custom_layout.addWidget(self.format_input)
        custom_layout.addWidget(self.comment_input)
        custom_layout.addWidget(add_suffix_button)
        custom_group.setLayout(custom_layout)

        # Version label
        version_label = QtWidgets.QLabel(f"Version: {self.version}")
        version_label.setAlignment(Qt.AlignRight)

        # Add all to main layout
        main_layout.addWidget(suffix_group)
        main_layout.addWidget(texconv_group)
        main_layout.addWidget(log_group)
        main_layout.addWidget(settings_group)
        main_layout.addWidget(custom_group)
        main_layout.addWidget(version_label)
        main_layout.addStretch()

        self.window.setLayout(main_layout)
        self.window.setWindowTitle("pmlstk BG3 DDS AutoComposer")
        self.window.setMinimumSize(400, 300)

        # Apply basic styling
        self.window.setStyleSheet("""
            QGroupBox { font-weight: bold; }
            QTextEdit { font-family: Consolas, monospace; }
            QPushButton { padding: 5px; }
            QTableWidget { gridline-color: #d3d3d3; }
        """)

        # Connect signals
        self.checkbox_export.stateChanged.connect(self.checkbox_export_change)
        self.checkbox_overwrite.stateChanged.connect(self.checkbox_overwrite_change)
        button_texconv.clicked.connect(self.button_texconv_clicked)
        button_clear.clicked.connect(self.button_clear_clicked)
        add_suffix_button.clicked.connect(self.add_suffix_clicked)
        import_button.clicked.connect(self.import_suffix_settings)
        export_button.clicked.connect(self.export_suffix_settings)

        substance_painter.ui.add_dock_widget(self.window)
        self.log.append("TexConv Path: {}".format(self.TexConvPath))
        self.log.append("Tip: Drag the 'pmlstk BG3 DDS AutoComposer' panel to dock near the Imported Resources tab.")

        connections = {
            substance_painter.event.ExportTexturesEnded: self.on_export_finished
        }
        for event, callback in connections.items():
            substance_painter.event.DISPATCHER.connect(event, callback)

    def update_suffix_table(self):
        self.suffix_table.setRowCount(len(self.suffix_settings))
        for row, (suffix, settings) in enumerate(self.suffix_settings.items()):
            # Suffix with checkbox
            checkbox_item = QtWidgets.QTableWidgetItem(suffix)
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Checked if settings["active"] else Qt.Unchecked)
            self.suffix_table.setItem(row, 0, checkbox_item)
            # Format
            self.suffix_table.setItem(row, 1, QtWidgets.QTableWidgetItem(settings["format"]))
        self.suffix_table.itemChanged.connect(self.on_table_item_changed)

    def on_table_item_changed(self, item):
        if item.column() == 0:  # Suffix column with checkbox
            suffix = item.text()
            self.suffix_settings[suffix]["active"] = item.checkState() == Qt.Checked
            self.log.append(f"Suffix {suffix} {'enabled' if item.checkState() == Qt.Checked else 'disabled'}")

    def add_suffix_clicked(self):
        suffix = self.suffix_input.text().strip().upper()
        format_type = self.format_input.currentText()
        comment = self.comment_input.text().strip()
        if suffix and suffix not in self.suffix_settings:
            self.suffix_settings[suffix] = {"format": format_type, "comment": comment, "active": True}
            self.update_suffix_table()
            self.log.append(f"Added suffix: {suffix} → {format_type} ({comment})")
            self.suffix_input.clear()
            self.comment_input.clear()
        elif suffix in self.suffix_settings:
            self.log.append(f"Error: Suffix {suffix} already exists")
        else:
            self.log.append("Error: Suffix cannot be empty")

    def import_suffix_settings(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            substance_painter.ui.get_main_window(), "Import Suffix Settings", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_settings = json.load(f)
                for suffix, settings in imported_settings.items():
                    if isinstance(settings, dict) and "format" in settings and "comment" in settings and "active" in settings:
                        self.suffix_settings[suffix] = settings
                self.update_suffix_table()
                self.log.append(f"Imported suffix settings from {file_path}")
            except Exception as e:
                self.log.append(f"Error importing settings: {str(e)}")

    def export_suffix_settings(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            substance_painter.ui.get_main_window(), "Export Suffix Settings", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.suffix_settings, f, indent=4)
                self.log.append(f"Exported suffix settings to {file_path}")
            except Exception as e:
                self.log.append(f"Error exporting settings: {str(e)}")

    def button_texconv_clicked(self):
        self.TexConvPath = config_ini(True)
        self.texconv_path_label.setText(f"TexConv Path: {self.TexConvPath}")
        self.log.append("New TexConv Path: {}".format(self.TexConvPath))

    def button_clear_clicked(self):
        self.log.clear()

    def checkbox_export_change(self, state):
        self.export = state == Qt.Checked

    def checkbox_overwrite_change(self, state):
        self.overwrite = state == Qt.Checked

    def __del__(self):
        substance_painter.ui.delete_ui_element(self.log)
        substance_painter.ui.delete_ui_element(self.window)

    def on_export_finished(self, res):
        if self.export:
            self.log.append(res.message)
            self.log.append("Exported files:")
            for file_list in res.textures.values():
                for file_path in file_list:
                    self.log.append("  {}".format(file_path))
            self.log.append("Converting to DDS files:")
            for file_list in res.textures.values():
                for file_path in file_list:
                    convert_tga_to_dds(self.TexConvPath, file_path, self.overwrite, self.suffix_settings)
                    convert_to_DDS(file_path[:-3] + "dds")
                    delete_tga(file_path)
                    file_path = file_path[:-3] + "DDS"
                    self.log.append("  {}".format(file_path))

    def on_export_error(self, err):
        self.log.append("Export failed.")
        self.log.append(repr(err))

PMLSTK_DDS_AUTOCOMPOSER_PLUGIN = None

def start_plugin():
    print("pmlstk DDS AutoComposer Initialized")
    global PMLSTK_DDS_AUTOCOMPOSER_PLUGIN
    PMLSTK_DDS_AUTOCOMPOSER_PLUGIN = PmlstkDDSAutoComposerPlugin()

def close_plugin():
    print("pmlstk DDS AutoComposer Shutdown")
    global PMLSTK_DDS_AUTOCOMPOSER_PLUGIN
    del PMLSTK_DDS_AUTOCOMPOSER_PLUGIN

if __name__ == "__main__":
    start_plugin()
