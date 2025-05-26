from ..imports import *
from .kml_exporter import KMLEXporter
from .report_generator import ReportGenerator
from .layer_manager import LayerManager
from ..config import Config
from .image_exporter import ImageExporter

class PluginController:
    def __init__(self, widget):
        self.widget = widget

    def export_to_kml(self):
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
            KMLEXporter.export_conditional_area_kml(config, analysis_id, parent_directory)
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

            # 3. Get ID and label - with proper field existence checks
            id_field = Config.get_id_field()
            label_field = Config.get_label_field()
            
            if id_field not in self.widget.selected_analysis.fields().names():
                raise ValueError(f"ID field '{id_field}' not found in selected feature")
                
            analysis_id = self.widget.selected_analysis[id_field]
            analysis_label = self.widget.selected_analysis[label_field] if label_field in self.widget.selected_analysis.fields().names() else f"id_{analysis_id}"

            # 4. Ask for output directory
            output_dir = QFileDialog.getExistingDirectory(
                self.widget,
                "Select Output Directory",
                os.path.expanduser("~")
            )
            if not output_dir:
                return

            restriction_layer_name = config['restriction_layer']
            restriction_layer = next((l for l in QgsProject.instance().mapLayers().values()
                                    if l.name() == restriction_layer_name), None)

            if restriction_layer:
                renderer = restriction_layer.renderer()
                if hasattr(renderer, 'rootRule'):
                    def enable_rules(rule):
                        if hasattr(rule, 'children'):
                            for child in rule.children():
                                enable_rules(child)
                        rule.setActive(True)

                    enable_rules(renderer.rootRule())
                    restriction_layer.triggerRepaint()

            # 5. Initialize LayerManager with the config
            layer_manager = LayerManager(
                layer_name=layer.name(),
                analysis_id=analysis_id,
                analysis_label=analysis_label,
                config=config
            )
            layer_manager.setup_layers()

            # 6. Group features
            features = layer_manager.get_restriction_features()
            grouped_by_theme = defaultdict(list)

            # Dans la partie groupement des features:
            for f in features:
                theme_raw = f['theme']
                theme_str = str(theme_raw).strip()
                # On garde la valeur originale pour le groupement
                grouped_by_theme[theme_str].append(f)

            # 7. Generate report
            image_exporter = ImageExporter(layer_manager)
            report_generator = ReportGenerator(layer_manager, image_exporter, output_dir)
            report_path = report_generator.create_word_document(grouped_by_theme)

            # 8. Cleanup
            layer_manager.cleanup()

            QMessageBox.information(
                self.widget,
                "Success",
                f"Report generated: {report_path}"
            )

        except Exception as e:
            error_msg = f"""Error generating report:
            {str(e)}

            Selected analysis fields: {self.widget.selected_analysis.fields().names() if hasattr(self.widget, 'selected_analysis') and self.widget.selected_analysis else 'No object selected'}

            Config ID field: {Config.get_id_field()}
            Config label field: {Config.get_label_field()}
            Current mode: {Config.CURRENT_MODE}"""

            QMessageBox.critical(self.widget, "Critical Error", error_msg)