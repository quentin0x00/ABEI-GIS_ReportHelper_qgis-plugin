from .imports import *


class Config:
    """Configuration centralisée du plugin Abei GIS Report Helper"""

    ### === SERVICES ===
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
        
    # === CONST ===
    PLUGIN_NAME = 'Abei GIS Report Helper'
    FOOTER_MIDDLE_TEXT = "ENVIRONMENTAL AND URBAN PLANNING ANALYSIS"
    BASEMAP = 'OSM Standard'
    
    CURRENT_MODE = 'FC'
    
    # FC
    FC_ANALYSE_TYPE = 'FirstCheck'
    FC_WORD_TITLE_TEXT = 'First Check - GIS report [Vmap]'
    FC_ID_FIELD = 'id'
    FC_RESTRI_ID = 'id'
    FC_LABEL_FIELD = 'label'
    FC_TYPE_RESTRI_STRICT = '1'
    FC_REINIT_RESTRI_STRICT_FILTER = '"type_restriction" = \'1\''
    FC_KML_FIELDS_EXPORT_SOURCEAREA = {
        "id": QVariant.Int,
        "label": QVariant.String,
        "source_buffer": QVariant.Int
    }
    FC_KML_FIELDS_EXPORT_FEASIBLEAREA = {
        "id": QVariant.Int,
        "label": QVariant.String
    }

    # DC
    DC_ANALYSE_TYPE = 'DoubleCheck'
    DC_WORD_TITLE_TEXT = 'Double Check - GIS report [Vmap]'
    DC_ID_FIELD = 'fid'
    DC_RESTRI_ID = 'as_id'
    DC_LABEL_FIELD = 'name'
    DC_TYPE_RESTRI_STRICT = 'Restriction'
    DC_REINIT_RESTRI_STRICT_FILTER = '"type_restriction" = \'1\''
    DC_KML_FIELDS_EXPORT_SOURCEAREA = {
        "fid": QVariant.Int,
        "name": QVariant.String
    }
    DC_KML_FIELDS_EXPORT_FEASIBLEAREA = {
        "fid": QVariant.Int,
        "name": QVariant.String
    }


    FC_FILTER_VALUES = {
        "Administration": "1",
        "Culture": "2",
        "Energy Infrastructure": "3",
        "Energy Renewable": "4",
        "Environment": "5",
        "Hydrography": "6",
        "Landuse": "7",
        "Military": "8",
        "Oil and Gas": "9",
        "Point of Interest": "10",
        "Risk": "11",
        "Transportation": "12",
        "Urban": "13"
    }

    DC_FILTER_VALUES = {
        "Administration": "Administration",
        "Culture": "Culture",
        "Energy Infrastructure": "Energy Infrastructure",
        "Energy Renewable": "Energy Renewable",
        "Environment": "Environment",
        "Hydrography": "Hydrography",
        "Landuse": "Landuse",
        "Military": "Military",
        "Oil and Gas": "Oil and Gas",
        "Point of Interest": "Point of Interest",
        "Risk": "Risk",
        "Transportation": "Transportation",
        "Urban": "Urban"
    }

    THEME_DISPLAY = {
        "1": "Administration",
        "2": "Culture",
        "3": "Energy Infrastructure",
        "4": "Energy Renewable",
        "5": "Environment",
        "6": "Hydrography",
        "7": "Landuse",
        "8": "Military",
        "9": "Oil and Gas",
        "10": "Point of Interest",
        "11": "Risk",
        "12": "Transportation",
        "13": "Urban"
    }






    FC_CONFIG = {
        's': {'global_area_layer': r'FC Area - Solar', 'feasible_layer': 'FC Feasible and Conditional area - Solar','conditional_layer': 'FC Conditional area - Solar', 'restriction_layer': 'FC Strict restrictions - Solar', 'restri_join_id_field': 'fc_s_id', 'technology': 'Solar'},
        'w': {'global_area_layer': r'FC Area - Wind', 'feasible_layer': 'FC Feasible and Conditional area - Wind','conditional_layer': 'FC Conditional area - Wind', 'restriction_layer': 'FC Strict restrictions - Wind', 'restri_join_id_field': 'fc_w_id', 'technology': 'Wind'},
        'b': {'global_area_layer': r'FC Area - Bess', 'feasible_layer': 'FC Feasible and Conditional area - Bess','conditional_layer': 'FC Conditional area - Bess', 'restriction_layer': 'FC Strict restrictions - Bess', 'restri_join_id_field': 'fc_b_id', 'technology': 'Bess'},
        'h': {'global_area_layer': r'FC Area - Hydrogen', 'feasible_layer': 'FC Feasible and Conditional area - Hydrogen','conditional_layer': 'FC Conditional area - H2', 'restriction_layer': 'FC Strict restrictions - Hydrogen', 'restri_join_id_field': 'fc_h_id', 'technology': 'Hydrogen'},
        'd': {'global_area_layer': r'FC Area - Datacenter', 'feasible_layer': 'FC Feasible and Conditional area - Datacenter','conditional_layer': 'FC Conditional area - Datacenter', 'restriction_layer': 'FC Strict restrictions - Datacenter', 'restri_join_id_field': 'fc_d_id', 'technology': 'Datacenter'},
        'bm': {'global_area_layer': r'FC Area - Biomethan', 'feasible_layer': 'FC Feasible and Conditional area - Biomethan', 'conditional_layer': 'FC Conditional area - Biomethan','restriction_layer': 'FC Strict restrictions - Biomethan', 'restri_join_id_field': 'fc_bm_id', 'technology': 'Biomethan'}
    }

    DC_CONFIG = {
        's': {'global_area_layer': r'DC Area - Solar', 'feasible_layer': 'DC Feasible and Conditional area - Solar','conditional_layer': 'DC Conditional area - Solar', 'restriction_layer': 'DC Strict restrictions - Solar', 'restri_join_id_field': 'fid_dc', 'technology': 'Solar'},
        'w': {'global_area_layer': r'DC Area - Wind', 'feasible_layer': 'DC Feasible and Conditional area - Wind','conditional_layer': 'DC Conditional area - Wind',  'restriction_layer': 'DC Strict restrictions - Wind', 'restri_join_id_field': 'fid_dc', 'technology': 'Wind'},
        'b': {'global_area_layer': r'DC Area - Bess', 'feasible_layer': 'DC Feasible and Conditional area - Bess','conditional_layer': 'DC Conditional area - Bess', 'restriction_layer': 'DC Strict restrictions - Bess', 'restri_join_id_field': 'fid_dc', 'technology': 'Bess'},
        'h': {'global_area_layer': r'DC Area - Hydrogen', 'feasible_layer': 'DC Feasible and Conditional area - Hydrogen','conditional_layer': 'DC Conditional area - H2',  'restriction_layer': 'DC Strict restrictions - Hydrogen', 'restri_join_id_field': 'fid_dc', 'technology': 'Hydrogen'},
        'd': {'global_area_layer': r'DC Area - Datacenter', 'feasible_layer': 'DC Feasible and Conditional area - Datacenter','conditional_layer': 'DC Conditional area - Datacenter',  'restriction_layer': 'DC Strict restrictions - Datacenter', 'restri_join_id_field': 'fid_dc', 'technology': 'Datacenter'},
        'bm': {'global_area_layer': r'DC Area - Biomethan', 'feasible_layer': 'DC Feasible and Conditional area - Biomethan','conditional_layer': 'DC Conditional area - Biomethan',  'restriction_layer': 'DC Strict restrictions - Biomethan', 'restri_join_id_field': 'fid_dc', 'technology': 'Biomethan'}
    }
        