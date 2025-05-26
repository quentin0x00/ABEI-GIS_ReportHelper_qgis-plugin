from ..imports import *
from ..config import Config

class LayerManager:
    """Gère les opérations sur les couches QGIS."""

    def __init__(self, layer_name, analysis_id, analysis_label, config=None):
        """
        Initialise le gestionnaire de couches.
        """
        self.analysis_id = analysis_id
        self.analysis_label = analysis_label
        self.selected_technology = None
        self.analysis_data = config if config else {}
        self.source_layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        
        # Store field names for consistent access
        self.id_field = Config.get_id_field()
        self.label_field = Config.get_label_field()
        
        if config is None:
            self._determine_technology()

    def _determine_technology(self):
        """
        Détermine la technologie à partir du nom de la couche.
        """
        if self.source_layer:
            layer_name = self.source_layer.name()
            config_dict = Config.FC_CONFIG if Config.CURRENT_MODE == 'FC' else Config.DC_CONFIG
            
            for technology, config in config_dict.items():
                if re.search(config['global_area_layer'], layer_name):
                    self.selected_technology = technology
                    self.analysis_data = config
                    break

        if not self.selected_technology:
            raise Exception("Selected layer is not a recognized area layer")

    def setup_layers(self):
        """
        Configure les couches pour le traitement.
        """
        self.source_layer.select([])
        
        # Use the stored id_field
        request = QgsFeatureRequest().setFilterExpression(f'"{self.id_field}" = {self.analysis_id}')
        feature = next(self.source_layer.getFeatures(request))
        self.analysis_extent = feature.geometry().boundingBox()

        self.area_layer = self.source_layer
        self.feasible_layer = QgsProject.instance().mapLayersByName(self.analysis_data['feasible_layer'])[0] if QgsProject.instance().mapLayersByName(self.analysis_data['feasible_layer']) else None
        self.restriction_layer = QgsProject.instance().mapLayersByName(self.analysis_data['restriction_layer'])[0]
        
        self.area_layer.setSubsetString(f'"{self.id_field}" = {self.analysis_id}')
        if self.feasible_layer:
            self.feasible_layer.setSubsetString(f'"{self.id_field}" = {self.analysis_id}')

    def get_restriction_features(self):
        """
        Récupère les entités de restrictions.
        """
        # Use the restri_join_id_field from the config
        request = QgsFeatureRequest().setFilterExpression(
            f'"{self.analysis_data["restri_join_id_field"]}" = \'{self.analysis_id}\' '
            f'AND "type_restriction" = \'{Config.get_type_restri_strict()}\''
        )
        features = list(self.restriction_layer.getFeatures(request))

        if not features:
            raise Exception(
                f"No restrictions found for {self.analysis_data['restri_join_id_field']}={self.analysis_id} "
                f"and type_restriction={Config.get_type_restri_strict()}"
            )
        return features

    def cleanup(self):
        """
        Nettoie les couches après traitement.
        """
        self.restriction_layer.setSubsetString(Config.get_restriction_filter())
        self.restriction_layer.triggerRepaint()
        self.area_layer.setSubsetString("")
        if self.feasible_layer:
            self.feasible_layer.setSubsetString("")