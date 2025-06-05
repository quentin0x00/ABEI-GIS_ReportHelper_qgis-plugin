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
        Header compact avec :
        - Logo à gauche
        - Texte à droite
        - Hauteur minimale (celle du logo)
        - Centrage vertical du texte
        - Espace après le header
        """
        section = doc.sections[0]
        header = section.header

        # Réduire la distance entre le haut de la page et le header
        section.header_distance = Inches(0.2)  # Plus compact
        
        # Un seul paragraphe pour tout le header
        header_para = header.paragraphs[0]

        # Logo à gauche (taille ajustée)
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo_run = header_para.add_run()
                logo_run.add_picture(self.logo_path, width=Inches(0.8))  # Logo plus lisible
            except:
                header_para.add_run("LOGO").bold = True

        # Texte à droite du logo (avec espaces)
        text_run = header_para.add_run("              " + f"{Config.FOOTER_MIDDLE_TEXT} - {self.layer_manager.analysis_label}")
        text_run.bold = True
        text_run.font.size = Pt(10)

        # Alignement à gauche pour tout garder ensemble
        header_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Centrage vertical du texte dans le header - méthode simplifiée
        header_para.paragraph_format.space_before = Pt(6)  # Espacement avant pour centrer
        header_para.paragraph_format.space_after = Pt(12)  # Espace après le contenu du header
        header_para.paragraph_format.line_spacing = 1
        
        # Ajouter un paragraphe vide supplémentaire dans le header pour plus d'espace
        empty_para = header.add_paragraph()
        empty_para.paragraph_format.space_after = Pt(6)  # Espace supplémentaire
        
        # Ajuster la hauteur du header pour un meilleur centrage
        section.header_distance = Inches(0.15)
        
    def _add_footer(self, doc):
        """
        Ajoute la pagination automatique en bas à droite
        """
        section = doc.sections[0]
        footer = section.footer
        paragraph = footer.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Ajout du champ de numérotation automatique
        run = paragraph.add_run()
        fldChar = parse_xml(r'<w:fldChar {} w:fldCharType="begin"/>'.format(nsdecls('w')))
        run._r.append(fldChar)
        
        instrText = parse_xml(r'<w:instrText {} xml:space="preserve">PAGE</w:instrText>'.format(nsdecls('w')))
        run._r.append(instrText)
        
        fldChar = parse_xml(r'<w:fldChar {} w:fldCharType="end"/>'.format(nsdecls('w')))
        run._r.append(fldChar)

    def _add_general_info(self, doc):
        """
        Ajoute une section avec les informations générales sur le projet.
        """
        # Ajouter un tableau avec 10 lignes et 3 colonnes
        info_table = doc.add_table(rows=10, cols=3)
        info_table.style = 'Table Grid'
        info_table.autofit = False

        # Set the widths of the columns
        # Reduce the width of the first two columns and increase the width of the image column
        # Définir les largeurs des colonnes (total = 9.5 pouces pour correspondre à la marge)
        info_table.columns[0].width = Inches(1.5)  # Première colonne
        info_table.columns[1].width = Inches(1.5)  # Deuxième colonne
        info_table.columns[2].width = Inches(8)  # Colonne pour l'image

        # Forcer l'application des largeurs
        for row in info_table.rows:
            for idx, cell in enumerate(row.cells):
                cell.width = info_table.columns[idx].width

        # Merge cells of the first row for the "SUMMARY" title
        summary_cell = info_table.cell(0, 0).merge(info_table.cell(0, 1))
        summary_cell.text = "SUMMARY"
        summary_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        summary_cell.paragraphs[0].runs[0].bold = True

        # Appliquer le style gris - version corrigée
        tcPr = summary_cell._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), "D9D9D9")
        tcPr.append(shd)

        # Apply a gray background to the "SUMMARY" cell
        shading_elm = parse_xml(r'<w:shd {} w:fill="D9D9D9"/>'.format(nsdecls('w')))

        # Add data to the first two columns
        data = [
            ("NAME", self.layer_manager.analysis_label),
            ("COUNTRY", "Poland"),
            ("VOIVODESHIP (WOJEWODZTWO)", ""),
            ("COUNTY (POWIAT)", ""),
            ("COMMUNE (GMINA)", ""),
            ("TECHNOLOGY", self.layer_manager.analysis_data['technology']),
            ("DATE SENT", QDateTime.currentDateTime().toString("dd/MM/yyyy"))
        ]

        for i, (label, value) in enumerate(data, start=1):
            info_table.cell(i, 0).text = label
            info_table.cell(i, 1).text = str(value)

        # Add the "KEY ISSUES" row merged over the first two columns
        key_issues_cell = info_table.cell(8, 0).merge(info_table.cell(8, 1))
        key_issues_cell.text = "KEY ISSUES"
        key_issues_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        key_issues_cell.paragraphs[0].runs[0].bold = True

        # Apply a gray background to the "KEY ISSUES" cell
        key_issues_cell._tc.get_or_add_tcPr().append(shading_elm)

        # Merge cells of the last row for an empty cell that spans the remaining height
        empty_cell = info_table.cell(9, 0).merge(info_table.cell(9, 1))
        empty_cell.text = ""

        # Merge cells in the image column to span the full height
        for i in range(1, 10):
            current_cell = info_table.cell(i, 2)
            current_cell.merge(info_table.cell(i-1, 2))

        # Add the image to the third column
        image_cell = info_table.cell(0, 2)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_img_path = temp_file.name

        try:
            # Export the image
            self.image_exporter.export_image(self.layer_manager.analysis_extent, temp_img_path, 'null')

            # Add the image to the cell
            image_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            image_cell.paragraphs[0].add_run().add_picture(temp_img_path, width=Inches(7.0))
        except Exception as e:
            image_cell.text = f"Erreur : {str(e)}"
            QgsMessageLog.logMessage(f"Erreur export image : {str(e)}", "ABEI GIS", Qgis.Warning)
        finally:
            try:
                os.remove(temp_img_path)
            except:
                pass


    def _add_theme_section(self, doc, theme_name, feats, grouped=True):
        """
        Ajoute une section thématique au rapport dans un tableau :
        - Ligne titre "ENVIRONMENTAL RESTRICTIONS..."
        - Nom du thème dans la colonne "Name"
        - Image + notes
        """
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        # Ajustement des largeurs des colonnes
        table.columns[0].width = Inches(1.1)  # 10% de la largeur totale
        table.columns[1].width = Inches(6.6)  # 60% de la largeur totale
        table.columns[2].width = Inches(3.3)  # 30% de la largeur totale

        # Ligne fusionnée pour le titre du tableau
        title_row = table.rows[0]
        title_cell = title_row.cells[0].merge(title_row.cells[1])
        title_cell = title_cell.merge(title_row.cells[2])
        title_cell.text = "ENVIRONMENTAL RESTRICTIONS"
        title_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_cell.paragraphs[0].runs[0].bold = True
        shading_elm = parse_xml(r'<w:shd {} w:fill="D9D9D9"/>'.format(nsdecls('w')))
        title_cell._tc.get_or_add_tcPr().append(shading_elm)

        # En-têtes
        hdr_cells = table.add_row().cells
        hdr_cells[0].text = 'NAME'
        hdr_cells[1].text = 'MAP/DESCRIPTION'
        hdr_cells[2].text = 'COMMENTS'
        
        for cell in hdr_cells:
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        if grouped:
            self._add_grouped_theme_content(table, feats)
        else:
            pass  # Cas non groupé non implémenté ici

        doc.add_paragraph()
        
    def _add_grouped_theme_content(self, table, feats):
        """
        Ajoute une ligne au tableau avec tous les labels regroupés d'un thème.
        """
        row_cells = table.add_row().cells

        theme_str = str(feats[0]['theme']).strip()
        display_name = Config.get_display_name(theme_str)
        row_cells[0].text = display_name  # Juste le nom du thème

        theme_str = str(feats[0]['theme']).strip()
        subset = (f'"{self.restri_join_id_field}" = \'{self.layer_manager.analysis_id}\' '
                 f'AND "type_restriction" = \'{self.type_restri_strict}\' '
                 f'AND "theme" = \'{theme_str}\'')

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_img_path = temp_file.name

        self.image_exporter.export_image(self.layer_manager.analysis_extent, temp_img_path, subset)

        try:
            row_cells[1].paragraphs[0].add_run().add_picture(temp_img_path, width=Inches(7.0))
        except Exception as e:
            row_cells[1].text = f"Error loading image: {str(e)}"
            QgsMessageLog.logMessage(f"Error loading image: {str(e)}", "ABEI GIS", Qgis.Warning)
        finally:
            try:
                os.remove(temp_img_path)
            except:
                pass

    def create_word_document(self, grouped_by_theme):
        """
        Crée le document Word en orientation paysage
        """
        doc = Document()
        
        # Configuration de la page en paysage
        section = doc.sections[0]
        section.orientation = WD_ORIENTATION.LANDSCAPE
        section.page_width = Inches(11.69)  # A4 landscape
        section.page_height = Inches(8.27)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.header_distance = Inches(0.3)
        section.footer_distance = Inches(0.3)

        self._add_header(doc)
        self._add_footer(doc)

        # Ajout des informations générales
        self._add_general_info(doc)
        
        # Saut de page après les informations générales
        doc.add_page_break()

        # Ajout des sections thématiques
        theme_items = list(grouped_by_theme.items())
        for index, (theme_value, feats) in enumerate(theme_items):
            display_name = Config.get_display_name(theme_value)
            self._add_theme_section(doc, display_name, feats, grouped=True)
            
            # Saut de page après chaque section thématique, SAUF pour la dernière
            if index < len(theme_items) - 1:
                doc.add_page_break()
        
        doc_path = os.path.join(self.report_directory, f"[Vmap-Report]{Config.get_analyse_type()}{self.layer_manager.analysis_data['technology']}={self.layer_manager.analysis_label}.docx")
        doc.save(doc_path)
        return doc_path