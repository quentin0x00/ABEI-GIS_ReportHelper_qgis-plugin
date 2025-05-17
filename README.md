# [ABEI GIS] Report-Helper

**A QGIS Plugin to generate Word reports, screenshots and kml for First Check environmental analysis.**

- **Generate Word reports**  
  Includes screenshots of individual restrictions and theme-grouped restrictions in a Word documents, formated in table displaying details of the restrictions.

- **Export to KML**  
  Exports all individual and theme-grouped restrictions, along with feasible areas and the global area of the analysis.




**Note:**  
This plugin relies on our dedicated QGIS projects and layers protected by vpn and database authentication. It will not function outside of this environment.
The config file has been hidden from the project.


## Project Information

- **Start Date:** May 17, 2025  
- **Author:** Quentin Rouquette  
- **Company:** ABEI Energy  
- **Email:** [quentinrouquette@abeienergy.com](mailto:quentinrouquette@abeienergy.com)


## Installation

This plugin is for internal use only and is not available via the QGIS Plugin Repository. It can only be installed as a ZIP plugin, which we provide internally.


### Prerequisites

Before installing the plugin, you need to ensure that the `python-docx` library is installed. This library is required for the plugin to function properly.

- If you are installing the plugin with the provided ZIP file, the `python-docx` library has already been included. However, if you need to install it manually, use the following command:

    ```bash
    pip install python-docx --target=./lib
    ```

    This will install the library in the `./lib` directory to make it easier for users to install.

- Alternatively, if users dont mind running a command line, use this:

    ```bash
    "C:\Program Files\QGIS 3.42.0\apps\Python312\python.exe" -m pip install python-docx
    ```

### Plugin Installation

To install the plugin, follow these steps:

1. Download the provided ZIP file containing the plugin.
2. In QGIS, go to `Plugins` > `Manage and Install Plugins`.
3. Click on the `Install from ZIP` button.
4. Select the downloaded ZIP file and install the plugin.

Once installed, the plugin will be available for use in QGIS.
