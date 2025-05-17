from ..imports import *

class ImageExporter:
    """Gère les opérations d'exportation d'image."""

    def __init__(self, layer_manager):
        """
        Initialisation de l'exportateur d'images.

        :param layer_manager: Instance de `LayerManager` pour accéder aux couches de la carte.
        """
        self.layer_manager = layer_manager
        self.width, self.height = self.layer_manager.fc_extent.width(), self.layer_manager.fc_extent.height()
        self.margin_x, self.margin_y = self.width * 0.1, self.height * 0.1

    def export_image(self, extent, output_path, subset=None):
        """
        Exporte une image de la carte dans un fichier.

        :param extent: Étendue géographique à capturer sous forme de `QgsRectangle`.
        :param output_path: Chemin de sortie pour enregistrer l'image au format PNG.
        :param subset: Expression de filtre pour restreindre les entités visibles (optionnel).
        """
        if subset:
            self.layer_manager.restriction_layer.setSubsetString(subset)

        rect = QgsRectangle(
            extent.xMinimum() - self.margin_x,
            extent.yMinimum() - self.margin_y,
            extent.xMaximum() + self.margin_x,
            extent.yMaximum() + self.margin_y
        )

        map_settings = QgsMapSettings()
        visible_layers = [
            self.layer_manager.restriction_layer,
            self.layer_manager.area_layer,
            self.layer_manager.feasible_layer if self.layer_manager.feasible_layer else None,
            QgsProject.instance().mapLayersByName('OSM Standard')[0]
        ]
        visible_layers = [l for l in visible_layers if l is not None]
        map_settings.setLayers(visible_layers)
        map_settings.setOutputSize(QSize(800, 600))
        map_settings.setExtent(rect)

        render = QgsMapRendererSequentialJob(map_settings)
        render.start()
        render.waitForFinished()
        img = render.renderedImage()
        img.save(output_path, "PNG")
        QgsMessageLog.logMessage(f"Image exported: {output_path}", "[Abei GIS] Report helper", Qgis.Info)
