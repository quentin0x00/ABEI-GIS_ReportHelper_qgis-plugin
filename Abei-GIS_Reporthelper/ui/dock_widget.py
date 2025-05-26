from ..imports import *
from ..config import Config
from .config_window import ConfigEditorDialog
from ..core.plugin_controller import PluginController
from .stylesheet import STYLESHEET

import os
import sys
import subprocess

class FCReportDock(QDockWidget):
    """
    Panneau latéral (dock) principal du plugin FC Report Helper.
    Gère l'interface utilisateur et les interactions.
    """
    def __init__(self, plugin, parent=None):
        """
        Initialise le dock du plugin.

        - Initialise l'UI
        - Connecte les boutons aux fonctions du contrôleur
        - Prépare le combo de sélection des types FC
        """
        super().__init__("[ABEI GIS] Report helper", parent)
        self.plugin = plugin
        self.controller = PluginController(self)

        self._init_ui()

        self.kml_btn.clicked.connect(self.controller.export_to_kml)
        self.cancel_btn.clicked.connect(self.reset_interface)
        self.ok_btn.clicked.connect(self.controller.generate_report)
        self.technology_combo.currentIndexChanged.connect(self.activate_selected_layer)
        
    def reset_interface(self):
        """
        Réinitialise l'interface à son état initial.
        - Vide la sélection
        - Désactive les boutons
        - Réinitialise les outils de sélection
        """
        self.technology_combo.setCurrentIndex(0)
        
        self.selected_object_label.clear()
        self.selected_object_label.setPlaceholderText("No analysis selected")

        self.ok_btn.setEnabled(False)
        self.kml_btn.setEnabled(False)

        if self.selection_tool:
            iface.mapCanvas().unsetMapTool(self.selection_tool)
            self.selection_tool = None
        
        self.selected_analysis = None
        self.update_status("Ready - Select a technology and click on an analysis")

    def _init_ui(self):
        """
        Initialise l'interface graphique du dock :
        - Styles
        - Boutons
        - Champs
        - En-tête
        """
        self.setObjectName("VmapDockWidget")
        self.setFeatures(QDockWidget.DockWidgetClosable |
                        QDockWidget.DockWidgetMovable |
                        QDockWidget.DockWidgetFloatable)

        self.setStyleSheet(STYLESHEET)

        self.main_widget = QWidget()
        self.setWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "icons", "icon.png")
        if os.path.exists(icon_path):
            logo = QLabel()
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio)
            logo.setPixmap(pixmap)
            header_layout.addWidget(logo)

        title = QLabel("Report Helper")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #212529;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Bouton Paramètres
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QgsApplication.getThemeIcon("mActionOptions.svg"))
        self.settings_btn.setToolTip("Open configuration file")
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.setStyleSheet("""
            border: none;
            background: transparent;
            padding: 0;
        }
        QPushButton:hover {
            background-color: #e0e0e0;  /* gris clair */
        }
        """)

        self.settings_btn.clicked.connect(self.open_config_file)
        header_layout.addWidget(self.settings_btn)

        self.layout.addWidget(header)


        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6;")
        self.layout.addWidget(separator)

        # Controls
        # Mode selector
        mode_layout = QHBoxLayout()
        mode_widget = QWidget() 
        mode_widget.setLayout(mode_layout)
        self.layout.addWidget(mode_widget, alignment=Qt.AlignCenter)
        self.radio_fc = QRadioButton("First Check")
        self.radio_dc = QRadioButton("Double Check")
        self.radio_fc.setChecked(True)  # FC par défaut
        # mode_layout.addWidget(QLabel("Select mode:"))
        mode_layout.addStretch()
        mode_layout.addWidget(self.radio_fc)
        mode_layout.addSpacing(20)  # Espace entre les boutons
        mode_layout.addWidget(self.radio_dc)
        mode_layout.addStretch()

        self.radio_fc.toggled.connect(lambda: self.switch_mode('FC'))
        self.radio_dc.toggled.connect(lambda: self.switch_mode('DC'))

        
        self.layout.addWidget(QLabel("1. Select the technology"))
        self.technology_combo = QComboBox()
        self.technology_combo.setToolTip("Select the technology of the analysis")
        self.layout.addWidget(self.technology_combo)

        self.layout.addWidget(QLabel("2. Click on the map to select an analysis"))
        self.selected_object_label = QLineEdit()
        self.selected_object_label.setPlaceholderText("No analysis selected")
        self.selected_object_label.setReadOnly(True)
        self.layout.addWidget(self.selected_object_label)

        self.button_layout = QHBoxLayout()
        self.kml_btn = QPushButton("Export KML")
        self.kml_btn.setIcon(QIcon.fromTheme("kml-export"))
        self.kml_btn.setEnabled(False)
        self.kml_btn.setToolTip("Export restrictions of the selected analysis to KML format")

        self.ok_btn = QPushButton("Generate Report")
        self.ok_btn.setIcon(QIcon.fromTheme("document-save"))
        self.ok_btn.setEnabled(False)
        self.ok_btn.setToolTip("Generate the Word restrictions report for the selected analysis")

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setIcon(QIcon.fromTheme("dialog-cancel"))
        self.cancel_btn.setToolTip("Reset the interface to initial state")

        self.button_layout.addWidget(self.kml_btn)
        self.button_layout.addWidget(self.ok_btn)
        self.button_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(self.button_layout)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        self.layout.addWidget(self.status_label)

        self.layout.addStretch()

        self.selection_tool = None
        self.selected_analysis = None
        self.init_technologys()

    def update_status(self, message, error=False):
        """
        Met à jour le message de statut affiché à l'utilisateur.

        :param message: Texte à afficher
        :param error: True pour afficher en rouge, sinon vert
        """
        color = "#dc3545" if error else "#28a745"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 11px;")
        self.status_label.setText(message)
        
    def switch_mode(self, mode):
        """
        Bascule entre les modes FC et DC et recharge les technologies disponibles.
        """
        Config.set_mode(mode)
        self.init_technologys()
        self.reset_interface()

    def init_technologys(self):
        """
        Charge les types de technologies (FC/DC) depuis la configuration,
        et les affiche dans le combo avec un choix par défaut.
        """
        self.technology_combo.clear()
        self.technology_combo.addItem("None", None)

        config_dict = Config.FC_CONFIG if Config.CURRENT_MODE == 'FC' else Config.DC_CONFIG
        for technology, config in config_dict.items():
            self.technology_combo.addItem(config['technology'], technology)

        self.technology_combo.setCurrentIndex(0)
        self.update_status("Ready - Select a technology and click on an analysis")


    def activate_selected_layer(self):
        current_index = self.technology_combo.currentIndex()
        if current_index == 0:
            self.reset_interface()
            return
            
        if self.selection_tool:
            iface.mapCanvas().unsetMapTool(self.selection_tool)

        technology = self.technology_combo.currentData()
        if not technology:
            return

        config = Config.get_config(technology)
        pattern = config['global_area_layer']
        
        QgsMessageLog.logMessage(f"Searching layer with pattern: {pattern}", "Debug")
        
        for layer in QgsProject.instance().mapLayers().values():
            if re.search(pattern, layer.name()):
                QgsMessageLog.logMessage(f"Found layer: {layer.name()}", "Debug")
                QgsMessageLog.logMessage(f"Fields: {[f.name() for f in layer.fields()]}", "Debug")
                iface.setActiveLayer(layer)
                self.setup_selection_tool(layer)
                break

    def setup_selection_tool(self, layer):
        """
        Configure l'outil de sélection d'entité sur la carte.
        """
        # Vérifie que les champs nécessaires existent
        id_field = Config.get_id_field()
        label_field = Config.get_label_field()
        
        if id_field not in layer.fields().names():
            self.update_status(f"Error: Field '{id_field}' not found in layer", error=True)
            return
            
        self.selection_tool = QgsMapToolIdentifyFeature(iface.mapCanvas())
        self.selection_tool.setLayer(layer)
        self.selection_tool.featureIdentified.connect(self.on_feature_selected)
        iface.mapCanvas().setMapTool(self.selection_tool)

        # Reset UI
        self.selected_object_label.clear()
        self.selected_object_label.setPlaceholderText("No analysis selected")
        self.ok_btn.setEnabled(False)
        self.kml_btn.setEnabled(False)
        self.selected_analysis = None

    def on_feature_selected(self, feature):
        try:
            self.selected_analysis = feature
            
            # Debug
            QgsMessageLog.logMessage(f"Selected feature fields: {feature.fields().names()}", "Debug")
            
            id_field = Config.get_id_field()
            label_field = Config.get_label_field()
            
            if id_field not in feature.fields().names():
                raise ValueError(f"ID field '{id_field}' not found in feature")
                
            feature_id = feature.attribute(id_field)
            if feature_id is None:
                raise ValueError("ID field is empty")
                
            label = feature.attribute(label_field) if label_field in feature.fields().names() else f"id_{feature_id}"
            
            self.selected_object_label.setText(f"ID: {feature_id} | Name: {label}")
            self.ok_btn.setEnabled(True)
            self.kml_btn.setEnabled(True)
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", error=True)
            QgsMessageLog.logMessage(f"Selection error: {str(e)}\nFields: {feature.fields().names() if 'feature' in locals() else 'No feature'}", 
                                "ABEI GIS", Qgis.Critical)

    def closeEvent(self, event):
        """
        Nettoyage lors de la fermeture du panneau.

        - Désactive l'outil de sélection s'il est actif
        """
        if self.selection_tool:
            iface.mapCanvas().unsetMapTool(self.selection_tool)
        super().closeEvent(event)
        

    def open_config_file(self):
        """Ouvre l'éditeur de configuration intégré"""
        try:
            editor = ConfigEditorDialog(self)
            editor.exec_()
            self.update_status("Configuration updated successfully")
        except Exception as e:
            error_msg = f"Error opening configuration editor: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "ABEI GIS", Qgis.Critical)
            self.update_status(error_msg, error=True)