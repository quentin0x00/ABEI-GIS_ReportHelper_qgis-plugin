from ..config import *

class ConfigEditorDialog(QDialog):
    """Boîte de dialogue pour éditer les constantes de configuration"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Editor")
        self.setMinimumSize(800, 600)

        self._init_ui()
        self._load_config_values()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Onglets pour organiser les différentes sections
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Onglet Général
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        general_tab.setLayout(general_layout)
        self.tab_widget.addTab(general_tab, "General")

        # Onglet FC
        fc_tab = QWidget()
        fc_layout = QVBoxLayout()
        fc_tab.setLayout(fc_layout)
        self.tab_widget.addTab(fc_tab, "First Check")

        # Onglet DC
        dc_tab = QWidget()
        dc_layout = QVBoxLayout()
        dc_tab.setLayout(dc_layout)
        self.tab_widget.addTab(dc_tab, "Double Check")

        # Création des champs pour chaque section
        self._create_general_fields(general_layout)
        self._create_fc_fields(fc_layout)
        self._create_dc_fields(dc_layout)

        # Hyperlien Teams (msteams protocol)
        teams_link = (
            "msteams:/l/chat/0/0"
            "?users=quentinrouquette@abeienergy.com"
            "&message=[QGIS-Plugin]"
        )
        teams_label = QLabel(
            f'Contact: <a href="{teams_link}">Quentin (Teams)</a>'
        )
        teams_label.setOpenExternalLinks(False)  # we'll handle it manually
        teams_label.linkActivated.connect(self._open_teams_link)
        teams_label.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(teams_label, alignment=Qt.AlignLeft)

        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_config)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)



    def _open_teams_link(self, link):
        try:
            os.startfile(link)
        except Exception as e:
            print(f"Erreur à l'ouverture de Teams : {e}")
            
    def _create_fc_fields(self, layout):
        """Crée les champs FC avec onglets et tableaux complets"""
        main_tab = QTabWidget()
        layout.addWidget(main_tab)

        # Onglet Paramètres de base
        base_tab = QWidget()
        base_layout = QFormLayout()
        base_tab.setLayout(base_layout)
        
        self.fc_word_title_edit = QLineEdit()
        base_layout.addRow("Word report - Title:", self.fc_word_title_edit)

        self.fc_id_field_edit = QLineEdit()
        base_layout.addRow("FC Area - ID Field:", self.fc_id_field_edit)
        
        self.fc_label_field_edit = QLineEdit()
        base_layout.addRow("FC Area - Label Field:", self.fc_label_field_edit)

        self.fc_restri_id_edit = QLineEdit()
        base_layout.addRow("Strict Restriction - ID Field:", self.fc_restri_id_edit)

        self.fc_type_restri_edit = QLineEdit()
        base_layout.addRow("Strict Restriction - Value:", self.fc_type_restri_edit)
        
        main_tab.addTab(base_tab, "General")

        # Onglet Configurations par technologie
        config_tab = QWidget()
        config_layout = QVBoxLayout()
        config_tab.setLayout(config_layout)
        
        tech_tabs = QTabWidget()
        config_layout.addWidget(tech_tabs)
        
        self.fc_config_edits = {}
        for tech_code, tech_config in Config.FC_CONFIG.items():
            tech_tab = QWidget()
            tech_layout = QFormLayout()
            tech_tab.setLayout(tech_layout)
            
            tech_edits = {}
            for field, value in tech_config.items():
                if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
                    combo = QComboBox()
                    self._populate_layer_combo(combo, value)
                    tech_layout.addRow(f"{field}:", combo)
                    tech_edits[field] = combo
            
            self.fc_config_edits[tech_code] = tech_edits
            tab_name = tech_config.get('technology', f'Tech {tech_code}')
            tech_tabs.addTab(tech_tab, tab_name)
        
        main_tab.addTab(config_tab, "Layers")

        # Onglet Thèmes
        themes_tab = QWidget()
        themes_layout = QVBoxLayout()
        themes_tab.setLayout(themes_layout)
        
        self.fc_theme_table = QTableWidget(len(Config.FC_FILTER_VALUES), 2)
        self.fc_theme_table.setHorizontalHeaderLabels(["Display Name", "Filter Value"])
        self.fc_theme_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fc_theme_table.verticalHeader().setVisible(False)
        
        # Adapter la hauteur du tableau
        row_count = len(Config.FC_FILTER_VALUES)
        self.fc_theme_table.setMinimumHeight(min(30 + row_count * 30, 600))  # 30px par ligne + marge
        
        themes_layout.addWidget(self.fc_theme_table)
        main_tab.addTab(themes_tab, "Themes")

    def _create_dc_fields(self, layout):
        """Crée les champs DC avec la même structure en onglets"""
        main_tab = QTabWidget()
        layout.addWidget(main_tab)

        # Onglet Paramètres de base
        base_tab = QWidget()
        base_layout = QFormLayout()
        base_tab.setLayout(base_layout)
        
        self.dc_word_title_edit = QLineEdit()
        base_layout.addRow("Word report - Title:", self.dc_word_title_edit)

        self.dc_id_field_edit = QLineEdit()
        base_layout.addRow("DC Area - ID Field:", self.dc_id_field_edit)
        
        self.dc_label_field_edit = QLineEdit()
        base_layout.addRow("DC Area - Label Field:", self.dc_label_field_edit)

        self.dc_restri_id_edit = QLineEdit()
        base_layout.addRow("Strict Restriction - ID Field:", self.dc_restri_id_edit)

        self.dc_type_restri_edit = QLineEdit()
        base_layout.addRow("Strict Restriction - Value:", self.dc_type_restri_edit)
        
        main_tab.addTab(base_tab, "General")

        # Onglet Configurations par technologie
        config_tab = QWidget()
        config_layout = QVBoxLayout()
        config_tab.setLayout(config_layout)
        
        tech_tabs = QTabWidget()
        config_layout.addWidget(tech_tabs)
        
        self.dc_config_edits = {}
        for tech_code, tech_config in Config.DC_CONFIG.items():
            tech_tab = QWidget()
            tech_layout = QFormLayout()
            tech_tab.setLayout(tech_layout)
            
            tech_edits = {}
            for field, value in tech_config.items():
                if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
                    combo = QComboBox()
                    self._populate_layer_combo(combo, value)
                    tech_layout.addRow(f"{field}:", combo)
                    tech_edits[field] = combo
            
            self.dc_config_edits[tech_code] = tech_edits
            tab_name = tech_config.get('technology', f'Tech {tech_code}')
            tech_tabs.addTab(tech_tab, tab_name)
        
        main_tab.addTab(config_tab, "Layers")

        # Onglet Thèmes
        themes_tab = QWidget()
        themes_layout = QVBoxLayout()
        themes_tab.setLayout(themes_layout)
        
        self.dc_theme_table = QTableWidget(len(Config.DC_FILTER_VALUES), 2)
        self.dc_theme_table.setHorizontalHeaderLabels(["Display Name", "Filter Value"])
        self.dc_theme_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dc_theme_table.verticalHeader().setVisible(False)
        
        # Adapter la hauteur du tableau
        row_count = len(Config.DC_FILTER_VALUES)
        self.dc_theme_table.setMinimumHeight(min(30 + row_count * 30, 600))  # 30px par ligne + marge
        
        themes_layout.addWidget(self.dc_theme_table)
        main_tab.addTab(themes_tab, "Themes")
        
    def _create_general_fields(self, layout):
        """Crée les champs pour les constantes générales avec menu déroulant pour le basemap"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        form_layout = QFormLayout()
        container_layout.addLayout(form_layout)

        self.footer_text_edit = QLineEdit()
        form_layout.addRow("Word report - Footer Text:", self.footer_text_edit)

        # Menu déroulant pour le basemap
        self.basemap_combo = QComboBox()
        self._populate_layer_combo(self.basemap_combo, Config.BASEMAP)
        form_layout.addRow("Word report - Basemap:", self.basemap_combo)

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def _load_config_values(self):
        """Charge les valeurs actuelles dans les champs"""
        self.footer_text_edit.setText(Config.FOOTER_MIDDLE_TEXT)
        index = self.basemap_combo.findText(Config.BASEMAP)
        if index >= 0:
            self.basemap_combo.setCurrentIndex(index)

        # FC
        self.fc_word_title_edit.setText(Config.FC_WORD_TITLE_TEXT)
        self.fc_id_field_edit.setText(Config.FC_ID_FIELD)
        self.fc_restri_id_edit.setText(Config.FC_RESTRI_ID)
        self.fc_label_field_edit.setText(Config.FC_LABEL_FIELD)
        self.fc_type_restri_edit.setText(Config.FC_TYPE_RESTRI_STRICT)

        # DC
        self.dc_word_title_edit.setText(Config.DC_WORD_TITLE_TEXT)
        self.dc_id_field_edit.setText(Config.DC_ID_FIELD)
        self.dc_restri_id_edit.setText(Config.DC_RESTRI_ID)
        self.dc_label_field_edit.setText(Config.DC_LABEL_FIELD)
        self.dc_type_restri_edit.setText(Config.DC_TYPE_RESTRI_STRICT)

        # Charger les thèmes FC
        self.fc_theme_table.setRowCount(len(Config.FC_FILTER_VALUES))
        for row, (display_name, filter_value) in enumerate(Config.FC_FILTER_VALUES.items()):
            self.fc_theme_table.setItem(row, 0, QTableWidgetItem(display_name))
            self.fc_theme_table.setItem(row, 1, QTableWidgetItem(filter_value))

        # Charger les thèmes DC
        self.dc_theme_table.setRowCount(len(Config.DC_FILTER_VALUES))
        for row, (display_name, filter_value) in enumerate(Config.DC_FILTER_VALUES.items()):
            self.dc_theme_table.setItem(row, 0, QTableWidgetItem(display_name))
            self.dc_theme_table.setItem(row, 1, QTableWidgetItem(filter_value))

    def _populate_layer_combo(self, combo_box, default_value=None):
        """Remplit un QComboBox avec les noms des couches du projet et sélectionne la valeur par défaut"""
        combo_box.clear()

        # Ajouter une entrée vide optionnelle
        combo_box.addItem("", None)

        # Récupérer toutes les couches du projet
        layers = QgsProject.instance().mapLayers().values()
        layer_names = [layer.name() for layer in layers]

        # Trier les noms par ordre alphabétique
        layer_names.sort()

        # Ajouter les noms au combo box
        for name in layer_names:
            combo_box.addItem(name, name)

        # Sélectionner la valeur par défaut si elle existe
        if default_value:
            index = combo_box.findText(default_value)
            if index >= 0:
                combo_box.setCurrentIndex(index)
            else:
                # Si la couche n'existe pas, l'ajouter comme élément spécial
                combo_box.addItem(f"{default_value} (non trouvé)", default_value)
                combo_box.setCurrentIndex(combo_box.count() - 1)

    def _save_config(self):
        """Sauvegarde les modifications dans le fichier de configuration"""
        try:
            # Constantes générales
            Config.FOOTER_MIDDLE_TEXT = self.footer_text_edit.text()
            Config.BASEMAP = self.basemap_combo.currentData() or self.basemap_combo.currentText()

            # FC
            Config.FC_WORD_TITLE_TEXT = self.fc_word_title_edit.text()
            Config.FC_ID_FIELD = self.fc_id_field_edit.text()
            Config.FC_RESTRI_ID = self.fc_restri_id_edit.text()
            Config.FC_LABEL_FIELD = self.fc_label_field_edit.text()
            Config.FC_TYPE_RESTRI_STRICT = self.fc_type_restri_edit.text()

            # DC
            Config.DC_WORD_TITLE_TEXT = self.dc_word_title_edit.text()
            Config.DC_ID_FIELD = self.dc_id_field_edit.text()
            Config.DC_RESTRI_ID = self.dc_restri_id_edit.text()
            Config.DC_LABEL_FIELD = self.dc_label_field_edit.text()
            Config.DC_TYPE_RESTRI_STRICT = self.dc_type_restri_edit.text()

            # Thèmes FC
            Config.FC_FILTER_VALUES.clear()
            for row in range(self.fc_theme_table.rowCount()):
                display_name = self.fc_theme_table.item(row, 0).text()
                filter_value = self.fc_theme_table.item(row, 1).text()
                Config.FC_FILTER_VALUES[display_name] = filter_value

            # Thèmes DC
            Config.DC_FILTER_VALUES.clear()
            for row in range(self.dc_theme_table.rowCount()):
                display_name = self.dc_theme_table.item(row, 0).text()
                filter_value = self.dc_theme_table.item(row, 1).text()
                Config.DC_FILTER_VALUES[display_name] = filter_value

            # Config FC
            for tech, edits in self.fc_config_edits.items():
                for field, widget in edits.items():
                    Config.FC_CONFIG[tech][field] = widget.currentData() or widget.currentText()

            # Config DC
            for tech, edits in self.dc_config_edits.items():
                for field, widget in edits.items():
                    Config.DC_CONFIG[tech][field] = widget.currentData() or widget.currentText()

            QMessageBox.information(self, "Success", "Configuration updated successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
