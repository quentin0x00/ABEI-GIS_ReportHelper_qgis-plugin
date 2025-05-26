import os
import sys
import re
import tempfile
from collections import defaultdict
from datetime import datetime


from qgis.core import (
    QgsProject, QgsFeatureRequest, QgsRectangle,
    QgsMapSettings, QgsMapRendererSequentialJob,
    QgsMessageLog, Qgis, QgsSettings,
    QgsFields, QgsField, QgsFeature,
    QgsVectorLayer, QgsVectorFileWriter,
    QgsCoordinateReferenceSystem, QgsWkbTypes, QgsApplication
)
from qgis.PyQt.QtCore import (
    QSize, QDateTime, QTranslator,
    QCoreApplication, QSettings, QVariant, Qt
)
from qgis.PyQt.QtGui import (
    QIcon, QPixmap, QColor, QImage, QPainter, QFont, QCursor
)
from qgis.PyQt.QtWidgets import (
    QAction, QFileDialog, QMessageBox, QDialog,
    QVBoxLayout, QLabel, QComboBox, QPushButton,
    QListWidget, QAbstractItemView, QHBoxLayout,
    QDockWidget, QWidget, QFrame, QLineEdit, QRadioButton, QTabWidget,
    QDialogButtonBox, QFormLayout, QScrollArea, QGroupBox,
    QTableWidget, QHeaderView, QTableWidgetItem, QSizePolicy
)

from qgis.utils import iface
from qgis.gui import QgsMapToolIdentifyFeature, QgsDockWidget

# > pip install python-docx --target=./lib pour faciliter l'install des utilisateurs.
#  sinon faire "C:\Program Files\QGIS 3.42.0\apps\Python312\python.exe" -m pip install python-docx
lib_path = os.path.join(os.path.dirname(__file__), 'lib')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)
from docx import Document
from docx.shared import Inches, Cm, Pt
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.section import WD_ORIENT
from docx.enum.section import WD_SECTION_START
from docx.oxml.ns import qn
from docx.oxml import OxmlElement