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
    def export_source_area_kml(layer, analysis_id, analysis_label, output_dir):
        """
        Exporte la zone source en KML, gère automatiquement le cas DC sans source_buffer.
        """
        try:
            # 1. Récupère l'entité
            features = list(layer.getFeatures(
                QgsFeatureRequest().setFilterExpression(f"{Config.get_id_field()} = {analysis_id}")
            ))
            if not features:
                QgsMessageLog.logMessage(
                    f"No features found for ID {analysis_id}",
                    "ABEI GIS", Qgis.Warning
                )
                return

            # 2. Détermine le nom du fichier
            buffer_km = ""
            if Config.CURRENT_MODE == 'FC' and 'source_buffer' in features[0].fields():
                buffer_value = features[0]['source_buffer']
                if buffer_value is not None:
                    buffer_km = f"_{int(buffer_value) // 1000}km"
            
            output_filename = f"Source-area{buffer_km}.kml"
            output_path = os.path.join(output_dir, output_filename)

            # 3. Export KML avec les champs adaptés
            fields_to_export = {
                k: v for k, v in Config.get_kml_source_fields().items() 
                if k in features[0].fields()
            }

            error = KMLEXporter.export_kml(
                layer.getFeatures(QgsFeatureRequest().setFilterExpression(f"{Config.get_id_field()} = {analysis_id}")),
                output_path,
                fields_to_export=fields_to_export,
                layer_name="source_area"
            )

            if error[0] != QgsVectorFileWriter.NoError:
                raise Exception(f"KML export error: {error[1]}")

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error in export_source_area_kml: {str(e)}",
                "ABEI GIS", Qgis.Critical
            )
            raise

    @staticmethod
    def export_feasible_area_kml(config, analysis_id, output_dir):
        """
        Exporte la zone faisable en fichier KML.

        :param config: La configuration contenant les informations de la couche faisable.
        :param analysis_id: L'ID de la fonctionnalité.
        :param output_dir: Le répertoire de sortie pour les fichiers KML.
        """
        feasible_layer = QgsProject.instance().mapLayersByName(config['feasible_layer'])
        if not feasible_layer:
            return

        feasible_layer = feasible_layer[0]
        request = QgsFeatureRequest().setFilterExpression(f"{Config.get_id_field()} = {analysis_id}")
        features = list(feasible_layer.getFeatures(request))

        if not features:
            return

        output_path = os.path.join(output_dir, f"Feasible-area.kml")
        error = KMLEXporter.export_kml(features, output_path,
                     fields_to_export=Config.get_kml_feasible_fields(),
                     layer_name="feasible_area")

        if error[0] != QgsVectorFileWriter.NoError:
            raise Exception(f"Error exporting feasible area: {error[1]}")

    @staticmethod
    def export_restrictions_kml(config, analysis_id, output_dir):
        """
        Exporte les restrictions en fichier KML.

        :param config: La configuration contenant les informations de la couche des restrictions.
        :param analysis_id: L'ID de la fonctionnalité.
        :param output_dir: Le répertoire de sortie pour les fichiers KML.
        """
        restriction_layer = QgsProject.instance().mapLayersByName(config['restriction_layer'])
        if not restriction_layer:
            return

        restriction_layer = restriction_layer[0]
        request = QgsFeatureRequest().setFilterExpression(f"{config['restri_join_id_field']} = '{analysis_id}' AND type_restriction = '{Config.get_type_restri_strict()}'")
        features = list(restriction_layer.getFeatures(request))

        if not features:
            return

        grouped_by_label = defaultdict(list)
        grouped_by_theme = defaultdict(list)
        for f in features:
            grouped_by_label[f["label"]].append(f)
            theme_value = f['theme']
            theme_display_name = Config.get_display_name(theme_value)
            grouped_by_theme[theme_display_name].append(f)

        # Export all restrictions by theme
        for theme_display_name , feats in grouped_by_theme.items():
            output_path = os.path.join(output_dir, f"[all-restrictions]{theme_display_name}.kml")
            error = KMLEXporter.export_kml(feats, output_path,
                         fields_to_export={config['restri_join_id_field']: QVariant.String, Config.get_restri_id(): QVariant.Int, "label": QVariant.String},
                         layer_name="restrictions")

            if error[0] != QgsVectorFileWriter.NoError:
                raise Exception(f"Error exporting restrictions by theme {theme_display_name}: {error[1]}")

        # Export detailed restrictions by label
        for label, feats in grouped_by_label.items():
            theme_value = feats[0]['theme']
            theme_display_name = Config.get_display_name(theme_value)
            safelabel = label.replace(" ", "").replace("/", "").replace("\\", "").replace(".","")

            theme_directory = os.path.join(output_dir, "detailed-restrictions", theme_display_name)
            os.makedirs(theme_directory, exist_ok=True)

            output_path = os.path.join(theme_directory, f"{safelabel}.kml")
            error = KMLEXporter.export_kml(feats, output_path,
                         fields_to_export={config['restri_join_id_field']: QVariant.String, Config.get_restri_id(): QVariant.Int, "label": QVariant.String},
                         layer_name="restriction")

            if error[0] != QgsVectorFileWriter.NoError:
                raise Exception(f"Error exporting restriction {label}: {error[1]}")
    