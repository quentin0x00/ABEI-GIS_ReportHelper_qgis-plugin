from ..imports import *
from .kml_exporter import KMLEXporter
from .report_generator import ReportGenerator
from .layer_manager import LayerManager
from ..config import Config
from .image_exporter import ImageExporter

class PluginController:
    """Contrôleur principal du plugin — gère les actions d'export et de génération de rapports."""

    def __init__(self, widget):
        """
        Initialise le contrôleur du plugin.

        :param widget: DockWidget graphique principal (interface utilisateur)
        """
        self.widget = widget

    def export_to_kml(self):
        """
        Interface du plugin. Exporte les données au format KML.

        Étapes :
        - Vérifie qu’un objet est sélectionné et qu’une technologie est choisie
        - Récupère la couche correspondante via un motif (regex)
        - Demande un dossier de sortie à l'utilisateur
        - Crée les fichiers KML : zone source, zone de faisabilité, restrictions
        """
        try:
            if not self.widget.selected_analysis:
                raise ValueError("No analysis selected")

            technology = self.widget.technology_combo.currentData()
            if not technology:
                raise ValueError("Please select a technology type")

            config = Config.get_config(technology)

            layer_name_pattern = config['global_area_layer']
            matching_layers = [layer for layer in QgsProject.instance().mapLayers().values()
                            if re.search(layer_name_pattern, layer.name())]

            if not matching_layers:
                raise ValueError(f"No layer found matching pattern: {layer_name_pattern}")

            layer = matching_layers[0]
            iface.setActiveLayer(layer)
            analysis_id = self.widget.selected_analysis[Config.get_id_field()]
            analysis_label = self.widget.selected_analysis[Config.get_label_field()] if Config.get_label_field() in self.widget.selected_analysis.fields().names() else f"id_{analysis_id}"

            output_dir = QFileDialog.getExistingDirectory(
                self.widget,
                "Select Output Directory",
                os.path.expanduser("~")
            )

            if not output_dir:
                return

            current_datetime = QDateTime.currentDateTime().toString("dd-MM-yyyy_hh'h'mm")
            parent_directory = os.path.join(output_dir, f"[Vmap-KML]{config['technology']}-{Config.get_analyse_type()}={analysis_label}")
            os.makedirs(parent_directory, exist_ok=True)

            KMLEXporter.export_source_area_kml(layer, analysis_id, analysis_label, parent_directory)
            KMLEXporter.export_feasible_area_kml(config, analysis_id, parent_directory)
            KMLEXporter.export_restrictions_kml(config, analysis_id, parent_directory)

            QMessageBox.information(
                self.widget,
                "Success",
                f"KML files exported."
            )

        except Exception as e:
            QMessageBox.critical(self.widget, "Error", f"Error during KML export:\n{str(e)}")
            QgsMessageLog.logMessage(f"KML export error: {str(e)}", "FC Report", Qgis.Critical)

    def generate_report(self):
        """
        Interface du plugin. Créé le rapport Word.

        Étapes :
        1. Vérifie la sélection (analyse + technologie)
        2. Récupère la bonne couche via un motif
        3. Demande un répertoire de sortie
        4. Instancie le gestionnaire de couches (LayerManager)
        5. Regroupe les entités par thème (via Config)
        6. Crée le rapport Word avec images et données
        7. Supprime les couches temporaires

        Affiche un message d’erreur en cas de problème, avec infos utiles.
        """
        try:
            if not self.widget.selected_analysis:
                raise ValueError("No object selected")

            # 1. Get configuration
            technology = self.widget.technology_combo.currentData()
            if not technology:
                raise ValueError("Please select a technology type")

            config = Config.get_config(technology)

            # 2. Check and select the correct layer
            layer_name_pattern = config['global_area_layer']
            matching_layers = [layer for layer in QgsProject.instance().mapLayers().values()
                            if re.search(layer_name_pattern, layer.name())]

            if not matching_layers:
                raise ValueError(f"No layer found matching pattern: {layer_name_pattern}")

            layer = matching_layers[0]
            iface.setActiveLayer(layer)

            # 3. Get ID and label directly as in the action script
            analysis_id = self.widget.selected_analysis[Config.get_id_field()]
            analysis_label = self.widget.selected_analysis['label'] if 'label' in self.widget.selected_analysis.fields().names() else f"id_{analysis_id}"

            # 4. Ask for output directory
            output_dir = QFileDialog.getExistingDirectory(
                self.widget,
                "Select Output Directory",
                os.path.expanduser("~")
            )

            if not output_dir:
                return

            # 5. Initialize managers
            layer_manager = LayerManager(layer.name(), analysis_id, analysis_label)
            layer_manager.setup_layers()

            # 6. Group features
            features = layer_manager.get_restriction_features()
            grouped_by_theme = defaultdict(list)

            for f in features:
                theme_raw = f['theme']
                theme_str = str(theme_raw).strip()
                theme_name = Config.THEMES_DICT.get(theme_str, "Unknown") if theme_str.isdigit() else theme_str or "Unknown"
                grouped_by_theme[theme_name].append(f)

            # 7. Generate report
            image_exporter = ImageExporter(layer_manager)
            report_generator = ReportGenerator(layer_manager, image_exporter, output_dir)
            report_path = report_generator.create_word_document(grouped_by_theme)

            # 8. Cleanup
            layer_manager.cleanup()

            QMessageBox.information(
                self.widget,
                "Success",
                f"Report generated"
            )

        except Exception as e:
            error_msg = f"""Error generating report:
            {str(e)}

            Available fields in layer:
            {self.widget.selected_analysis.fields().names() if hasattr(self.widget, 'selected_analysis') and self.widget.selected_analysis else 'No object selected'}

            Expected configuration:
            {config}"""  # <-- Utilisez directement la config déjà récupérée

            QMessageBox.critical(self.widget, "Critical Error", error_msg)
