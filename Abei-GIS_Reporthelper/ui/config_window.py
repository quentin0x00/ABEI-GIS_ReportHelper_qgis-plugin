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
            
        # Onglets principaux reorganisés
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Onglet 1: Word Report (le plus important pour les utilisateurs)
        word_report_tab = QWidget()
        word_report_layout = QVBoxLayout()
        word_report_tab.setLayout(word_report_layout)
        self.tab_widget.addTab(word_report_tab, "Word Report")

        # Onglet 2: Layers (le deuxième plus important)
        layers_tab = QWidget()
        layers_layout = QVBoxLayout()
        layers_tab.setLayout(layers_layout)
        self.tab_widget.addTab(layers_tab, "Layers")

        # Onglet 3: Settings (moins fréquemment utilisé)
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)
        self.tab_widget.addTab(settings_tab, "Settings")

        # Création du contenu pour chaque onglet
        self._create_word_report_fields(word_report_layout)
        self._create_layers_fields(layers_layout)
        self._create_settings_fields(settings_layout)

        # Hyperlien Teams (msteams protocol)
        teams_link = (
            "msteams:/l/chat/0/0"
            "?users=quentinrouquette@abeienergy.com"
            "&message=HELP!!😰"
        )
        teams_label = QLabel(
            f'Contact: <a href="{teams_link}">Quentin (Teams)</a>'
        )
        teams_label.setOpenExternalLinks(False)  # we'll handle it manually
        teams_label.linkActivated.connect(self._open_teams_link)
        teams_label.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(teams_label, alignment=Qt.AlignLeft)

        # Boutons en bas (annuler/enregistrer)
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_config)
        button_box.rejected.connect(self.reject)

        # Créer le bouton load JSON (comme votre settings_btn)
        load_json_container = QWidget()
        load_json_layout = QHBoxLayout()
        load_json_container.setLayout(load_json_layout)
        load_json_layout.setContentsMargins(0, 0, 0, 0)  # Supprimer les marges

        # Ajouter le texte à gauche
        load_json_label = QLabel("Load JSON:")
        load_json_layout.addWidget(load_json_label)

        # Garder votre bouton existant (inchangé)
        self.load_json_btn = QPushButton()
        self.load_json_btn.setIcon(QgsApplication.getThemeIcon("/processingResult.svg"))
        self.load_json_btn.setToolTip("Load JSON configuration")
        self.load_json_btn.setFixedSize(28, 28)
        self.load_json_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.load_json_btn.clicked.connect(self._load_json_file)
        load_json_layout.addWidget(self.load_json_btn)
        
        # Layout pour les boutons en bas
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(load_json_container)    # Icône à gauche
        bottom_layout.addStretch()  # Espace entre les boutons
        bottom_layout.addWidget(button_box)  # Boutons standard à droite

        # Ajouter le layout de boutons au layout principal
        layout.addLayout(bottom_layout)
        
    def _create_word_report_fields(self, layout):
        """Onglet Word Report - Contient tout ce qui concerne les rapports Word"""
        
        # Créer un conteneur vertical pour les éléments généraux + onglets
        container = QVBoxLayout()
        
        # Ajouter les éléments généraux en premier
        general_form = QFormLayout()
        self.basemap_combo = QComboBox()
        self._populate_layer_combo(self.basemap_combo, Config.BASEMAP)
        general_form.addRow("Basemap:", self.basemap_combo)
        
        self.footer_text_edit = QLineEdit()
        general_form.addRow("Footer Text:", self.footer_text_edit)
        general_form.addRow(QLabel(""))
        container.addLayout(general_form)
        
        # Sous-onglets pour FC et DC (inchangé)
        word_tabs = QTabWidget()
        container.addWidget(word_tabs)

        # Onglet FC Word Report (inchangé)
        fc_word_tab = QWidget()
        fc_word_layout = QVBoxLayout()
        fc_word_tab.setLayout(fc_word_layout)
        word_tabs.addTab(fc_word_tab, "First Check")

        # Paramètres FC Word Report (inchangé)
        fc_form = QFormLayout()
        self.fc_word_title_edit = QLineEdit()
        fc_form.addRow("Title:", self.fc_word_title_edit)
        fc_word_layout.addLayout(fc_form)

        # Onglet DC Word Report (inchangé)
        dc_word_tab = QWidget()
        dc_word_layout = QVBoxLayout()
        dc_word_tab.setLayout(dc_word_layout)
        word_tabs.addTab(dc_word_tab, "Double Check")

        # Paramètres DC Word Report (inchangé)
        dc_form = QFormLayout()
        self.dc_word_title_edit = QLineEdit()
        dc_form.addRow("Title:", self.dc_word_title_edit)
        dc_word_layout.addLayout(dc_form)
        
        # Ajouter le conteneur au layout principal
        layout.addLayout(container)

    def _create_layers_fields(self, layout):
        """Onglet Layers - Contient toutes les configurations de couches par technologie"""
        # Sous-onglets pour FC et DC
        layers_tabs = QTabWidget()
        layout.addWidget(layers_tabs)

        # Onglet FC Layers
        fc_layers_tab = QWidget()
        fc_layers_layout = QVBoxLayout()
        fc_layers_tab.setLayout(fc_layers_layout)
        layers_tabs.addTab(fc_layers_tab, "First Check Layers")

        # Configurations FC par technologie
        fc_tech_tabs = QTabWidget()
        fc_layers_layout.addWidget(fc_tech_tabs)
        
        self.fc_config_edits = {}
        for tech_code, tech_config in Config.FC_CONFIG.items():
            tech_tab = QWidget()
            tech_layout = QFormLayout()
            tech_tab.setLayout(tech_layout)
            
            tech_edits = {}
            for field, value in tech_config.items():
                if field in ['global_area_layer', 'feasible_layer', 'conditional_layer', 'restriction_layer']:
                    combo = QComboBox()
                    self._populate_layer_combo(combo, value)
                    tech_layout.addRow(f"{field}:", combo)
                    tech_edits[field] = combo
            
            self.fc_config_edits[tech_code] = tech_edits
            tab_name = tech_config.get('technology', f'Tech {tech_code}')
            fc_tech_tabs.addTab(tech_tab, tab_name)

        # Onglet DC Layers
        dc_layers_tab = QWidget()
        dc_layers_layout = QVBoxLayout()
        dc_layers_tab.setLayout(dc_layers_layout)
        layers_tabs.addTab(dc_layers_tab, "Double Check Layers")

        # Configurations DC par technologie
        dc_tech_tabs = QTabWidget()
        dc_layers_layout.addWidget(dc_tech_tabs)
        
        self.dc_config_edits = {}
        for tech_code, tech_config in Config.DC_CONFIG.items():
            tech_tab = QWidget()
            tech_layout = QFormLayout()
            tech_tab.setLayout(tech_layout)
            
            tech_edits = {}
            for field, value in tech_config.items():
                if field in ['global_area_layer', 'feasible_layer', 'conditional_layer', 'restriction_layer']:
                    combo = QComboBox()
                    self._populate_layer_combo(combo, value)
                    tech_layout.addRow(f"{field}:", combo)
                    tech_edits[field] = combo
            
            self.dc_config_edits[tech_code] = tech_edits
            tab_name = tech_config.get('technology', f'Tech {tech_code}')
            dc_tech_tabs.addTab(tech_tab, tab_name)

    def _create_settings_fields(self, layout):
        """Onglet Settings - Contient les paramètres moins fréquemment modifiés"""
        # Sous-onglets pour FC et DC
        settings_tabs = QTabWidget()
        layout.addWidget(settings_tabs)

        # Onglet FC Settings
        fc_settings_tab = QWidget()
        fc_settings_scroll = QScrollArea()
        fc_settings_scroll.setWidgetResizable(True)
        fc_settings_container = QWidget()
        fc_settings_layout = QFormLayout()
        fc_settings_container.setLayout(fc_settings_layout)
        fc_settings_scroll.setWidget(fc_settings_container)
        
        fc_settings_tab_layout = QVBoxLayout()
        fc_settings_tab_layout.addWidget(fc_settings_scroll)
        fc_settings_tab.setLayout(fc_settings_tab_layout)
        settings_tabs.addTab(fc_settings_tab, "First Check Settings")

        # Paramètres FC avancés
        self.fc_id_field_edit = QLineEdit()
        fc_settings_layout.addRow("FC Area - ID Field:", self.fc_id_field_edit)
        
        self.fc_label_field_edit = QLineEdit()
        fc_settings_layout.addRow("FC Area - Label Field:", self.fc_label_field_edit)
        
        self.fc_restri_id_edit = QLineEdit()
        fc_settings_layout.addRow("Strict Restriction - ID Field:", self.fc_restri_id_edit)
        
        self.fc_type_restri_edit = QLineEdit()
        fc_settings_layout.addRow("Strict Restriction - Value:", self.fc_type_restri_edit)

        # Thèmes FC dans Settings
        fc_settings_layout.addRow(QLabel(""))  # Espacement
        fc_settings_layout.addRow(QLabel("Themes:"))
        
        self.fc_theme_table = QTableWidget(len(Config.FC_FILTER_VALUES), 2)
        self.fc_theme_table.setHorizontalHeaderLabels(["Display Name", "Filter Value"])
        self.fc_theme_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fc_theme_table.verticalHeader().setVisible(False)
        
        # Adapter la hauteur du tableau pour qu'il soit scrollable
        row_count = len(Config.FC_FILTER_VALUES)
        self.fc_theme_table.setMinimumHeight(200)  # Hauteur fixe plus petite
        self.fc_theme_table.setMaximumHeight(300)  # Hauteur maximale pour permettre le scroll
        
        fc_settings_layout.addRow(self.fc_theme_table)

        # Onglet DC Settings
        dc_settings_tab = QWidget()
        dc_settings_scroll = QScrollArea()
        dc_settings_scroll.setWidgetResizable(True)
        dc_settings_container = QWidget()
        dc_settings_layout = QFormLayout()
        dc_settings_container.setLayout(dc_settings_layout)
        dc_settings_scroll.setWidget(dc_settings_container)
        
        dc_settings_tab_layout = QVBoxLayout()
        dc_settings_tab_layout.addWidget(dc_settings_scroll)
        dc_settings_tab.setLayout(dc_settings_tab_layout)
        settings_tabs.addTab(dc_settings_tab, "Double Check Settings")

        # Paramètres DC avancés
        self.dc_id_field_edit = QLineEdit()
        dc_settings_layout.addRow("DC Area - ID Field:", self.dc_id_field_edit)
        
        self.dc_label_field_edit = QLineEdit()
        dc_settings_layout.addRow("DC Area - Label Field:", self.dc_label_field_edit)
        
        self.dc_restri_id_edit = QLineEdit()
        dc_settings_layout.addRow("Strict Restriction - ID Field:", self.dc_restri_id_edit)
        
        self.dc_type_restri_edit = QLineEdit()
        dc_settings_layout.addRow("Strict Restriction - Value:", self.dc_type_restri_edit)

        # Thèmes DC dans Settings
        dc_settings_layout.addRow(QLabel(""))  # Espacement
        dc_settings_layout.addRow(QLabel("Themes:"))
        
        self.dc_theme_table = QTableWidget(len(Config.DC_FILTER_VALUES), 2)
        self.dc_theme_table.setHorizontalHeaderLabels(["Display Name", "Filter Value"])
        self.dc_theme_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dc_theme_table.verticalHeader().setVisible(False)
        
        # Adapter la hauteur du tableau pour qu'il soit scrollable
        row_count = len(Config.DC_FILTER_VALUES)
        self.dc_theme_table.setMinimumHeight(200)  # Hauteur fixe plus petite
        self.dc_theme_table.setMaximumHeight(300)  # Hauteur maximale pour permettre le scroll
        
        dc_settings_layout.addRow(self.dc_theme_table)

    def _load_json_file(self):
        """Charge un fichier JSON et remplace complètement la config"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select JSON Configuration", 
            "", 
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # 1. Lire le nouveau fichier JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)
            
            # 2. Écraser param.json
            with open(Config._config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2)
            
            # 3. Recharger la config
            Config._load_config()
            
            # 4. Rafraîchir l'UI
            self._load_config_values()
            
            QMessageBox.information(self, "Success", "Configuration loaded and applied!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config: {str(e)}")

    def _open_teams_link(self, link):
        try:
            os.startfile(link)
        except Exception as e:
            print(f"Erreur à l'ouverture de Teams : {e}")

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
        """Sauvegarde les modifications dans le fichier JSON et recharge la config"""
        try:
            # 1. Charger la config existante
            with open(Config._config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Mettre à jour les valeurs
            # Global
            config_data['global']['FOOTER_MIDDLE_TEXT'] = self.footer_text_edit.text()
            config_data['global']['BASEMAP'] = self.basemap_combo.currentData() or self.basemap_combo.currentText()
            
            # FC
            config_data['FC']['FC_WORD_TITLE_TEXT'] = self.fc_word_title_edit.text()
            config_data['FC']['FC_ID_FIELD'] = self.fc_id_field_edit.text()
            config_data['FC']['FC_RESTRI_ID'] = self.fc_restri_id_edit.text()
            config_data['FC']['FC_LABEL_FIELD'] = self.fc_label_field_edit.text()
            config_data['FC']['FC_TYPE_RESTRI_STRICT'] = self.fc_type_restri_edit.text()
            
            # DC
            config_data['DC']['DC_WORD_TITLE_TEXT'] = self.dc_word_title_edit.text()
            config_data['DC']['DC_ID_FIELD'] = self.dc_id_field_edit.text()
            config_data['DC']['DC_RESTRI_ID'] = self.dc_restri_id_edit.text()
            config_data['DC']['DC_LABEL_FIELD'] = self.dc_label_field_edit.text()
            config_data['DC']['DC_TYPE_RESTRI_STRICT'] = self.dc_type_restri_edit.text()
            
            # Thèmes FC
            config_data['FC']['FC_FILTER_VALUES'] = {}
            for row in range(self.fc_theme_table.rowCount()):
                display_name = self.fc_theme_table.item(row, 0).text()
                filter_value = self.fc_theme_table.item(row, 1).text()
                config_data['FC']['FC_FILTER_VALUES'][display_name] = filter_value
            
            # Thèmes DC
            config_data['DC']['DC_FILTER_VALUES'] = {}
            for row in range(self.dc_theme_table.rowCount()):
                display_name = self.dc_theme_table.item(row, 0).text()
                filter_value = self.dc_theme_table.item(row, 1).text()
                config_data['DC']['DC_FILTER_VALUES'][display_name] = filter_value
            
            # Config FC
            for tech, edits in self.fc_config_edits.items():
                for field, widget in edits.items():
                    config_data['FC']['FC_CONFIG'][tech][field] = widget.currentData() or widget.currentText()
            
            # Config DC
            for tech, edits in self.dc_config_edits.items():
                for field, widget in edits.items():
                    config_data['DC']['DC_CONFIG'][tech][field] = widget.currentData() or widget.currentText()
            
            with open(Config._config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            Config._load_config()
            
            QMessageBox.information(self, "Success", "Configuration saved")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving config: {str(e)}")