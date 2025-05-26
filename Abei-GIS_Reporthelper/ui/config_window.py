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

        # Label "quentin" qui renvoie un mail
        mail_label = QLabel('contact: <a href="mailto:quentinrouquette@abeienergy.com">Quentin Rouquette</a>')
        mail_label.setOpenExternalLinks(True)
        layout.addWidget(mail_label, alignment=Qt.AlignLeft)

        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_config)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _create_fc_fields(self, layout):
        """Crée les champs pour les constantes FC"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        form_layout = QFormLayout()
        container_layout.addLayout(form_layout)

        self.fc_word_title_edit = QLineEdit()
        form_layout.addRow("Word Title:", self.fc_word_title_edit)

        self.fc_id_field_edit = QLineEdit()
        form_layout.addRow("ID Field:", self.fc_id_field_edit)

        self.fc_restri_id_edit = QLineEdit()
        form_layout.addRow("Restriction ID:", self.fc_restri_id_edit)

        self.fc_label_field_edit = QLineEdit()
        form_layout.addRow("Label Field:", self.fc_label_field_edit)

        self.fc_type_restri_edit = QLineEdit()
        form_layout.addRow("Type Restriction Strict:", self.fc_type_restri_edit)

        # Ajouter les thèmes FC
        fc_themes_group = QGroupBox("FC Themes")
        fc_themes_layout = QFormLayout()
        fc_themes_group.setLayout(fc_themes_layout)
        container_layout.addWidget(fc_themes_group)

        self.fc_theme_edits = {}
        for key, value in Config.FC_THEMES_DICT.items():
            edit = QLineEdit()
            edit.setText(value)
            fc_themes_layout.addRow(f"Theme {key}:", edit)
            self.fc_theme_edits[key] = edit

        # Ajouter les configurations FC
        fc_config_group = QGroupBox("FC Configurations")
        fc_config_layout = QVBoxLayout()
        fc_config_group.setLayout(fc_config_layout)
        container_layout.addWidget(fc_config_group)

        self.fc_config_edits = {}
        for tech_code, tech_config in Config.FC_CONFIG.items():
            group = QGroupBox(tech_config.get('technology', f'Tech {tech_code}'))
            group_layout = QFormLayout()
            group.setLayout(group_layout)
            fc_config_layout.addWidget(group)

            tech_edits = {}
            for field, value in tech_config.items():
                if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
                    # Menu déroulant pour les couches
                    combo = QComboBox()
                    self._populate_layer_combo(combo, value)
                    group_layout.addRow(f"{field}:", combo)
                    tech_edits[field] = combo
                else:
                    # Champ texte normal pour les autres champs
                    edit = QLineEdit()
                    if isinstance(value, type(QVariant.Int)):
                        edit.setText('QVariant.Int')
                    else:
                        edit.setText(str(value))
                    group_layout.addRow(f"{field}:", edit)
                    tech_edits[field] = edit
            self.fc_config_edits[tech_code] = tech_edits

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def _create_dc_fields(self, layout):
        """Crée les champs pour les constantes DC"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        form_layout = QFormLayout()
        container_layout.addLayout(form_layout)

        self.dc_word_title_edit = QLineEdit()
        form_layout.addRow("Word Title:", self.dc_word_title_edit)

        self.dc_id_field_edit = QLineEdit()
        form_layout.addRow("ID Field:", self.dc_id_field_edit)

        self.dc_restri_id_edit = QLineEdit()
        form_layout.addRow("Restriction ID:", self.dc_restri_id_edit)

        self.dc_label_field_edit = QLineEdit()
        form_layout.addRow("Label Field:", self.dc_label_field_edit)

        self.dc_type_restri_edit = QLineEdit()
        form_layout.addRow("Type Restriction Strict:", self.dc_type_restri_edit)

        # Ajouter les thèmes DC
        dc_themes_group = QGroupBox("DC Themes")
        dc_themes_layout = QFormLayout()
        dc_themes_group.setLayout(dc_themes_layout)
        container_layout.addWidget(dc_themes_group)

        self.dc_theme_edits = {}
        for key, value in Config.DC_THEMES_DICT.items():
            edit = QLineEdit()
            edit.setText(value)
            dc_themes_layout.addRow(f"Theme {key}:", edit)
            self.dc_theme_edits[key] = edit

        # Ajouter les configurations DC
        dc_config_group = QGroupBox("DC Configurations")
        dc_config_layout = QVBoxLayout()
        dc_config_group.setLayout(dc_config_layout)
        container_layout.addWidget(dc_config_group)

        self.dc_config_edits = {}
        for tech_code, tech_config in Config.DC_CONFIG.items():
            group = QGroupBox(tech_config.get('technology', f'Tech {tech_code}'))
            group_layout = QFormLayout()
            group.setLayout(group_layout)
            dc_config_layout.addWidget(group)

            tech_edits = {}
            for field, value in tech_config.items():
                if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
                    # Menu déroulant pour les couches
                    combo = QComboBox()
                    self._populate_layer_combo(combo, value)
                    group_layout.addRow(f"{field}:", combo)
                    tech_edits[field] = combo
                else:
                    # Champ texte normal pour les autres champs
                    edit = QLineEdit()
                    if isinstance(value, type(QVariant.Int)):
                        edit.setText('QVariant.Int')
                    else:
                        edit.setText(str(value))
                    group_layout.addRow(f"{field}:", edit)
                    tech_edits[field] = edit
            self.dc_config_edits[tech_code] = tech_edits

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def _create_general_fields(self, layout):
        """Crée les champs pour les constantes générales avec menu déroulant pour le basemap"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        form_layout = QFormLayout()
        container_layout.addLayout(form_layout)

        self.plugin_name_edit = QLineEdit()
        form_layout.addRow("Plugin Name:", self.plugin_name_edit)

        self.footer_text_edit = QLineEdit()
        form_layout.addRow("Footer Text:", self.footer_text_edit)

        # Menu déroulant pour le basemap
        self.basemap_combo = QComboBox()
        self._populate_layer_combo(self.basemap_combo, Config.BASEMAP)
        form_layout.addRow("Basemap:", self.basemap_combo)

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def _load_config_values(self):
        """Charge les valeurs actuelles dans les champs"""
        self.plugin_name_edit.setText(Config.PLUGIN_NAME)
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
        for key, edit in self.fc_theme_edits.items():
            edit.setText(Config.FC_THEMES_DICT.get(key, ""))

        # Charger les thèmes DC
        for key, edit in self.dc_theme_edits.items():
            edit.setText(Config.DC_THEMES_DICT.get(key, ""))

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
            Config.PLUGIN_NAME = self.plugin_name_edit.text()
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
            for key, edit in self.fc_theme_edits.items():
                Config.FC_THEMES_DICT[key] = edit.text()

            # Thèmes DC
            for key, edit in self.dc_theme_edits.items():
                Config.DC_THEMES_DICT[key] = edit.text()

            # Config FC
            for tech, edits in self.fc_config_edits.items():
                for field, widget in edits.items():
                    if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
                        Config.FC_CONFIG[tech][field] = widget.currentData() or widget.currentText()
                    else:
                        value = widget.text()
                        if field == 'restri_join_id_field':
                            Config.FC_CONFIG[tech][field] = QVariant.Int if value == 'QVariant.Int' else value
                        else:
                            Config.FC_CONFIG[tech][field] = value

            # Config DC
            for tech, edits in self.dc_config_edits.items():
                for field, widget in edits.items():
                    if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
                        Config.DC_CONFIG[tech][field] = widget.currentData() or widget.currentText()
                    else:
                        value = widget.text()
                        if field == 'restri_join_id_field':
                            Config.DC_CONFIG[tech][field] = QVariant.Int if value == 'QVariant.Int' else value
                        else:
                            Config.DC_CONFIG[tech][field] = value

            QMessageBox.information(self, "Success", "Configuration updated successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")

# from ..config import *

# class ConfigEditorDialog(QDialog):
#     """Boîte de dialogue pour éditer les constantes de configuration"""
    
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Configuration Editor")
#         self.setMinimumSize(600, 500)
        
#         self._init_ui()
#         self._load_config_values()
        
#     def _init_ui(self):
#         layout = QVBoxLayout()
#         self.setLayout(layout)
        
#         # Onglets pour organiser les différentes sections
#         self.tab_widget = QTabWidget()
#         layout.addWidget(self.tab_widget)
        
#         # Onglet Général
#         general_tab = QWidget()
#         general_layout = QVBoxLayout()
#         general_tab.setLayout(general_layout)
#         self.tab_widget.addTab(general_tab, "General")
        
#         # Onglet FC
#         fc_tab = QWidget()
#         fc_layout = QVBoxLayout()
#         fc_tab.setLayout(fc_layout)
#         self.tab_widget.addTab(fc_tab, "First Check")
        
#         # Onglet DC
#         dc_tab = QWidget()
#         dc_layout = QVBoxLayout()
#         dc_tab.setLayout(dc_layout)
#         self.tab_widget.addTab(dc_tab, "Double Check")
        
#         # Onglet Thèmes
#         themes_tab = QWidget()
#         themes_layout = QVBoxLayout()
#         themes_tab.setLayout(themes_layout)
#         self.tab_widget.addTab(themes_tab, "Themes")
        
#         # Onglet Configurations
#         config_tab = QWidget()
#         config_layout = QVBoxLayout()
#         config_tab.setLayout(config_layout)
#         self.tab_widget.addTab(config_tab, "Configurations")
        
#         # Création des champs pour chaque section
#         self._create_general_fields(general_layout)
#         self._create_fc_fields(fc_layout)
#         self._create_dc_fields(dc_layout)
#         self._create_themes_fields(themes_layout)
#         self._create_config_fields(config_layout)
        
#         # Boutons
#         button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
#         button_box.accepted.connect(self._save_config)
#         button_box.rejected.connect(self.reject)
#         layout.addWidget(button_box)
        
        
#     def _create_fc_fields(self, layout):
#         """Crée les champs pour les constantes FC"""
#         form_layout = QFormLayout()
#         layout.addLayout(form_layout)
        
#         self.fc_word_title_edit = QLineEdit()
#         form_layout.addRow("Word Title:", self.fc_word_title_edit)
        
#         self.fc_id_field_edit = QLineEdit()
#         form_layout.addRow("ID Field:", self.fc_id_field_edit)
        
#         self.fc_restri_id_edit = QLineEdit()
#         form_layout.addRow("Restriction ID:", self.fc_restri_id_edit)
        
#         self.fc_label_field_edit = QLineEdit()
#         form_layout.addRow("Label Field:", self.fc_label_field_edit)
        
#         self.fc_type_restri_edit = QLineEdit()
#         form_layout.addRow("Type Restriction Strict:", self.fc_type_restri_edit)
        
#     def _create_dc_fields(self, layout):
#         """Crée les champs pour les constantes DC"""
#         form_layout = QFormLayout()
#         layout.addLayout(form_layout)
        
#         self.dc_word_title_edit = QLineEdit()
#         form_layout.addRow("Word Title:", self.dc_word_title_edit)
        
#         self.dc_id_field_edit = QLineEdit()
#         form_layout.addRow("ID Field:", self.dc_id_field_edit)
        
#         self.dc_restri_id_edit = QLineEdit()
#         form_layout.addRow("Restriction ID:", self.dc_restri_id_edit)
        
#         self.dc_label_field_edit = QLineEdit()
#         form_layout.addRow("Label Field:", self.dc_label_field_edit)
        
#         self.dc_type_restri_edit = QLineEdit()
#         form_layout.addRow("Type Restriction Strict:", self.dc_type_restri_edit)
        
#     def _create_themes_fields(self, layout):
#         """Crée les champs pour les thèmes FC et DC"""
#         notebook = QTabWidget()
#         layout.addWidget(notebook)
        
#         # Onglet Thèmes FC
#         fc_themes_tab = QWidget()
#         fc_themes_scroll = QScrollArea()
#         fc_themes_scroll.setWidgetResizable(True)
        
#         fc_themes_content = QWidget()
#         fc_themes_layout = QFormLayout(fc_themes_content)
#         fc_themes_scroll.setWidget(fc_themes_content)
        
#         self.fc_theme_edits = {}
#         for key, value in Config.FC_THEMES_DICT.items():
#             edit = QLineEdit()
#             edit.setText(value)
#             fc_themes_layout.addRow(f"Theme {key}:", edit)
#             self.fc_theme_edits[key] = edit
        
#         fc_themes_tab.setLayout(QVBoxLayout())
#         fc_themes_tab.layout().addWidget(fc_themes_scroll)
#         notebook.addTab(fc_themes_tab, "FC Themes")
        
#         # Onglet Thèmes DC
#         dc_themes_tab = QWidget()
#         dc_themes_scroll = QScrollArea()
#         dc_themes_scroll.setWidgetResizable(True)
        
#         dc_themes_content = QWidget()
#         dc_themes_layout = QFormLayout(dc_themes_content)
#         dc_themes_scroll.setWidget(dc_themes_content)
        
#         self.dc_theme_edits = {}
#         for key, value in Config.DC_THEMES_DICT.items():
#             edit = QLineEdit()
#             edit.setText(value)
#             dc_themes_layout.addRow(f"Theme {key}:", edit)
#             self.dc_theme_edits[key] = edit
        
#         dc_themes_tab.setLayout(QVBoxLayout())
#         dc_themes_tab.layout().addWidget(dc_themes_scroll)
#         notebook.addTab(dc_themes_tab, "DC Themes")  


#     def _create_general_fields(self, layout):
#         """Crée les champs pour les constantes générales avec menu déroulant pour le basemap"""
#         form_layout = QFormLayout()
#         layout.addLayout(form_layout)
        
#         self.plugin_name_edit = QLineEdit()
#         form_layout.addRow("Plugin Name:", self.plugin_name_edit)
        
#         self.footer_text_edit = QLineEdit()
#         form_layout.addRow("Footer Text:", self.footer_text_edit)
        
#         # Menu déroulant pour le basemap
#         self.basemap_combo = QComboBox()
#         self._populate_layer_combo(self.basemap_combo, Config.BASEMAP)
#         form_layout.addRow("Basemap:", self.basemap_combo)

#     def _create_config_fields(self, layout):
#         """Crée les champs pour les configurations FC et DC avec menus déroulants pour les couches"""
#         notebook = QTabWidget()
#         layout.addWidget(notebook)
        
#         # Config FC
#         fc_config_tab = QWidget()
#         fc_config_layout = QVBoxLayout()
#         fc_config_scroll = QScrollArea()
#         fc_config_scroll.setWidgetResizable(True)
#         fc_config_tab.setLayout(fc_config_layout)
#         fc_config_scroll.setWidget(fc_config_tab)
#         notebook.addTab(fc_config_scroll, "FC Config")
        
#         self.fc_config_edits = {}
#         for tech_code, tech_config in Config.FC_CONFIG.items():
#             group = QGroupBox(tech_config.get('technology', f'Tech {tech_code}'))
#             group_layout = QFormLayout()
#             group.setLayout(group_layout)
#             fc_config_layout.addWidget(group)
            
#             tech_edits = {}
#             for field, value in tech_config.items():
#                 if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
#                     # Menu déroulant pour les couches
#                     combo = QComboBox()
#                     self._populate_layer_combo(combo, value)
#                     group_layout.addRow(f"{field}:", combo)
#                     tech_edits[field] = combo
#                 else:
#                     # Champ texte normal pour les autres champs
#                     edit = QLineEdit()
#                     if isinstance(value, type(QVariant.Int)):
#                         edit.setText('QVariant.Int')
#                     else:
#                         edit.setText(str(value))
#                     group_layout.addRow(f"{field}:", edit)
#                     tech_edits[field] = edit
#             self.fc_config_edits[tech_code] = tech_edits
        
#         # Config DC
#         dc_config_tab = QWidget()
#         dc_config_layout = QVBoxLayout()
#         dc_config_scroll = QScrollArea()
#         dc_config_scroll.setWidgetResizable(True)
#         dc_config_tab.setLayout(dc_config_layout)
#         dc_config_scroll.setWidget(dc_config_tab)
#         notebook.addTab(dc_config_scroll, "DC Config")
        
#         self.dc_config_edits = {}
#         for tech_code, tech_config in Config.DC_CONFIG.items():
#             group = QGroupBox(tech_config.get('technology', f'Tech {tech_code}'))
#             group_layout = QFormLayout()
#             group.setLayout(group_layout)
#             dc_config_layout.addWidget(group)
            
#             tech_edits = {}
#             for field, value in tech_config.items():
#                 if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
#                     # Menu déroulant pour les couches
#                     combo = QComboBox()
#                     self._populate_layer_combo(combo, value)
#                     group_layout.addRow(f"{field}:", combo)
#                     tech_edits[field] = combo
#                 else:
#                     # Champ texte normal pour les autres champs
#                     edit = QLineEdit()
#                     if isinstance(value, type(QVariant.Int)):
#                         edit.setText('QVariant.Int')
#                     else:
#                         edit.setText(str(value))
#                     group_layout.addRow(f"{field}:", edit)
#                     tech_edits[field] = edit
#             self.dc_config_edits[tech_code] = tech_edits
            
#     def _load_config_values(self):
#         """Charge les valeurs actuelles dans les champs"""
#         self.plugin_name_edit.setText(Config.PLUGIN_NAME)
#         self.footer_text_edit.setText(Config.FOOTER_MIDDLE_TEXT)
#         index = self.basemap_combo.findText(Config.BASEMAP)
#         if index >= 0:
#             self.basemap_combo.setCurrentIndex(index)
        
#         # FC
#         self.fc_word_title_edit.setText(Config.FC_WORD_TITLE_TEXT)
#         self.fc_id_field_edit.setText(Config.FC_ID_FIELD)
#         self.fc_restri_id_edit.setText(Config.FC_RESTRI_ID)
#         self.fc_label_field_edit.setText(Config.FC_LABEL_FIELD)
#         self.fc_type_restri_edit.setText(Config.FC_TYPE_RESTRI_STRICT)
        
#         # DC
#         self.dc_word_title_edit.setText(Config.DC_WORD_TITLE_TEXT)
#         self.dc_id_field_edit.setText(Config.DC_ID_FIELD)
#         self.dc_restri_id_edit.setText(Config.DC_RESTRI_ID)
#         self.dc_label_field_edit.setText(Config.DC_LABEL_FIELD)
#         self.dc_type_restri_edit.setText(Config.DC_TYPE_RESTRI_STRICT)

#         # Charger les thèmes FC
#         for key, edit in self.fc_theme_edits.items():
#             edit.setText(Config.FC_THEMES_DICT.get(key, ""))

#         # Charger les thèmes DC
#         for key, edit in self.dc_theme_edits.items():
#             edit.setText(Config.DC_THEMES_DICT.get(key, ""))
            
        
#     def _populate_layer_combo(self, combo_box, default_value=None):
#         """Remplit un QComboBox avec les noms des couches du projet et sélectionne la valeur par défaut"""
#         combo_box.clear()
        
#         # Ajouter une entrée vide optionnelle
#         combo_box.addItem("", None)
        
#         # Récupérer toutes les couches du projet
#         layers = QgsProject.instance().mapLayers().values()
#         layer_names = [layer.name() for layer in layers]
        
#         # Trier les noms par ordre alphabétique
#         layer_names.sort()
        
#         # Ajouter les noms au combo box
#         for name in layer_names:
#             combo_box.addItem(name, name)
        
#         # Sélectionner la valeur par défaut si elle existe
#         if default_value:
#             index = combo_box.findText(default_value)
#             if index >= 0:
#                 combo_box.setCurrentIndex(index)
#             else:
#                 # Si la couche n'existe pas, l'ajouter comme élément spécial
#                 combo_box.addItem(f"{default_value} (non trouvé)", default_value)
#                 combo_box.setCurrentIndex(combo_box.count() - 1)

#     def _save_config(self):
#         """Sauvegarde les modifications dans le fichier de configuration"""
#         try:
#             # Constantes générales
#             Config.PLUGIN_NAME = self.plugin_name_edit.text()
#             Config.FOOTER_MIDDLE_TEXT = self.footer_text_edit.text()
#             Config.BASEMAP = self.basemap_combo.currentData() or self.basemap_combo.currentText()
            
#             # FC
#             Config.FC_WORD_TITLE_TEXT = self.fc_word_title_edit.text()
#             Config.FC_ID_FIELD = self.fc_id_field_edit.text()
#             Config.FC_RESTRI_ID = self.fc_restri_id_edit.text()
#             Config.FC_LABEL_FIELD = self.fc_label_field_edit.text()
#             Config.FC_TYPE_RESTRI_STRICT = self.fc_type_restri_edit.text()
            
#             # DC
#             Config.DC_WORD_TITLE_TEXT = self.dc_word_title_edit.text()
#             Config.DC_ID_FIELD = self.dc_id_field_edit.text()
#             Config.DC_RESTRI_ID = self.dc_restri_id_edit.text()
#             Config.DC_LABEL_FIELD = self.dc_label_field_edit.text()
#             Config.DC_TYPE_RESTRI_STRICT = self.dc_type_restri_edit.text()
            
#             # Thèmes FC
#             for key, edit in self.fc_theme_edits.items():
#                 Config.FC_THEMES_DICT[key] = edit.text()
                
#             # Thèmes DC
#             for key, edit in self.dc_theme_edits.items():
#                 Config.DC_THEMES_DICT[key] = edit.text()
                
#             # Config FC
#             for tech, edits in self.fc_config_edits.items():
#                 for field, widget in edits.items():
#                     if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
#                         Config.FC_CONFIG[tech][field] = widget.currentData() or widget.currentText()
#                     else:
#                         value = widget.text()
#                         if field == 'restri_join_id_field':
#                             Config.FC_CONFIG[tech][field] = QVariant.Int if value == 'QVariant.Int' else value
#                         else:
#                             Config.FC_CONFIG[tech][field] = value
            
#             # Config DC
#             for tech, edits in self.dc_config_edits.items():
#                 for field, widget in edits.items():
#                     if field in ['global_area_layer', 'feasible_layer', 'restriction_layer']:
#                         Config.DC_CONFIG[tech][field] = widget.currentData() or widget.currentText()
#                     else:
#                         value = widget.text()
#                         if field == 'restri_join_id_field':
#                             Config.DC_CONFIG[tech][field] = QVariant.Int if value == 'QVariant.Int' else value
#                         else:
#                             Config.DC_CONFIG[tech][field] = value
            
#             QMessageBox.information(self, "Success", "Configuration updated successfully!")
#             self.accept()
            
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")