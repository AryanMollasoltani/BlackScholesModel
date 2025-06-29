from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SimulationPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)