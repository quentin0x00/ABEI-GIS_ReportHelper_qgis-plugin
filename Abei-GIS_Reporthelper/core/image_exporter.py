from ..imports import *
from ..config import Config

class ImageExporter:
    """Gère les opérations d'exportation d'image."""

    def __init__(self, layer_manager):
        """
        Initialisation de l'exportateur d'images.

        :param layer_manager: Instance de `LayerManager` pour accéder aux couches de la carte.
        """
        self.layer_manager = layer_manager
        self.width, self.height = self.layer_manager.analysis_extent.width(), self.layer_manager.analysis_extent.height()
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
            self.layer_manager.conditional_layer if self.layer_manager.conditional_layer else None,
            self.layer_manager.feasible_layer if self.layer_manager.feasible_layer else None,
            QgsProject.instance().mapLayersByName(Config.BASEMAP)[0]
        ]
        visible_layers = [l for l in visible_layers if l is not None]
        map_settings.setLayers(visible_layers)
        map_settings.setOutputSize(QSize(800, 600))
        map_settings.setExtent(rect)

        render = QgsMapRendererSequentialJob(map_settings)
        render.start()
        render.waitForFinished()
        img = render.renderedImage()
        
        # ECHELLE
        map_units_per_pixel = rect.width() / map_settings.outputSize().width()
        max_bar_px = 30
        raw_length_m = max_bar_px * map_units_per_pixel

        def round_scale(val):
            for step in [1, 2, 5]:
                for power in range(0, 6):
                    rounded = step * (10 ** power)
                    if val <= rounded:
                        return rounded
            return val

        scale_length_m = round_scale(raw_length_m)
        scale_pixel_length = int(scale_length_m / map_units_per_pixel)

        margin = 20
        bar_height = 2
        x = img.width() - scale_pixel_length - margin
        y = img.height() - bar_height - margin

        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.black)
        painter.drawRect(x, y, scale_pixel_length, bar_height)
        
        painter.setPen(Qt.black)
        font = QFont("Sans Serif", 10)
        painter.setFont(font)
        painter.drawText(x, y - 5, f"{scale_length_m} m")
        painter.end()

        
        # --- Légende améliorée ---
        legend_margin = 20
        line_height = 25
        symbol_size = 16
        max_lines = 10

        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Sans Serif", 10)
        painter.setFont(font)

        x_legend = legend_margin
        y_legend = legend_margin

        # Créer un contexte de rendu minimal
        context = QgsRenderContext.fromMapSettings(map_settings)
        context.setPainter(painter)

        for layer in visible_layers[:max_lines]:
            if not layer or not isinstance(layer, QgsVectorLayer):
                continue
                
            # Récupérer le symbole principal de la couche
            renderer = layer.renderer()
            if not renderer:
                continue

            # Cas 1 : rendu par symbole unique
            if isinstance(renderer, QgsSingleSymbolRenderer):
                symbol = renderer.symbol()
                if symbol:
                    symbol.startRender(context)
                    if layer.geometryType() == QgsWkbTypes.PointGeometry:
                        symbol.renderPoint(QPointF(x_legend + symbol_size / 2, y_legend + symbol_size / 2), None, context)
                    elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                        points = [QPointF(x_legend, y_legend + symbol_size / 2),
                                QPointF(x_legend + symbol_size, y_legend + symbol_size / 2)]
                        symbol.renderPolyline(points, None, context)
                    elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                        polygon = QPolygonF([
                            QPointF(x_legend, y_legend),
                            QPointF(x_legend + symbol_size, y_legend),
                            QPointF(x_legend + symbol_size, y_legend + symbol_size),
                            QPointF(x_legend, y_legend + symbol_size)
                        ])
                        symbol.renderPolygon(polygon, None, None, context)
                    symbol.stopRender(context)
                    painter.setPen(Qt.black)
                    painter.drawText(x_legend + symbol_size + 5, y_legend + symbol_size - 5, layer.name())
                    y_legend += line_height

            # Cas 2 : rendu par catégories
            elif isinstance(renderer, QgsCategorizedSymbolRenderer):
                # Extraire les valeurs visibles dans l'étendue et avec subset
                provider = layer.dataProvider()
                request = QgsFeatureRequest(rect)
                request.setSubsetOfAttributes([renderer.classAttribute()], provider.fields())
                visible_values = set()

                for feat in layer.getFeatures(request):
                    val = feat[renderer.classAttribute()]
                    if val is not None:
                        visible_values.add(val)
                        
                drawn_labels = set()

                for cat in renderer.categories():
                    if not cat.renderState():
                        continue  # catégorie décochée
                    if cat.value() not in visible_values:
                        continue  # catégorie non visible

                    label = cat.label()
                    if label in drawn_labels:
                        continue  # cette légende a déjà été dessinée

                    symbol = cat.symbol()
                    symbol.startRender(context)
                    if layer.geometryType() == QgsWkbTypes.PointGeometry:
                        symbol.renderPoint(QPointF(x_legend + symbol_size / 2, y_legend + symbol_size / 2), None, context)
                    elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                        points = [QPointF(x_legend, y_legend + symbol_size / 2),
                                QPointF(x_legend + symbol_size, y_legend + symbol_size / 2)]
                        symbol.renderPolyline(points, None, context)
                    elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                        polygon = QPolygonF([
                            QPointF(x_legend, y_legend),
                            QPointF(x_legend + symbol_size, y_legend),
                            QPointF(x_legend + symbol_size, y_legend + symbol_size),
                            QPointF(x_legend, y_legend + symbol_size)
                        ])
                        symbol.renderPolygon(polygon, None, None, context)
                    symbol.stopRender(context)

                    painter.setPen(Qt.black)
                    painter.drawText(x_legend + symbol_size + 5, y_legend + symbol_size - 5, label)
                    y_legend += line_height

                    drawn_labels.add(label)  # marquer cette légende comme déjà affichée

        painter.end()

        img.save(output_path, "PNG")
        QgsMessageLog.logMessage(f"Image exported: {output_path}", Config.PLUGIN_NAME, Qgis.Info)
