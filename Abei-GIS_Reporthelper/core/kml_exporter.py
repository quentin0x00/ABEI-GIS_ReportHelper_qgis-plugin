from ..imports import *
from ..config import Config

class KMLEXporter:
    """Gère les opérations d'exportation en format KML."""

    @staticmethod
    def export_kml(features, output_path, fields_to_export=None, layer_name="temp_kml_layer"):
        """
        Exporte des entités en fichier KML.

        :param features: Liste des entités à exporter.
        :param output_path: Chemin de sortie pour le fichier KML.
        :param fields_to_export: Dictionnaire des champs à exporter (nom du champ et type).
        :param layer_name: Nom de la couche temporaire pour l'export.
        :return: Erreur de l'opération d'exportation, le cas échéant.
        """
        if not features:
            return

        fields = QgsFields()
        if fields_to_export:
            for field_name, field_type in fields_to_export.items():
                fields.append(QgsField(field_name, field_type))

        crs = QgsCoordinateReferenceSystem("EPSG:3857")
        mem_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", layer_name, "memory")
        mem_layer_data = mem_layer.dataProvider()
        mem_layer_data.addAttributes(fields)
        mem_layer.updateFields()

        for feature in features:
            new_feature = QgsFeature()
            new_feature.setGeometry(feature.geometry())

            if fields_to_export:
                attributes = []
                for field_name in fields_to_export.keys():
                    attributes.append(feature[field_name])
                new_feature.setAttributes(attributes)

            mem_layer_data.addFeature(new_feature)

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "KML"
        options.fileEncoding = "UTF-8"
        error = QgsVectorFileWriter.writeAsVectorFormatV2(
            mem_layer,
            output_path,
            QgsProject.instance().transformContext(),
            options
        )

        return error

    @staticmethod
    def export_source_area_kml(layer, fc_id, fc_label, output_dir):
        """
        Exporte la zone source en fichier KML.

        :param layer: La couche source contenant les données.
        :param fc_id: L'ID de la fonctionnalité.
        :param fc_label: Le label de la fonctionnalité.
        :param output_dir: Le répertoire de sortie pour les fichiers KML.
        """
        features = layer.getFeatures(QgsFeatureRequest().setFilterExpression(f"id = {fc_id}"))
        if not features:
            return

        buffer_value = None
        for feature in features:
            buffer_value = feature['source_buffer']
            break

        if buffer_value is not None:
            buffer_km = int(buffer_value) // 1000
            output_filename = f"Source-area{buffer_km}km.kml"
        else:
            output_filename = "Source-area.kml"

        features = layer.getFeatures(QgsFeatureRequest().setFilterExpression(f"id = {fc_id}"))
        output_path = os.path.join(output_dir, output_filename)

        error = KMLEXporter.export_kml(features, output_path,
                     fields_to_export={"id": QVariant.Int, "label": QVariant.String, "source_buffer": QVariant.Int},
                     layer_name="source_area")

        if error[0] != QgsVectorFileWriter.NoError:
            raise Exception(f"Error exporting source area: {error[1]}")

    @staticmethod
    def export_feasible_area_kml(config, fc_id, output_dir):
        """
        Exporte la zone faisable en fichier KML.

        :param config: La configuration contenant les informations de la couche faisable.
        :param fc_id: L'ID de la fonctionnalité.
        :param output_dir: Le répertoire de sortie pour les fichiers KML.
        """
        feasible_layer = QgsProject.instance().mapLayersByName(config['feasible_layer'])
        if not feasible_layer:
            return

        feasible_layer = feasible_layer[0]
        request = QgsFeatureRequest().setFilterExpression(f"id = {fc_id}")
        features = list(feasible_layer.getFeatures(request))

        if not features:
            return

        output_path = os.path.join(output_dir, f"Feasible-area_with_conditional.kml")
        error = KMLEXporter.export_kml(features, output_path,
                     fields_to_export={"id": QVariant.Int, "label": QVariant.String},
                     layer_name="feasible_area")

        if error[0] != QgsVectorFileWriter.NoError:
            raise Exception(f"Error exporting feasible area: {error[1]}")

    @staticmethod
    def export_restrictions_kml(config, fc_id, output_dir):
        """
        Exporte les restrictions en fichier KML.

        :param config: La configuration contenant les informations de la couche des restrictions.
        :param fc_id: L'ID de la fonctionnalité.
        :param output_dir: Le répertoire de sortie pour les fichiers KML.
        """
        restriction_layer = QgsProject.instance().mapLayersByName(config['restriction_layer'])
        if not restriction_layer:
            return

        restriction_layer = restriction_layer[0]
        request = QgsFeatureRequest().setFilterExpression(f"{config['id_field']} = '{fc_id}' AND type_restriction = '1'")
        features = list(restriction_layer.getFeatures(request))

        if not features:
            return

        grouped_by_label = defaultdict(list)
        grouped_by_theme = defaultdict(list)
        for f in features:
            grouped_by_label[f["label"]].append(f)
            theme_raw = f['theme']
            theme_str = str(theme_raw).strip()
            theme_name = Config.THEMES_DICT.get(theme_str, "Unknown") if theme_str.isdigit() else theme_str or "Unknown"
            grouped_by_theme[theme_name].append(f)

        # Export all restrictions by theme
        for theme_name, feats in grouped_by_theme.items():
            output_path = os.path.join(output_dir, f"[all-restrictions]{theme_name}.kml")
            error = KMLEXporter.export_kml(feats, output_path,
                         fields_to_export={config['id_field']: QVariant.String, "id": QVariant.Int, "label": QVariant.String},
                         layer_name="restrictions")

            if error[0] != QgsVectorFileWriter.NoError:
                raise Exception(f"Error exporting restrictions by theme {theme_name}: {error[1]}")

        # Export detailed restrictions by label
        for label, feats in grouped_by_label.items():
            theme_raw = feats[0]['theme']
            theme_str = str(theme_raw).strip()
            theme_name = Config.THEMES_DICT.get(theme_str, "Unknown") if theme_str.isdigit() else theme_str or "Unknown"
            safelabel = label.replace(" ", "").replace("/", "").replace("\\", "")

            theme_directory = os.path.join(output_dir, "detailed-restrictions", theme_name)
            os.makedirs(theme_directory, exist_ok=True)

            output_path = os.path.join(theme_directory, f"{safelabel}.kml")
            error = KMLEXporter.export_kml(feats, output_path,
                         fields_to_export={config['id_field']: QVariant.String, "id": QVariant.Int, "label": QVariant.String},
                         layer_name="restriction")

            if error[0] != QgsVectorFileWriter.NoError:
                raise Exception(f"Error exporting restriction {label}: {error[1]}")
    