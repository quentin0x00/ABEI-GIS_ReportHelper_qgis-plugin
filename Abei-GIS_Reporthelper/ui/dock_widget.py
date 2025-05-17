from ..imports import *
from ..config import Config
from ..core.plugin_controller import PluginController

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
        self.fc_type_combo.currentIndexChanged.connect(self.activate_selected_layer)
        
    def reset_interface(self):
        """
        Réinitialise l'interface à son état initial.
        - Vide la sélection
        - Désactive les boutons
        - Réinitialise les outils de sélection
        """
        self.fc_type_combo.setCurrentIndex(0)
        
        self.selected_object_label.clear()
        self.selected_object_label.setPlaceholderText("No analysis selected")

        self.ok_btn.setEnabled(False)
        self.kml_btn.setEnabled(False)

        if self.selection_tool:
            iface.mapCanvas().unsetMapTool(self.selection_tool)
            self.selection_tool = None
        
        self.selected_feature = None
        self.update_status("Ready - Select a technology and click on an analysis")

    def _init_ui(self):
        """
        Initialise l'interface graphique du dock :
        - Styles
        - Boutons
        - Champs
        - En-tête
        """
        self.setObjectName("FCReportDockWidget")
        self.setFeatures(QDockWidget.DockWidgetClosable |
                        QDockWidget.DockWidgetMovable |
                        QDockWidget.DockWidgetFloatable)

        self.setStyleSheet("""
            QDockWidget {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                titlebar-close-icon: url(:/icons/close.svg);
                titlebar-normal-icon: url(:/icons/dock.svg);
                font-family: Segoe UI, Arial;
            }
            QDockWidget::title {
                color: black;
                padding: 4px;
                text-align: center;
                font-weight: bold;
            }
            QWidget {
                background: white;
            }
            QLabel {
                color: #495057;
                font-size: 12px;
                margin-top: 8px;
            }
            QComboBox {
                background: white;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 3px;
                min-height: 24px;
                color: #212529;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox:on {  /* When the combo box is open */
                color: #212529;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #212529;
                selection-background-color: #0d6efd;
                selection-color: white;
                outline: 0;  /* Remove focus border */
            }
            QLineEdit {
                background: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                color: #212529;
            }
            QPushButton {
                background: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0b5ed7;
            }
            QPushButton:disabled {
                background: #6c757d;
            }
        """)

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

        title = QLabel("Report Helper - First Check")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #212529;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.layout.addWidget(header)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6;")
        self.layout.addWidget(separator)

        # Controls
        self.layout.addWidget(QLabel("1. Select the technology:"))
        self.fc_type_combo = QComboBox()
        self.fc_type_combo.setToolTip("Select the technology of the analysis")
        self.layout.addWidget(self.fc_type_combo)

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
        self.selected_feature = None
        self.init_fc_types()

    def update_status(self, message, error=False):
        """
        Met à jour le message de statut affiché à l'utilisateur.

        :param message: Texte à afficher
        :param error: True pour afficher en rouge, sinon vert
        """
        color = "#dc3545" if error else "#28a745"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 11px;")
        self.status_label.setText(message)

    def init_fc_types(self):
        """
        Charge les types de technologies FC depuis la configuration,
        et les affiche dans le combo avec un choix par défaut.
        """
        self.fc_type_combo.clear()
        self.fc_type_combo.addItem("None", None)
        
        
        
        for fc_type, config in Config.FC_CONFIG.items():
            self.fc_type_combo.addItem(config['name'], fc_type)
        self.fc_type_combo.setCurrentIndex(0)
        self.update_status("Ready - Select a technology and click on an analysis")


    def activate_selected_layer(self):
        """
        Active la couche correspondant au type FC sélectionné.

        - Vérifie la sélection
        - Active la couche avec le motif défini
        - Active l'outil de sélection
        """
        current_index = self.fc_type_combo.currentIndex()
        
        if current_index == 0:
            self.reset_interface()
            return
            
        if self.selection_tool:
            iface.mapCanvas().unsetMapTool(self.selection_tool)

        fc_type = self.fc_type_combo.currentData()
        if fc_type is None:
            return

        pattern = Config.FC_CONFIG[fc_type]['area_layer_pattern']
        for layer in QgsProject.instance().mapLayers().values():
            if re.search(pattern, layer.name()):
                iface.setActiveLayer(layer)
                self.setup_selection_tool(layer)
                self.update_status(f"Ready - Click on an analysis to select it")
                break

    def setup_selection_tool(self, layer):
        """
        Configure l'outil de sélection d'entité sur la carte.

        - Associe l'outil à la couche sélectionnée
        - Réinitialise l'affichage
        """
        self.selection_tool = QgsMapToolIdentifyFeature(iface.mapCanvas())
        self.selection_tool.setLayer(layer)
        self.selection_tool.featureIdentified.connect(self.on_feature_selected)
        iface.mapCanvas().setMapTool(self.selection_tool)

        self.selected_object_label.clear()
        self.selected_object_label.setPlaceholderText("No analysis selected")

        self.ok_btn.setEnabled(False)
        self.kml_btn.setEnabled(False)

        self.selected_feature = None

    def on_feature_selected(self, feature):
        """
        Réagit à la sélection d'une entité sur la carte.

        - Vérifie l'identifiant de l'entité
        - Active les boutons d'action
        - Affiche les infos de l'entité sélectionnée
        """
        try:
            self.selected_feature = feature

            if 'id' not in feature.fields().names():
                raise ValueError("Object has no 'id' field")
            feature_id = feature.attribute('id')
            if feature_id is None:
                raise ValueError("ID field is empty")
            label = feature.attribute('label') if 'label' in feature.fields().names() else f"FC_{feature_id}"
            self.selected_object_label.setText(f"ID: {feature_id} | Label: {label}")

            self.ok_btn.setEnabled(True)
            self.kml_btn.setEnabled(True)

            self.update_status(f"Analysis selected - Ready to generate report or export KML")

        except Exception as e:
            self.update_status(f"Error: {str(e)}", error=True)
            self.selected_object_label.setText(f"Error: {str(e)}")
            QgsMessageLog.logMessage(f"Feature selection error: {str(e)}", "FC Report", Qgis.Critical)

    def closeEvent(self, event):
        """
        Nettoyage lors de la fermeture du panneau.

        - Désactive l'outil de sélection s'il est actif
        """
        if self.selection_tool:
            iface.mapCanvas().unsetMapTool(self.selection_tool)
        super().closeEvent(event)
