# -*- coding: utf-8 -*-
"""
/***************************************************************************
 [ABEI GIS]Report-Helper
                                 A QGIS plugin
 Generates reports, screenshots and kml for First Check analysis
                             -------------------
        Begin                : 2025-05-17
        Copyright            : (C) 2025 by ABEI Energy
        Email                : quentinrouquette@abeienergy.com
 ***************************************************************************/

/***************************************************************************
                                                                          
    This plugin generates a Word document for the First Check analysis,   
    including screenshots of individual restrictions and grouped          
    restrictions by theme.                                                
                                                                          
    It also exports all individual and grouped restrictions to KML        
    format, along with feasible areas and the global area of interest.    
                                                                          
    Note: This plugin relies on our dedicated QGIS projects protected     
    by VPN and database authentication. It will not function              
    outside of this environment. 
    The config file has been hidden from the git repository.
                                                                          
 ***************************************************************************/
"""

def classFactory(iface):
    """
    Appellé par QGIS, renvoie une instance du plugin.
    """
    from .plugin import FCReportGeneratorPlugin
    return FCReportGeneratorPlugin(iface)
