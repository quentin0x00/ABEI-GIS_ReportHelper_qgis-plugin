from ..imports import *
from ..config import Config

class LayerManager:
    """Gère les opérations sur les couches QGIS."""

    def __init__(self, layer_name, fc_id, fc_label):
        """
        Initialise le gestionnaire de couches.

        :param layer_name: Nom de la couche source (ex : "Area FC")
        :param fc_id: id qu'on associe au fc_s_id (sur solar par ex)
        :param fc_label: label du FC
        """
        self.fc_id = fc_id
        self.fc_label = fc_label
        self.selected_fc_type = None
        self.fc_data = None
        self.source_layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        self._determine_fc_type()

    def _determine_fc_type(self):
        """
        Détermine la technology du FC à partir du nom de la couche.

        Vérifie le nom de la couche source et le compare aux motifs définis dans
        la configuration (Config.FC_CONFIG) pour déterminer le type de FC.
        """
        if self.source_layer:
            layer_name = self.source_layer.name()
            for fc_type, config in Config.FC_CONFIG.items():
                if re.search(config['area_layer_pattern'], layer_name):
                    self.selected_fc_type = fc_type
                    self.fc_data = Config.FC_CONFIG[fc_type]
                    break

        if not self.selected_fc_type:
            raise Exception("Selected layer is not a recognized FC Area layer")

    def setup_layers(self):
        """
        Configure les couches pour le traitement des données.

        - Sélectionne les entités de la couche source correspondant à l'ID.
        - Récupère les autres couches (feasible, restriction) définies dans la configuration.
        - Applique un filtre à la couche pour ne garder que l'ID sélectionné.
        """
        self.source_layer.select([])

        request = QgsFeatureRequest().setFilterExpression(f"id = {self.fc_id}")
        feature = next(self.source_layer.getFeatures(request))
        self.fc_extent = feature.geometry().boundingBox()

        self.area_layer = self.source_layer
        self.feasible_layer = QgsProject.instance().mapLayersByName(self.fc_data['feasible_layer'])[0] if QgsProject.instance().mapLayersByName(self.fc_data['feasible_layer']) else None
        self.restriction_layer = QgsProject.instance().mapLayersByName(self.fc_data['restriction_layer'])[0]
        self.area_layer.setSubsetString(f"id = {self.fc_id}")
        if self.feasible_layer:
            self.feasible_layer.setSubsetString(f"id = {self.fc_id}")

    def get_restriction_features(self):
        """
        Récupère les entités de restrictions pour la fonctionnalité sélectionnée.

        :return: Liste des entités de restriction.
        :raises Exception: Si aucune restriction n'est trouvée pour l'ID sélectionné.
        """
        request = QgsFeature
        request = QgsFeatureRequest().setFilterExpression(f"{self.fc_data['id_field']} = '{self.fc_id}' AND type_restriction = '1'")
        features = list(self.restriction_layer.getFeatures(request))

        if not features:
            raise Exception(f"No restrictions found for FC_ID = {self.fc_id}")
        return features

    def cleanup(self):
        """
        Nettoie les couches après traitement.

        - Réinitialise les filtres sur les couches et les repaints.
        """
        self.restriction_layer.setSubsetString('"type_restriction" = \'1\'')
        self.restriction_layer.triggerRepaint()
        self.area_layer.setSubsetString("")
        if self.feasible_layer:
            self.feasible_layer.setSubsetString("")
