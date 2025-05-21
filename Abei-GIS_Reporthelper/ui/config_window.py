from ..config import *

class ConfigEditorDialog(QDialog):
    """Boîte de dialogue pour éditer les constantes de configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Editor")
        self.setMinimumSize(600, 500)
        
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
        
        # Onglet Thèmes
        themes_tab = QWidget()
        themes_layout = QVBoxLayout()
        themes_tab.setLayout(themes_layout)
        self.tab_widget.addTab(themes_tab, "Themes")
        
        # Onglet Configurations
        config_tab = QWidget()
        config_layout = QVBoxLayout()
        config_tab.setLayout(config_layout)
        self.tab_widget.addTab(config_tab, "Configurations")
        
        # Création des champs pour chaque section
        self._create_general_fields(general_layout)
        self._create_fc_fields(fc_layout)
        self._create_dc_fields(dc_layout)
        self._create_themes_fields(themes_layout)
        self._create_config_fields(config_layout)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_config)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _create_general_fields(self, layout):
        """Crée les champs pour les constantes générales"""
        form_layout = QFormLayout()
        layout.addLayout(form_layout)
        
        self.plugin_name_edit = QLineEdit()
        form_layout.addRow("Plugin Name:", self.plugin_name_edit)
        
        self.footer_text_edit = QLineEdit()
        form_layout.addRow("Footer Text:", self.footer_text_edit)
        
        self.basemap_edit = QLineEdit()
        form_layout.addRow("Basemap:", self.basemap_edit)
        
    def _create_fc_fields(self, layout):
        """Crée les champs pour les constantes FC"""
        form_layout = QFormLayout()
        layout.addLayout(form_layout)
        
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
        
    def _create_dc_fields(self, layout):
        """Crée les champs pour les constantes DC"""
        form_layout = QFormLayout()
        layout.addLayout(form_layout)
        
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
        
    def _create_themes_fields(self, layout):
        """Crée les champs pour les thèmes"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        form_layout = QFormLayout()
        content.setLayout(form_layout)
        
        self.theme_edits = {}
        for key, value in Config.THEMES_DICT.items():
            edit = QLineEdit()
            edit.setText(value)
            form_layout.addRow(f"Theme {key}:", edit)
            self.theme_edits[key] = edit
            
    def _create_config_fields(self, layout):
        """Crée les champs pour les configurations FC et DC - Version corrigée"""
        notebook = QTabWidget()
        layout.addWidget(notebook)
        
        # Config FC - Correction ici
        fc_config_tab = QWidget()
        fc_config_layout = QVBoxLayout()
        fc_config_scroll = QScrollArea()
        fc_config_scroll.setWidgetResizable(True)
        fc_config_tab.setLayout(fc_config_layout)
        fc_config_scroll.setWidget(fc_config_tab)
        notebook.addTab(fc_config_scroll, "FC Config")
        
        self.fc_config_edits = {}
        for tech_code, tech_config in Config.FC_CONFIG.items():
            group = QGroupBox(tech_config.get('technology', f'Tech {tech_code}'))
            group_layout = QFormLayout()
            group.setLayout(group_layout)
            fc_config_layout.addWidget(group)
            
            tech_edits = {}
            for field, value in tech_config.items():
                edit = QLineEdit()
                # Conversion spéciale pour QVariant
                if isinstance(value, type(QVariant.Int)):
                    edit.setText('QVariant.Int')
                else:
                    edit.setText(str(value))
                group_layout.addRow(f"{field}:", edit)
                tech_edits[field] = edit
            self.fc_config_edits[tech_code] = tech_edits
        
        # Config DC - Même correction
        dc_config_tab = QWidget()
        dc_config_layout = QVBoxLayout()
        dc_config_scroll = QScrollArea()
        dc_config_scroll.setWidgetResizable(True)
        dc_config_tab.setLayout(dc_config_layout)
        dc_config_scroll.setWidget(dc_config_tab)
        notebook.addTab(dc_config_scroll, "DC Config")
        
        self.dc_config_edits = {}
        for tech_code, tech_config in Config.DC_CONFIG.items():
            group = QGroupBox(tech_config.get('technology', f'Tech {tech_code}'))
            group_layout = QFormLayout()
            group.setLayout(group_layout)
            dc_config_layout.addWidget(group)
            
            tech_edits = {}
            for field, value in tech_config.items():
                edit = QLineEdit()
                if isinstance(value, type(QVariant.Int)):
                    edit.setText('QVariant.Int')
                else:
                    edit.setText(str(value))
                group_layout.addRow(f"{field}:", edit)
                tech_edits[field] = edit
            self.dc_config_edits[tech_code] = tech_edits
            
    def _load_config_values(self):
        """Charge les valeurs actuelles dans les champs"""
        self.plugin_name_edit.setText(Config.PLUGIN_NAME)
        self.footer_text_edit.setText(Config.FOOTER_MIDDLE_TEXT)
        self.basemap_edit.setText(Config.BASEMAP)
        
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
        
    def _save_config(self):
        """Sauvegarde les modifications dans le fichier de configuration"""
        try:
            # Constantes générales
            Config.PLUGIN_NAME = self.plugin_name_edit.text()
            Config.FOOTER_MIDDLE_TEXT = self.footer_text_edit.text()
            Config.BASEMAP = self.basemap_edit.text()
            
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
            
            # Thèmes
            for key, edit in self.theme_edits.items():
                Config.THEMES_DICT[key] = edit.text()
                
            # Config FC
            for tech, edits in self.fc_config_edits.items():
                for field, edit in edits.items():
                    Config.FC_CONFIG[tech][field] = edit.text()
                    if field == 'id_field':
                        # Conversion en QVariant si nécessaire
                        Config.FC_CONFIG[tech][field] = QVariant.Int if edit.text() == 'QVariant.Int' else edit.text()
            
            # Config DC
            for tech, edits in self.dc_config_edits.items():
                for field, edit in edits.items():
                    Config.DC_CONFIG[tech][field] = edit.text()
                    if field == 'id_field':
                        # Conversion en QVariant si nécessaire
                        Config.DC_CONFIG[tech][field] = QVariant.Int if edit.text() == 'QVariant.Int' else edit.text()
            
            QMessageBox.information(self, "Success", "Configuration updated successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")