from ..imports import *
from ..config import Config

class LayerManager:
    """Gère les opérations sur les couches QGIS."""

    def __init__(self, layer_name, analysis_id, analysis_label):
        """
        Initialise le gestionnaire de couches.
        """
        self.analysis_id = analysis_id
        self.analysis_label = analysis_label
        self.source_layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        self._determine_technology()

    def _determine_technology(self):
        """
        Détermine la technologie à partir du nom de la couche.
        """
        if self.source_layer:
            layer_name = self.source_layer.name()
            current_mode = 'FC' if Config.CURRENT_MODE == 'FC' else 'DC'
            config_dict = Config.FC_CONFIG if current_mode == 'FC' else Config.DC_CONFIG
            
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
        
        # Utilisation des méthodes get_*
        id_field = Config.get_id_field()
        request = QgsFeatureRequest().setFilterExpression(f'"{id_field}" = {self.analysis_id}')
        feature = next(self.source_layer.getFeatures(request))
        self.analysis_extent = feature.geometry().boundingBox()

        self.area_layer = self.source_layer
        self.feasible_layer = QgsProject.instance().mapLayersByName(self.analysis_data['feasible_layer'])[0] if QgsProject.instance().mapLayersByName(self.analysis_data['feasible_layer']) else None
        self.restriction_layer = QgsProject.instance().mapLayersByName(self.analysis_data['restriction_layer'])[0]
        
        self.area_layer.setSubsetString(f'"{id_field}" = {self.analysis_id}')
        if self.feasible_layer:
            self.feasible_layer.setSubsetString(f'"{id_field}" = {self.analysis_id}')

    # def get_restriction_features(self):
    #     """
    #     Récupère les entités de restrictions en utilisant get_restri_id().
    #     """
    #     restri_id_field = Config.get_restri_id()  # 'id' pour FC, 'as_id' pour DC
    #     type_restri = Config.get_type_restri_strict()  # '1' ou 'Restriction'
        
    #     request = QgsFeatureRequest().setFilterExpression(
    #         f'"{restri_id_field}" = \'{self.analysis_id}\' '
    #         f'AND "type_restriction" = \'{type_restri}\''
    #     )
    #     features = list(self.restriction_layer.getFeatures(request))

    #     if not features:
    #         raise Exception(
    #             f"No restrictions found for {restri_id_field}={self.analysis_id} "
    #             f"and type_restriction={type_restri}"
    #         )
    #     return features

    def get_restriction_features(self):
        """
        Récupère les entités de restrictions.
        """
        request = QgsFeatureRequest().setFilterExpression(
            f"{self.analysis_data['id_field']} = '{self.analysis_id}' "
            f"AND type_restriction = {Config.get_type_restri_strict()}"
        )
        features = list(self.restriction_layer.getFeatures(request))

        if not features:
            raise Exception(f"No restrictions found for analysis_id = {self.analysis_id}")
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