from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QMessageBox, QFileDialog)
from PyQt6.QtGui import QIcon, QAction
import sys
import os

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg  # Note: 'qtagg' not 'qt5agg'

# Import pages
from pages.home_page import HomePage
from pages.PnL_page import PnLPage
from pages.SensAN_page import SensANPage
from pages.simul_page import SimulationPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BSM Option Pricing Model")
        self.setWindowIcon(QIcon('Abstract_icon.png'))
        self.resize(1200, 800)  # Wider window for side-by-side heatmaps
        #self.showFullScreen() #True full screen
        # Apply dark theme

#        # Main container
#        central_widget = QWidget()
#        self.setCentralWidget(central_widget)

        # Main layout
#        main_layout = QVBoxLayout(central_widget)
#        main_layout.setContentsMargins(15, 15, 15, 15)
#        main_layout.setSpacing(15)
        # Central widget with stacked layout
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Initialize pages
        self.pages = {
            "home": HomePage(),
            "PnL analysis": PnLPage(),
            "sensitivity analysis": SensANPage(),
            "simulation hub": SimulationPage()
        }

        # Add pages to stacked widget
        for name, page in self.pages.items():
            self.central_widget.addWidget(page)

        # Create menu bar
        self.create_menu_bar()

        # Show home page by default
        self.switch_page("home")

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

#        new_action = QAction("New", self)
#        file_menu.addAction(new_action)

        import_action = QAction("Import", self)
        import_action.triggered.connect(self.imprt)
        file_menu.addAction(import_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Pages Menu
        pages_menu = menubar.addMenu("Pages")

        home_action = QAction("Home", self)
        home_action.triggered.connect(lambda: self.switch_page("home"))
        pages_menu.addAction(home_action)

        pnl_page_action = QAction("PnL analysis", self)
        pnl_page_action.triggered.connect(lambda: self.switch_page("PnL analysis"))
        pages_menu.addAction(pnl_page_action)

        sens_analysis_action = QAction("sensitivity analysis", self)
        sens_analysis_action.triggered.connect(lambda: self.switch_page("sensitivity analysis"))
        pages_menu.addAction(sens_analysis_action)

        sens_analysis_action = QAction("simulator", self)
        sens_analysis_action.triggered.connect(lambda: self.switch_page("simulation hub"))
        pages_menu.addAction(sens_analysis_action)

    def switch_page(self, page_name):
        if page_name in self.pages:
            self.central_widget.setCurrentWidget(self.pages[page_name])
            self.setWindowTitle(f"Options Trading - {page_name.capitalize()}")
        else:
            QMessageBox.warning(self, "Error", "Page not found!")

    def imprt(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Data File",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                file_name = os.path.basename(file_path)
                QMessageBox.information(self, "File Imported", f"Successfully imported: {file_name}")

                # TODO: Load file into memory / pass to relevant page
                print(f"Imported file path: {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Abstract_icon.png"))
    app.setStyle("Fusion")

    # Ensure assets directory exists
#    if not os.path.exists('assets'):
#        os.makedirs('assets')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# Faner: simulation 1, simulation 2,
# save img button, solve opening fullscreen problems, taskbar icon not showing
# make a start loading page
# add option-probability-distribution