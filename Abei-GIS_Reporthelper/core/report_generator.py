from ..imports import *
from ..config import Config

class ReportGenerator:
    """Génère des rapports Word pour l'analyse environnementale"""

    def __init__(self, layer_manager, image_exporter, output_directory):
        """
        Initialise le générateur de rapports.
        """
        self.layer_manager = layer_manager
        self.image_exporter = image_exporter
        self.output_directory = output_directory
        self.current_datetime = QDateTime.currentDateTime().toString("dd-MM-yyyy_hh'h'mm")
        self.report_directory = os.path.join(output_directory)
        
        # Store field names from config for consistent access
        self.id_field = Config.get_id_field()
        self.label_field = Config.get_label_field()
        self.restri_join_id_field = layer_manager.analysis_data['restri_join_id_field']
        self.type_restri_strict = Config.get_type_restri_strict()

        # Logo path setup
        self.logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "icon.png")
        if not os.path.exists(self.logo_path):
            self.logo_path = None
            QgsMessageLog.logMessage(f"Warning: Logo not found at {self.logo_path}", "ABEI GIS", Qgis.Warning)

    def _add_header(self, doc):
        """
        Ajoute un en-tête au document Word.
        Comprend un logo (si disponible) ou le nom "ABEI Energy".
        """
        section = doc.sections[0]
        header = section.header

        header_table = header.add_table(1, 2, width=Inches(6.5))
        header_table.autofit = False

        hdr_cols = header_table.columns
        hdr_cols[0].width = Inches(1.5)
        hdr_cols[1].width = Inches(5.0)

        logo_cell = header_table.cell(0, 0)
        logo_para = logo_cell.paragraphs[0]
        logo_para.alignment = WD_ALIGN_PARAGRAPH.LEFT

        try:
            if self.logo_path and os.path.exists(self.logo_path):
                logo_run = logo_para.add_run()
                logo_run.add_picture(self.logo_path, width=Inches(1.0))
            else:
                logo_para.text = "ABEI Energy"
        except Exception as e:
            print(f"Error loading logo: {str(e)}")
            logo_para.text = "ABEI Energy"


    def _add_footer(self, doc):
        """
        Ajoute un pied de page au document.
        Contient la date actuelle, le type de rapport et le label du projet.
        """
        current_date = QDateTime.currentDateTime().toString("dd/MM/yyyy")
        footer = doc.sections[0].footer
        footer_paragraph = footer.paragraphs[0]
        footer_paragraph.text = f"({current_date}) - {Config.FOOTER_MIDDLE_TEXT} - {self.layer_manager.analysis_label}"
        footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _add_general_info(self, doc):
        """
        Ajoute une section avec les informations générales sur le projet :
        nom, technologie, date, développeur, etc.
        """
        doc.add_heading('General informations', level=1)
        info_table = doc.add_table(rows=7, cols=2)
        info_table.style = 'Table Grid'
        info_table.autofit = False
        info_table.columns[0].width = Inches(2.5)
        info_table.columns[1].width = Inches(2.5)
        rows = info_table.rows

        data = [
            ("NAME OF PROJECT OR LANDOWNER", self.layer_manager.analysis_label),
            ("TECHNOLOGY", self.layer_manager.analysis_data['technology']),
            ("COUNTY", ""),
            ("TOWNSHIP", ""),
            ("DATE", QDateTime.currentDateTime().toString("dd/MM/yyyy")),
            ("PROJECT DEVELOPER", ""),
            ("ENVIRONMENTAL TECHNICIAN", (QgsProject.instance().baseName()))
        ]

        for i, (label, value) in enumerate(data):
            rows[i].cells[0].text = label
            rows[i].cells[1].text = value

        for row in rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    paragraph.paragraph_format.space_after = Pt(0)
                    paragraph.paragraph_format.space_before = Pt(0)

    def _add_theme_section(self, doc, theme_name, feats, grouped=True):
        """
        Ajoute une section thématique au rapport, contenant :

        - Le nom du thème
        - Une table avec labels + image(s) + commentaire(s)
        - Données regroupées ou individuelles selon le paramètre `grouped`

        :param doc: Document Word
        :param theme_name: Nom du thème
        :param feats: Liste des entités à afficher
        :param grouped: Regrouper les labels ou non
        """
        doc.add_heading(theme_name, level=2)

        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        table.columns[0].width = Inches(3)
        table.columns[1].width = Inches(4)
        table.columns[2].width = Inches(2)

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Labels list' if grouped else 'Label'
        hdr_cells[1].text = 'Capture'
        hdr_cells[2].text = 'Notes'

        if grouped:
            self._add_grouped_theme_content(table, feats)
        else:
            self._add_individual_theme_content(table, feats)

        doc.add_paragraph()
        
    def _add_global_feasible_restriction_map(self, doc):
        """Aperçu dans un tableau sans paramètre obsolète"""
        doc.add_heading("Analysis overview", level=2)
        
        # Tableau ajusté (total 5.5")
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.columns[0].width = Inches(1.0)  # Colonne Notes
        table.columns[1].width = Inches(4.5)  # Colonne Capture

        # En-têtes
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Notes'
        hdr_cells[1].text = 'Capture'

        # Contenu
        row_cells = table.add_row().cells
        row_cells[0].text = ''  # Cellule vide

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_img_path = temp_file.name
        
        subset = f'"{self.restri_join_id_field}" = \'{self.layer_manager.analysis_id}\' AND "type_restriction" = \'{self.type_restri_strict}\''

        try:
            # Appel SIMPLIFIÉ sans paramètre
            self.image_exporter.export_image(self.layer_manager.analysis_extent, temp_img_path, subset)
            
            # Image à 4.3" pour rester dans la marge
            row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row_cells[1].paragraphs[0].add_run().add_picture(temp_img_path, width=Inches(4.3))
        except Exception as e:
            row_cells[1].text = f"Erreur : {str(e)}"
            QgsMessageLog.logMessage(f"Erreur export image : {str(e)}", "ABEI GIS", Qgis.Warning)
        finally:
            try: os.remove(temp_img_path)
            except: pass
        doc.add_paragraph()  # Espace après le tableau

    def _add_grouped_theme_content(self, table, feats):
        """
        Ajoute une ligne au tableau avec tous les labels regroupés d'un thème.
        """
        row_cells = table.add_row().cells

        # Use the stored label_field
        unique_labels = sorted(set(f[Config.get_label_field()] for f in feats))
        row_cells[0].text = "\n".join(f"• {label}" for label in unique_labels)

        theme_str = str(feats[0]['theme']).strip()
        subset = (f'"{self.restri_join_id_field}" = \'{self.layer_manager.analysis_id}\' '
                 f'AND "type_restriction" = \'{self.type_restri_strict}\' '
                 f'AND "theme" = \'{theme_str}\'')

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_img_path = temp_file.name

        self.image_exporter.export_image(self.layer_manager.analysis_extent, temp_img_path, subset)

        try:
            row_cells[1].paragraphs[0].add_run().add_picture(temp_img_path, width=Inches(3.5))
        except Exception as e:
            row_cells[1].text = f"Error loading image: {str(e)}"
            QgsMessageLog.logMessage(f"Error loading image: {str(e)}", "ABEI GIS", Qgis.Warning)
        finally:
            try:
                os.remove(temp_img_path)
            except:
                pass

    def _add_individual_theme_content(self, table, feats):
        """
        Ajoute une ligne par label dans le tableau.
        """
        # On groupe d'abord par label
       
        # On trie les labels par ordre alphabétique
        for label in sorted(set(f[Config.get_label_field()] for f in feats)):
            row_cells = table.add_row().cells
            row_cells[0].text = label

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_img_path = temp_file.name

            subset = (f'"{self.restri_join_id_field}" = \'{self.layer_manager.analysis_id}\' '
                    f'AND \"type_restriction\" = \'{self.type_restri_strict}\' '
                    f'AND label = \'{label.replace("'", "''")}\'')
            
            try:
                self.image_exporter.export_image(self.layer_manager.analysis_extent, temp_img_path, subset)
                row_cells[1].paragraphs[0].add_run().add_picture(temp_img_path, width=Inches(3.5))
            except Exception as e:
                row_cells[1].text = f"Image error: {str(e)}"
                QgsMessageLog.logMessage(f"Error exporting image for label {label}: {str(e)}", "ABEI GIS", Qgis.Warning)
            finally:
                try:
                    os.remove(temp_img_path)
                except:
                    pass

    def create_word_document(self, grouped_by_theme):
        """
        Crée l'intégralité du document Word à partir des données d'analyse.

        - Ajoute entête et pied de page
        - Génère les sections d’information générale
        - Génère les sections thématiques (groupées et individuelles)
        - Sauvegarde le fichier .docx dans le répertoire spécifié

        :param grouped_by_theme: Dictionnaire de thèmes avec entités associées
        :return: Chemin complet vers le fichier Word généré
        """
        doc = Document()

        self._add_header(doc)
        self._add_footer(doc)

        title = doc.add_heading(Config.FC_WORD_TITLE_TEXT, level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        self._add_general_info(doc)
        self._add_global_feasible_restriction_map(doc)
        doc.add_paragraph()

        doc.add_heading("[GIS analysis] Strict restrictions - Grouped by theme", level=1)
        for theme_value, feats in grouped_by_theme.items():
            display_name = Config.get_display_name(theme_value)
            # Ajout du nombre de restrictions dans le titre
            self._add_theme_section(doc, display_name, feats, grouped=True)
    
            
        # Section Individual
        doc.add_heading("[GIS analysis] Strict restrictions - Individual detail", level=1)
        for theme_value, feats in grouped_by_theme.items():
            display_name = Config.get_display_name(theme_value)
            # On passe grouped=False pour avoir une ligne par label
            self._add_theme_section(doc, display_name, feats, grouped=False)
        

        doc_path = os.path.join(self.report_directory, f"[Vmap-Report]{Config.get_analyse_type()}{self.layer_manager.analysis_data['technology']}={self.layer_manager.analysis_label}.docx")
        doc.save(doc_path)
        QgsMessageLog.logMessage(f"Word document created: {doc_path}", "[Abei GIS] Report helper", Qgis.Success)
        return doc_path
