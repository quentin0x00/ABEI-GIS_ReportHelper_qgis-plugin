from .imports import *
import json
from pathlib import Path

class Config:
    """Configuration centralisée du plugin Abei GIS Report Helper"""
    
    _config_path = Path(__file__).parent / 'param.json'
    _config_data = None
    CURRENT_MODE = 'FC'

    # Initialisation au chargement de la classe
    @classmethod
    def _load_config(cls):
        """Charge/recharge la configuration depuis le fichier JSON"""
        with open(cls._config_path, 'r', encoding='utf-8') as f:
            cls._config_data = json.load(f)
    
    # Initialisation au premier accès
    @classmethod
    def _ensure_loaded(cls):
        if cls._config_data is None:
            cls._load_config()

    # === Version dynamique des constantes ===
    @classmethod
    @property
    def PLUGIN_NAME(cls):
        cls._ensure_loaded()
        return cls._config_data['global']['PLUGIN_NAME']

    @classmethod
    @property
    def FOOTER_MIDDLE_TEXT(cls):
        cls._ensure_loaded()
        return cls._config_data['global']['FOOTER_MIDDLE_TEXT']

    @classmethod
    @property
    def BASEMAP(cls):
        cls._ensure_loaded()
        return cls._config_data['global']['BASEMAP']

    @classmethod
    @property
    def THEME_DISPLAY(cls):
        cls._ensure_loaded()
        return cls._config_data['global']['THEME_DISPLAY']

    # FC Properties
    @classmethod
    @property
    def FC_ANALYSE_TYPE(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_ANALYSE_TYPE']

    @classmethod
    @property
    def FC_WORD_TITLE_TEXT(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_WORD_TITLE_TEXT']

    @classmethod
    @property
    def FC_ID_FIELD(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_ID_FIELD']

    @classmethod
    @property
    def FC_RESTRI_ID(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_RESTRI_ID']

    @classmethod
    @property
    def FC_LABEL_FIELD(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_LABEL_FIELD']

    @classmethod
    @property
    def FC_TYPE_RESTRI_STRICT(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_TYPE_RESTRI_STRICT']

    @classmethod
    @property
    def FC_REINIT_RESTRI_STRICT_FILTER(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_REINIT_RESTRI_STRICT_FILTER']

    @classmethod
    @property
    def FC_KML_FIELDS_EXPORT_SOURCEAREA(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_KML_FIELDS_EXPORT_SOURCEAREA']

    @classmethod
    @property
    def FC_KML_FIELDS_EXPORT_FEASIBLEAREA(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_KML_FIELDS_EXPORT_FEASIBLEAREA']

    @classmethod
    @property
    def FC_FILTER_VALUES(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_FILTER_VALUES']

    @classmethod
    @property
    def FC_CONFIG(cls):
        cls._ensure_loaded()
        return cls._config_data['FC']['FC_CONFIG']

    # DC Properties
    @classmethod
    @property
    def DC_ANALYSE_TYPE(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_ANALYSE_TYPE']

    @classmethod
    @property
    def DC_WORD_TITLE_TEXT(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_WORD_TITLE_TEXT']

    @classmethod
    @property
    def DC_ID_FIELD(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_ID_FIELD']

    @classmethod
    @property
    def DC_RESTRI_ID(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_RESTRI_ID']

    @classmethod
    @property
    def DC_LABEL_FIELD(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_LABEL_FIELD']

    @classmethod
    @property
    def DC_TYPE_RESTRI_STRICT(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_TYPE_RESTRI_STRICT']

    @classmethod
    @property
    def DC_REINIT_RESTRI_STRICT_FILTER(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_REINIT_RESTRI_STRICT_FILTER']

    @classmethod
    @property
    def DC_KML_FIELDS_EXPORT_SOURCEAREA(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_KML_FIELDS_EXPORT_SOURCEAREA']

    @classmethod
    @property
    def DC_KML_FIELDS_EXPORT_FEASIBLEAREA(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_KML_FIELDS_EXPORT_FEASIBLEAREA']

    @classmethod
    @property
    def DC_FILTER_VALUES(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_FILTER_VALUES']

    @classmethod
    @property
    def DC_CONFIG(cls):
        cls._ensure_loaded()
        return cls._config_data['DC']['DC_CONFIG']

    ### === SERVICES (inchangés) ===
    @staticmethod
    def set_mode(mode):
        if mode in ('FC', 'DC'):
            Config.CURRENT_MODE = mode
        else:
            raise ValueError("Mode must be 'FC' or 'DC'")
        
    @staticmethod
    def get_analyse_type():
        return Config.FC_ANALYSE_TYPE if Config.CURRENT_MODE == 'FC' else Config.DC_ANALYSE_TYPE

    @staticmethod
    def get_word_title():
        return Config.FC_WORD_TITLE_TEXT if Config.CURRENT_MODE == 'FC' else Config.DC_WORD_TITLE_TEXT

    @staticmethod
    def get_id_field():
        return Config.FC_ID_FIELD if Config.CURRENT_MODE == 'FC' else Config.DC_ID_FIELD

    @staticmethod
    def get_restri_id():
        return Config.FC_RESTRI_ID if Config.CURRENT_MODE == 'FC' else Config.DC_RESTRI_ID

    @staticmethod
    def get_label_field():
        return Config.FC_LABEL_FIELD if Config.CURRENT_MODE == 'FC' else Config.DC_LABEL_FIELD

    @staticmethod
    def get_type_restri_strict():
        return Config.FC_TYPE_RESTRI_STRICT if Config.CURRENT_MODE == 'FC' else Config.DC_TYPE_RESTRI_STRICT

    @staticmethod
    def get_restriction_filter():
        return Config.FC_REINIT_RESTRI_STRICT_FILTER if Config.CURRENT_MODE == 'FC' else Config.DC_REINIT_RESTRI_STRICT_FILTER

    @staticmethod
    def get_kml_source_fields():
        return Config.FC_KML_FIELDS_EXPORT_SOURCEAREA if Config.CURRENT_MODE == 'FC' else Config.DC_KML_FIELDS_EXPORT_SOURCEAREA

    @staticmethod
    def get_kml_feasible_fields():
        return Config.FC_KML_FIELDS_EXPORT_FEASIBLEAREA if Config.CURRENT_MODE == 'FC' else Config.DC_KML_FIELDS_EXPORT_FEASIBLEAREA

    @staticmethod
    def get_config(tech_code):
        return Config.FC_CONFIG[tech_code] if Config.CURRENT_MODE == 'FC' else Config.DC_CONFIG[tech_code]
    
    @staticmethod
    def get_display_name(theme_value):
        """Pour les noms de fichiers/dossiers/titres"""
        return Config.THEME_DISPLAY.get(str(theme_value), str(theme_value))

    @staticmethod
    def get_filter_value(display_name):
        """Pour les valeurs de filtre (FC=numérique, DC=texte)"""
        if Config.CURRENT_MODE == 'FC':
            return Config.FC_FILTER_VALUES.get(display_name, display_name)
        else:
            return Config.DC_FILTER_VALUES.get(display_name, display_name)