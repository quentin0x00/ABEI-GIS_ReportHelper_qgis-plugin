from .imports import *

class FCReportGeneratorPlugin:
    """Plugin QGIS pour générer des rapports FC"""

    def __init__(self, iface):
        """
        Initialisation du plugin.

        - Récupère l'interface de QGIS
        - Prépare la traduction si disponible
        - Initialise la barre d'outils et le menu du plugin
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        icons_path = os.path.join(self.plugin_dir, 'icons')
        if icons_path not in sys.path:
            sys.path.insert(0, icons_path)

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FCReportGenerator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr('&[Abei GIS] Report helper')
        self.toolbar = self.iface.addToolBar('[Abei GIS] Report helper')
        self.toolbar.setObjectName('FCReportGenerator')

    def tr(self, message):
        """
        Fonction utilitaire pour traduire une chaîne de caractères.
        """
        return QCoreApplication.translate('FCReportGenerator', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """
        Ajoute une action (bouton) au plugin.

        - icon_path : chemin vers l'icône
        - text : texte affiché
        - callback : fonction appelée au clic
        - enabled_flag : bouton actif ou non
        - add_to_menu : ajouter au menu QGIS
        - add_to_toolbar : ajouter à la barre d'outils
        - status_tip, whats_this : infos bulle d’aide
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self):
        """
        Initialise l’interface graphique du plugin.

        - Ajoute l'action dans la barre d'outils et le menu
        """
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr('[Abei GIS] Report helper'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """
        Supprime l’interface graphique du plugin.

        - Retire les actions du menu et de la barre d’outils
        """
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr('&[Abei GIS] Report helper'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        """
        Affiche le panneau latéral (dock) du plugin.

        - Instancie et affiche le widget dockable
        - Le place à gauche de l’interface QGIS
        - Gère les erreurs via une boîte de dialogue
        """
        try:
            from .ui.dock_widget import FCReportDock

            if not hasattr(self, 'dock_widget'):
                self.dock_widget = FCReportDock(self, self.iface.mainWindow())
                self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

            self.dock_widget.show()
            self.dock_widget.raise_()
            self.dock_widget.activateWindow()

        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), "Erreur", str(e))
