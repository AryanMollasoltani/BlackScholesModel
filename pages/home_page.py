from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QDoubleSpinBox, QLabel, QLineEdit, QFrame, QSlider)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
import sys

import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt6 backend for PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg  # Note: 'qtagg' not 'qt5agg'
from matplotlib.figure import Figure
import numpy as np
import main


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.set_dark_theme()

#        self.label = QLabel("Welcome to the Home Page")
#        self.label.setStyleSheet("font-size: 24px; font-weight: bold;")
#        self.layout.addWidget(self.label)

        inputs_frame = QFrame()
        inputs_frame.setStyleSheet("background: #2D2D2D; border-radius: 5px;")
        inputs_layout = QVBoxLayout(inputs_frame)
        inputs_layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel("Model Inputs")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFFFFF;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inputs_layout.addWidget(title_label)

        input_specs = [
            ("Underlying price:", 0.01, 10000.00, 100.00, 2),  # 2 decimals
            ("Strike price:", 0.01, 10000.00, 100.00, 2),  # 2 decimals
            ("Volatility:", 0.0000, 2.0000, 0.2000, 4),  # 4 decimals
            ("Interest rate:", -0.0500, 0.2000, 0.0300, 4),  # 4 decimals
            ("Time to expiration:", 0.01, 50.00, 1.00, 2)  # 2 decimals
        ]

        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(15)

        self.model_inputs = []
        for label, min_val, max_val, default, decimals in input_specs:
            spinbox = QDoubleSpinBox()
            spinbox.setPrefix(f"{label} ")
            spinbox.setDecimals(decimals)  # Use specified decimal places
            spinbox.setSingleStep(0.01 if decimals == 2 else 0.0001)  # Adjust step size
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default)
            spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)
            spinbox.setMinimumWidth(140)
            spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)
            spinbox.setStyleSheet("""
                QDoubleSpinBox {
                    background: #3E3E3E;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    padding: 5px;
                }
            """)

            self.model_inputs.append(spinbox)
            inputs_row.addWidget(spinbox)
            spinbox.valueChanged.connect(self.calculate_bsm)

        inputs_layout.addLayout(inputs_row)
        self.layout.addWidget(inputs_frame)

        # Results section (same as before)
        results_frame = QFrame()
        results_frame.setStyleSheet("background: #2D2D2D; border-radius: 5px;")
        results_layout = QHBoxLayout(results_frame)
        results_layout.setContentsMargins(20, 10, 20, 10)
        results_layout.setSpacing(30)

        call_container = QVBoxLayout()
        call_label = QLabel("Call Price")
        call_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        call_label.setStyleSheet("color: #FFFFFF;")
        call_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        call_container.addWidget(call_label)

        self.call_price = QLineEdit("0.00")
        self.call_price.setReadOnly(True)
        self.call_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.call_price.setMinimumWidth(180)
        self.call_price.setStyleSheet("""
                QLineEdit {
                    font: bold 18px 'Arial';
                    color: #00AAFF;
                    background: #003350;
                    border: 2px solid #0077AA;
                    border-radius: 5px;
                    padding: 8px;
                    min-height: 32px;
                }
            """)
        call_container.addWidget(self.call_price)
        results_layout.addLayout(call_container)

        put_container = QVBoxLayout()
        put_label = QLabel("Put Price")
        put_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        put_label.setStyleSheet("color: #FFFFFF;")
        put_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        put_container.addWidget(put_label)

        self.put_price = QLineEdit("0.00")
        self.put_price.setReadOnly(True)
        self.put_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.put_price.setMinimumWidth(180)
        self.put_price.setStyleSheet("""
                QLineEdit {
                    font: bold 18px 'Arial';
                    color: #FF5555;
                    background: #500000;
                    border: 2px solid #AA0000;
                    border-radius: 5px;
                    padding: 8px;
                    min-height: 32px;
                }
            """)
        put_container.addWidget(self.put_price)
        results_layout.addLayout(put_container)

        self.layout.addWidget(results_frame)

        # Heatmap section - now side by side
        heatmap_frame = QFrame()
        heatmap_frame.setStyleSheet("background: #2D2D2D; border-radius: 5px;")
        heatmap_layout = QVBoxLayout(heatmap_frame)
        heatmap_layout.setContentsMargins(10, 10, 10, 10)

        # Header with slider
        header_layout = QHBoxLayout()

        heatmap_label = QLabel("Options Heatmaps")
        heatmap_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        heatmap_label.setStyleSheet("color: #FFFFFF;")
        header_layout.addWidget(heatmap_label)

        # Size slider
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Size:")
        slider_label.setFont(QFont("Arial", 10))
        slider_label.setStyleSheet("color: #FFFFFF;")
        slider_layout.addWidget(slider_label)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 15)
        self.size_slider.setValue(10)
        self.size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.size_slider.setTickInterval(1)
        self.size_slider.setSingleStep(1)
        self.size_slider.setStyleSheet("""
                QSlider {
                    min-width: 150px;
                }
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #555555;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    width: 12px;
                    margin: -4px 0;
                    background: #00AAFF;
                    border-radius: 6px;
                }
            """)
        slider_layout.addWidget(self.size_slider)

        self.size_value = QLabel("10")
        self.size_value.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.size_value.setStyleSheet("color: #00AAFF; min-width: 20px;")
        slider_layout.addWidget(self.size_value)

        header_layout.addStretch()
        header_layout.addLayout(slider_layout)
        heatmap_layout.addLayout(header_layout)

        # Heatmap Section
        heatmap_frame = QFrame()
        heatmap_frame.setStyleSheet("""
                        background: #2D2D2D; 
                        border-radius: 5px;
                    """)
        heatmap_layout = QVBoxLayout(heatmap_frame)
        heatmap_layout.setContentsMargins(10, 10, 10, 10)

        # Header with slider
        header_layout = QHBoxLayout()

        heatmap_label = QLabel("Options Heatmaps")
        heatmap_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        heatmap_label.setStyleSheet("color: #FFFFFF;")
        header_layout.addWidget(heatmap_label)

        # Size slider
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Size:")
        slider_label.setFont(QFont("Arial", 10))
        slider_label.setStyleSheet("color: #FFFFFF;")
        slider_layout.addWidget(slider_label)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 10)
        self.size_slider.setValue(2)
        self.size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.size_slider.setTickInterval(1)
        self.size_slider.setSingleStep(1)
        self.size_slider.setStyleSheet("""
                        QSlider {
                            min-width: 150px;
                        }
                        QSlider::groove:horizontal {
                            height: 6px;
                            background: #555555;
                            border-radius: 3px;
                        }
                        QSlider::handle:horizontal {
                            width: 12px;
                            margin: -4px 0;
                            background: #00AAFF;
                            border-radius: 6px;
                        }
                    """)
        slider_layout.addWidget(self.size_slider)

        self.size_value = QLabel("10")
        self.size_value.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.size_value.setStyleSheet("color: #00AAFF; min-width: 20px;")
        slider_layout.addWidget(self.size_value)

        header_layout.addStretch()
        header_layout.addLayout(slider_layout)
        heatmap_layout.addLayout(header_layout)

        # Side-by-side heatmaps
        heatmaps_row = QHBoxLayout()
        heatmaps_row.setSpacing(20)

        # Heatmap 1 - Call Prices
        heatmap1_container = QVBoxLayout()

        self.figure1 = Figure(facecolor='#2D2D2D')
        self.canvas1 = FigureCanvasQTAgg(self.figure1)
        self.canvas1.setStyleSheet("background-color: transparent;")
        heatmap1_container.addWidget(self.canvas1)

        # Heatmap 2 - Put Prices
        heatmap2_container = QVBoxLayout()

        self.figure2 = Figure(facecolor='#2D2D2D')
        self.canvas2 = FigureCanvasQTAgg(self.figure2)
        self.canvas2.setStyleSheet("background-color: transparent;")
        heatmap2_container.addWidget(self.canvas2)

        # Add to layout with stretch factors
        heatmaps_row.addLayout(heatmap1_container, stretch=1)
        heatmaps_row.addLayout(heatmap2_container, stretch=1)
        heatmap_layout.addLayout(heatmaps_row)

        # Add to main layout with stretch
        self.layout.addWidget(heatmap_frame, stretch=1)

        # Initial draw
        self.update_heatmaps()

        # Connections
        self.size_slider.valueChanged.connect(
            lambda value: self.size_value.setText(str(value))
        )
        self.size_slider.valueChanged.connect(self.update_heatmaps)
        for spinbox in self.model_inputs:
            spinbox.valueChanged.connect(self.update_heatmaps)

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        self.setPalette(palette)

    def calculate_bsm(self):

        S = self.model_inputs[0].value()  # Underlying
        K = self.model_inputs[1].value()  # Strike
        sigma = self.model_inputs[2].value()  # Volatility (decimal)
        r = self.model_inputs[3].value()  # Interest rate (decimal)
        T = self.model_inputs[4].value()  # Time

        Model = main.BlackScholesModel(S, K, sigma, r, T)
        self.call_price.setText(f"{Model.c_p:.2f}")
        self.put_price.setText(f"{Model.p_p:.2f}")

    def update_heatmaps(self):
        """Update heatmaps with model data"""
        try:
            # Get current parameters
            S = self.model_inputs[0].value()
            K = self.model_inputs[1].value()
            sigma = self.model_inputs[2].value()
            r = self.model_inputs[3].value()
            T = self.model_inputs[4].value()

            # Get heatmap data from model
            Model = main.BlackScholesModel(S, K, sigma, r, T)
            xc_vals, yc_vals, call_prices, put_prices = Model.cp_heatmap_val(size=self.size_slider.value())

            xc_vals = np.round(xc_vals, decimals=2)
            yc_vals = np.round(yc_vals, decimals=2)
            call_prices = np.round(call_prices, decimals=2)
            put_prices = np.round(put_prices, decimals=2)
            # Plot Call Prices
            self.figure1.clear()
            ax1 = self.figure1.add_subplot()
            c1 = ax1.imshow(call_prices)
            self.figure1.colorbar(c1, ax=ax1)
            ax1.set_title('Call Prices', color='white', pad=20)
            ax1.set_xlabel('Strike Price', color='white')
            ax1.set_ylabel('Volatility', color='white')
            ax1.tick_params(colors='white')
            ax1.set_facecolor('#3E3E3E')
            ax1.set_xticks(range(len(xc_vals)), labels=xc_vals)
            ax1.set_yticks(range(len(yc_vals)), labels=yc_vals)

            # Plot Put Prices
            self.figure2.clear()
            ax2 = self.figure2.add_subplot()
            c2 = ax2.imshow(put_prices)
            self.figure2.colorbar(c2, ax=ax2)
            ax2.set_title('Put Prices', color='white', pad=20)
            ax2.set_xlabel('Strike Price', color='white')
            ax2.set_ylabel('Volatility', color='white')
            ax2.tick_params(colors='white')
            ax2.set_facecolor('#3E3E3E')
            ax2.set_xticks(range(len(xc_vals)), labels=xc_vals)
            ax2.set_yticks(range(len(yc_vals)), labels=yc_vals)

            for i in range(len(xc_vals)):
                for j in range(len(yc_vals)):
                    ax1.text(j, i, call_prices[i, j], ha="center", va="center", color="w")
                    ax2.text(j, i, put_prices[i, j], ha="center", va="center", color="w")

            # Redraw
            self.canvas1.draw()
            self.canvas2.draw()

        except Exception as e:
            print(f"Heatmap error: {e}")