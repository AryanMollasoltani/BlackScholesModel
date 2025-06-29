from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QDoubleSpinBox, QLabel, QFormLayout,
                             QLineEdit, QFrame, QHBoxLayout, QButtonGroup, QPushButton)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from superqt import QDoubleRangeSlider
import main
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PnLPage(QWidget):
    def __init__(self):
        super().__init__()
        # Main layout with two columns
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.main_layout)

        # Left column (will contain inputs and slider)
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Right column (will contain results and graph)
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Add columns to main layout
        self.main_layout.addWidget(left_column, stretch=2)  # Left column takes 2/3 space
        self.main_layout.addWidget(right_column, stretch=1)  # Right column takes 1/3 space

        # --- LEFT COLUMN CONTENTS ---
        # Inputs frame
        inputs_frame = QFrame()
        inputs_frame.setStyleSheet("background: #2D2D2D; border-radius: 5px;")
        inputs_layout = QVBoxLayout(inputs_frame)
        inputs_layout.setContentsMargins(10, 10, 10, 10)
        inputs_layout.setSpacing(8)

        title_label = QLabel("Model Inputs")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
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

        for spinbox in self.model_inputs:
            spinbox.setMinimumWidth(120)

        inputs_layout.addLayout(inputs_row)
        left_layout.addWidget(inputs_frame)

        # Results frame
        results_frame = QFrame()
        results_frame.setStyleSheet("background: #2D2D2D; border-radius: 5px;")
        results_layout = QVBoxLayout(results_frame)
        results_layout.setContentsMargins(15, 10, 15, 10)
        results_layout.setSpacing(8)

        # Add option buttons
        self.graph_options = QButtonGroup()
        call_btn = QPushButton("Call")
        put_btn = QPushButton("Put")
        call_btn.setCheckable(True)
        put_btn.setCheckable(True)

        self.graph_options = QButtonGroup()
        self.graph_options.addButton(call_btn, 0)  # ID 0 for call
        self.graph_options.addButton(put_btn, 1)  # ID 1 for put
        call_btn.setChecked(True)  # Default to call

        # Style the buttons
        button_style = """
                    QPushButton {
                        background: #3E3E3E;
                        color: white;
                        border: 1px solid #555;
                        padding: 3px;
                        min-width: 60px;
                    }
                    QPushButton:checked {
                        background: #00AAFF;
                        color: white;
                    }
                """
        call_btn.setStyleSheet(button_style)
        put_btn.setStyleSheet(button_style.replace("00AAFF", "FF5555"))

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(call_btn)
        btn_layout.addWidget(put_btn)
        results_layout.addLayout(btn_layout)

        # Call Price Display
        call_container = QVBoxLayout()
        call_container.setSpacing(5)
        self.call_label = QLabel("Call Price")
        self.call_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))  # Smaller font
        self.call_label.setStyleSheet("color: #FFFFFF;")
        self.call_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.call_price = QLineEdit("0.00")
        self.call_price.setReadOnly(True)
        self.call_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.call_price.setMinimumWidth(150)
        self.call_price.setStyleSheet("""
                    QLineEdit {
                        font: bold 16px 'Arial';
                        color: #00AAFF;
                        background: #003350;
                        border: 2px solid #0077AA;
                        border-radius: 5px;
                        padding: 6px;
                        min-height: 28px;
                    }
                """)

        call_container.addWidget(self.call_label)
        call_container.addWidget(self.call_price)
        results_layout.addLayout(call_container)

        # Put Price Display
        put_container = QVBoxLayout()
        put_container.setSpacing(5)
        self.put_label = QLabel("Put Price")
        self.put_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))  # Smaller font
        self.put_label.setStyleSheet("color: #FFFFFF;")
        self.put_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.put_price = QLineEdit("0.00")
        self.put_price.setReadOnly(True)
        self.put_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.put_price.setMinimumWidth(150)
        self.put_price.setStyleSheet("""
                    QLineEdit {
                        font: bold 16px 'Arial';
                        color: #FF5555;
                        background: #500000;
                        border: 2px solid #AA0000;
                        border-radius: 5px;
                        padding: 6px;
                        min-height: 28px;
                    }
                """)

        put_container.addWidget(self.put_label)
        put_container.addWidget(self.put_price)
        results_layout.addLayout(put_container)

        right_layout.addWidget(results_frame)

        # Slider
        slider_container = QWidget()
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setContentsMargins(0, 5, 0, 5)
        slider_layout.setSpacing(5)

        # Add title label
        slider_title = QLabel("Market Price Range at Expiry")
        slider_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        slider_title.setStyleSheet("color: #FFFFFF;")
        slider_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider_layout.addWidget(slider_title)

        # Initialize slider with default values
        self.slider = QDoubleRangeSlider(Qt.Orientation.Horizontal)
        self.slider.setStyleSheet("""
                    QSlider::handle:horizontal {
                        background: #00AAFF;
                        width: 12px;
                        height: 12px;
                        margin: -6px 0;
                        border-radius: 6px;
                    }
                """)

        # Create value display widgets
        self.value_display = QWidget()
        value_layout = QHBoxLayout(self.value_display)
        value_layout.setContentsMargins(0, 5, 0, 0)

        # Min value label
        self.min_value_label = QLabel()
        self.min_value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.min_value_label.setStyleSheet("""
                    QLabel {
                        color: #00AAFF;
                        font: bold 9px;
                        min-width: 80px;
                    }
                """)

        # Current range label
        self.range_label = QLabel()
        self.range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.range_label.setStyleSheet("""
                    QLabel {
                        color: #FFFFFF;
                        font: bold 9px;
                    }
                """)

        # Max value label
        self.max_value_label = QLabel()
        self.max_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.max_value_label.setStyleSheet("""
                    QLabel {
                        color: #00AAFF;
                        font: bold 9px;
                        min-width: 80px;
                    }
                """)

        value_layout.addWidget(self.min_value_label)
        value_layout.addWidget(self.range_label)
        value_layout.addWidget(self.max_value_label)

        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.value_display)
        left_layout.addWidget(slider_container)
        left_layout.addStretch()

        # Connect signals
        self.slider.valueChanged.connect(self.update_slider_labels)

        # Right container setup
        right_graph_container = QFrame()
        right_graph_container.setStyleSheet("background: #2D2D2D; border-radius: 5px;")
        right_graph_layout = QVBoxLayout(right_graph_container)
        right_graph_layout.setContentsMargins(10, 10, 10, 10)
        right_graph_layout.setSpacing(15)

        # Title
        title_label = QLabel("Practical Calculator")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        right_graph_layout.addWidget(title_label)

        # Input Fields Layout
        input_form = QFormLayout()
        input_form.setLabelAlignment(Qt.AlignLeft)
        input_form.setFormAlignment(Qt.AlignTop)
        input_form.setVerticalSpacing(10)

        # Market Maker Quote input
        self.quote_input = QLineEdit()
        self.quote_input.setStyleSheet(
            "background-color: #3A3A3A; color: white; border: 1px solid #555555; padding: 5px;")
        input_form.addRow("Market Maker Quote:", self.quote_input)

        # Market Price at Expiry input
        self.expiry_input = QLineEdit()
        self.expiry_input.setStyleSheet(
            "background-color: #3A3A3A; color: white; border: 1px solid #555555; padding: 5px;")
        input_form.addRow("Market Price at Expiry:", self.expiry_input)

        right_graph_layout.addLayout(input_form)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                padding: 8px;
                border: 1px solid #666;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        right_graph_layout.addWidget(self.calculate_button)

        # Result Fields Layout
        result_form = QFormLayout()
        result_form.setLabelAlignment(Qt.AlignLeft)
        result_form.setFormAlignment(Qt.AlignTop)
        result_form.setVerticalSpacing(10)

        # Labels for results
        self.call_pnl_value = QLabel("-")
        self.put_pnl_value = QLabel("-")
        self.call_edge_value = QLabel("-")
        self.put_edge_value = QLabel("-")

        # Styling for value labels
        for val_label in [self.call_pnl_value, self.put_pnl_value, self.call_edge_value, self.put_edge_value]:
            val_label.setStyleSheet("color: white; font-size: 14px;")

        # Add result label rows
        result_form.addRow("Call PnL:", self.call_pnl_value)
        result_form.addRow("Put PnL:", self.put_pnl_value)
        result_form.addRow("Call Trade Edge:", self.call_edge_value)
        result_form.addRow("Put Trade Edge:", self.put_edge_value)

        right_graph_layout.addLayout(result_form)
        self.calculate_button.clicked.connect(self.update_custom_metrics)
        # Add to layout
        right_layout.addWidget(right_graph_container)

        # Left Graph Frame
        left_graph_container = QFrame()
        left_graph_container.setStyleSheet("background: #2D2D2D; border-radius: 5px;")
        left_graph_layout = QVBoxLayout(left_graph_container)
        left_graph_layout.setContentsMargins(5, 5, 5, 5)

        # Create left figure and canvas
        self.left_figure = Figure(figsize=(5, 3), dpi=100)
        self.left_canvas = FigureCanvas(self.left_figure)
        self.left_ax = self.left_figure.add_subplot(111)

        # Set dark theme for the plot
        self.left_figure.patch.set_facecolor('#2D2D2D')
        self.left_ax.set_facecolor('#2D2D2D')
        self.left_ax.tick_params(colors='white')
        self.left_ax.xaxis.label.set_color('white')
        self.left_ax.yaxis.label.set_color('white')
        self.left_ax.title.set_color('white')

        for spine in self.left_ax.spines.values():
            spine.set_edgecolor('#555555')

        left_graph_layout.addWidget(self.left_canvas)
        left_layout.addWidget(left_graph_container, stretch=1)  # Takes remaining space

#        self.slider.valueChanged.connect(self.plot_call)
        self.slider.valueChanged.connect(self.update_active_plot)

        # Initialize slider values
        self.update_slider_range()

        # Connect button signals
        call_btn.clicked.connect(self.plot_call)
        put_btn.clicked.connect(self.plot_put)

    def update_custom_metrics(self):
        quote = float(self.quote_input.text())
        expiry = float(self.expiry_input.text())

        S = self.model_inputs[0].value()  # Underlying
        K = self.model_inputs[1].value()  # Strike
        sigma = self.model_inputs[2].value()  # Volatility (decimal)
        r = self.model_inputs[3].value()  # Interest rate (decimal)
        T = self.model_inputs[4].value()  # Time

        Model = main.BlackScholesModel(S, K, sigma, r, T)
        c_pnl_val = Model.prac_call_pnl(quote, expiry)
        p_pnl_val = Model.prac_put_pnl(quote, expiry)
        c_edge = Model.call_trade_edge(quote)
        p_edge = Model.put_trade_edge(quote)

        # Replace this with your own calculation logic
        self.call_pnl_value.setText(f"{c_pnl_val:.2f}")
        self.put_pnl_value.setText(f"{p_pnl_val:.2f}")
        self.call_edge_value.setText(f"{c_edge:.2f}")
        self.put_edge_value.setText(f"{p_edge:.2f}")

    def update_active_plot(self):
        """Handle slider changes by updating the correct plot"""
        if self.graph_options.checkedId() == 0:  # Call is selected
            self.plot_call()
        else:  # Put is selected
            self.plot_put()

    def update_slider_range(self):
        """Update slider range based on current underlying price"""
        S = self.model_inputs[0].value()

        slide_r_min = max(0.01, S * 0.6)
        slide_r_max = S * 1.4

        self.slider.setRange(slide_r_min, slide_r_max)
        self.slider.setValue((S * 0.8, S * 1.2))
        self.update_slider_labels(self.slider.value())

    def update_slider_labels(self, values):
        """Update all slider-related labels"""
        min_val, max_val = values
        range_size = max_val - min_val

        self.min_value_label.setText(f"Min: {min_val:.2f}")
        self.max_value_label.setText(f"Max: {max_val:.2f}")
        self.range_label.setText(f"Range: {range_size:.2f}")

    def calculate_bsm(self):
        S = self.model_inputs[0].value()  # Underlying
        K = self.model_inputs[1].value()  # Strike
        sigma = self.model_inputs[2].value()  # Volatility (decimal)
        r = self.model_inputs[3].value()  # Interest rate (decimal)
        T = self.model_inputs[4].value()  # Time

        Model = main.BlackScholesModel(S, K, sigma, r, T)
        self.call_price.setText(f"{Model.c_p:.2f}")
        self.put_price.setText(f"{Model.p_p:.2f}")

        self.update_slider_range()
        self.plot_call()

    def plot_call(self):
        """Plot and update call option P&L heatmap"""
        self.left_ax.clear()
        # Add your call option plotting logic here
        self.left_ax.set_title('Call Option P&L', color='white')
        try:
            # Get current parameters
            S = self.model_inputs[0].value()
            K = self.model_inputs[1].value()
            sigma = self.model_inputs[2].value()
            r = self.model_inputs[3].value()
            T = self.model_inputs[4].value()

            # Get heatmap data from model
            Model = main.BlackScholesModel(S, K, sigma, r, T)
            min_value = self.slider.value()[0]
            max_value = self.slider.value()[1]
            xc_vals, yc_vals, call_prices, put_prices = Model.theo_pnl_chart(size=8, min_mp=min_value, max_mp=max_value)

            xc_vals = np.round(xc_vals, decimals=2)
            yc_vals = np.round(yc_vals, decimals=2)
            call_prices = np.round(call_prices, decimals=2)
            # Plot Call Prices
            self.left_figure.clear()
            left_ax = self.left_figure.add_subplot()
            c1 = left_ax.imshow(call_prices, cmap='RdYlGn')
            self.left_figure.colorbar(c1, ax=left_ax)
            left_ax.set_title('Call Option Theoretical P&L', color='white', pad=20)
            left_ax.set_xlabel('Expiry Price range', color='white')
            left_ax.set_ylabel('Volatility', color='white')
            left_ax.tick_params(colors='white')
            left_ax.set_facecolor('#3E3E3E')
            left_ax.set_xticks(range(len(xc_vals)), labels=xc_vals)
            left_ax.set_yticks(range(len(yc_vals)), labels=yc_vals)

            for i in range(len(xc_vals)):
                for j in range(len(yc_vals)):
                    left_ax.text(j, i, call_prices[i, j], ha="center", va="center", color="black")

            self.left_canvas.draw()

        except Exception as e:
            print(f"Heatmap error: {e}")

    def plot_put(self):
        """Plot put option P&L diagram"""
        self.left_ax.clear()
        # Add your put option plotting logic here
        self.left_ax.set_title("Put Option Theoretical P&L", color='white')
        try:
            # Get current parameters
            S = self.model_inputs[0].value()
            K = self.model_inputs[1].value()
            sigma = self.model_inputs[2].value()
            r = self.model_inputs[3].value()
            T = self.model_inputs[4].value()

            # Get heatmap data from model
            Model = main.BlackScholesModel(S, K, sigma, r, T)
            min_value = self.slider.value()[0]
            max_value = self.slider.value()[1]
            xc_vals, yc_vals, call_prices, put_prices = Model.theo_pnl_chart(size=8, min_mp=min_value, max_mp=max_value)

            xc_vals = np.round(xc_vals, decimals=2)
            yc_vals = np.round(yc_vals, decimals=2)
            call_prices = np.round(put_prices, decimals=2)
            # Plot Call Prices
            self.left_figure.clear()
            left_ax = self.left_figure.add_subplot()
            c1 = left_ax.imshow(call_prices, cmap='RdYlGn')
            self.left_figure.colorbar(c1, ax=left_ax)
            left_ax.set_title('Put Option P&L', color='white', pad=20)
            left_ax.set_xlabel('Expiry Price range', color='white')
            left_ax.set_ylabel('Volatility', color='white')
            left_ax.tick_params(colors='white')
            left_ax.set_facecolor('#3E3E3E')
            left_ax.set_xticks(range(len(xc_vals)), labels=xc_vals)
            left_ax.set_yticks(range(len(yc_vals)), labels=yc_vals)

            for i in range(len(xc_vals)):
                for j in range(len(yc_vals)):
                    left_ax.text(j, i, call_prices[i, j], ha="center", va="center", color="black")

            self.left_canvas.draw()

        except Exception as e:
            print(f"Heatmap error: {e}")