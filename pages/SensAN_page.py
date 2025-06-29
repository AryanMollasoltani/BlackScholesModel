from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QDoubleSpinBox, QLabel, QFormLayout,
                             QLineEdit, QFrame, QHBoxLayout, QButtonGroup, QPushButton)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt

import main
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class SensANPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.set_dark_theme()

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

        # Results section (same as before)
        results_frame = QFrame()
        results_frame.setStyleSheet("background: #2D2D2D; border-radius: 5px;")
        results_layout = QHBoxLayout(results_frame)
        results_layout.setContentsMargins(20, 10, 20, 10)
        results_layout.setSpacing(5)

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

        # === Wrap inputs and results in a compact horizontal layout ===
        upper_container = QFrame()
        upper_container.setStyleSheet("background: none;")
        upper_layout = QHBoxLayout(upper_container)
        upper_layout.setContentsMargins(10, 10, 0, 10)
        upper_layout.setSpacing(20)
        upper_container.setFixedHeight(120)

        results_frame.setFixedWidth(380)  # Optional: shrink results panel width

        upper_layout.addWidget(inputs_frame, stretch=2)
        upper_layout.addWidget(results_frame, stretch=1)

        # Now add the upper container to the main layout
        self.layout.addWidget(upper_container)

        # Main sensitivity container
        sensitivity_container = QFrame()
        sensitivity_container.setStyleSheet("background-color: #2D2D2D; border-radius: 8px;")
        sensitivity_layout = QHBoxLayout(sensitivity_container)
        sensitivity_layout.setContentsMargins(10, 10, 10, 10)
        sensitivity_layout.setSpacing(20)

        # === LEFT: Theta Decay Graph ===
        theta_graph_frame = QFrame()
        theta_graph_layout = QVBoxLayout(theta_graph_frame)
        theta_graph_layout.setContentsMargins(5, 5, 5, 5)

        # Matplotlib Figure
        self.theta_fig = Figure(figsize=(10, 4), dpi=100)
        self.theta_canvas = FigureCanvas(self.theta_fig)
        self.theta_ax = self.theta_fig.add_subplot(111)
        self.theta_fig.patch.set_facecolor("#2D2D2D")
        self.theta_ax.set_facecolor("#2D2D2D")
        self.theta_ax.tick_params(colors='white')
        self.theta_ax.xaxis.label.set_color('white')
        self.theta_ax.yaxis.label.set_color('white')
        self.theta_ax.title.set_color('white')
        for spine in self.theta_ax.spines.values():
            spine.set_edgecolor('#555555')

        theta_graph_layout.addWidget(self.theta_canvas)
        sensitivity_layout.addWidget(theta_graph_frame, stretch=2)
        self.plot_theta_graph()

        # === RIGHT: Calculated Labels ===
        label_container = QFrame()
        label_container.setStyleSheet("background-color: #2D2D2D;")
        label_layout = QHBoxLayout(label_container)
        label_layout.setContentsMargins(10, 10, 10, 10)
        label_layout.setSpacing(40)

        # Create two columns
        column1 = QVBoxLayout()
        column2 = QVBoxLayout()
        column3 = QVBoxLayout()

        # Helper to add styled labels
        def create_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: white; font-size: 14px;")
            return lbl

        # Add labels to column 1
        self.theta_call_label = create_label("Theta Call: -")
        self.theta_put_label = create_label("Theta Put: -")
        self.theta_c_daily_label = create_label("Theta Call Daily: -")
        self.theta_p_daily_label = create_label("Theta Put Daily: -")
        self.delta_call_label = create_label("Delta Call: -")
        self.delta_put_label = create_label("Delta Put: -")
        self.gamma_label = create_label("Gamma: -")
        column1.addWidget(self.theta_call_label)
        column1.addWidget(self.theta_put_label)
        column1.addWidget(self.theta_c_daily_label)
        column1.addWidget(self.theta_p_daily_label)
        column1.addWidget(self.delta_put_label)
        column1.addWidget(self.delta_call_label)
        column1.addWidget(self.gamma_label)

        # Add labels to column 2
        self.vega_label = create_label("Vega: -")
        self.rho_call_label = create_label("Rho Call: -")
        self.rho_put_label = create_label("Rho Put: -")
        self.elasticity_call_label = create_label("Elasticity Call: -")
        self.elasticity_put_label = create_label("Elasticity Put: -")
        column2.addWidget(self.vega_label)
        column2.addWidget(self.rho_call_label)
        column2.addWidget(self.rho_put_label)
        column2.addWidget(self.elasticity_call_label)
        column2.addWidget(self.elasticity_put_label)

        # Add labels to column 3
        self.t_val_label = create_label("Time Value: -")
        self.int_val_label = create_label("Intrinsic Value: -")
        self.put_call_parity_label = create_label("Put-Call Parity: -")
        self.breakeven_put_label = create_label("Breakeven Put: -")
        self.breakeven_call_label = create_label("Breakeven Call: -")
        column3.addWidget(self.t_val_label)
        column3.addWidget(self.int_val_label)
        column3.addWidget(self.put_call_parity_label)
        column3.addWidget(self.breakeven_call_label)
        column3.addWidget(self.breakeven_put_label)

        # Add columns to right panel
        label_layout.addLayout(column1)
        label_layout.addLayout(column2)
        label_layout.addLayout(column3)

        sensitivity_layout.addWidget(label_container, stretch=1)
        self.update_stats_values()

        # Finally, add the full container to your main layout
        self.layout.addWidget(sensitivity_container)


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

        self.plot_theta_graph()
        self.update_stats_values()

    def update_stats_values(self):
        S = self.model_inputs[0].value()  # Underlying
        K = self.model_inputs[1].value()  # Strike
        sigma = self.model_inputs[2].value()  # Volatility (decimal)
        r = self.model_inputs[3].value()  # Interest rate (decimal)
        T = self.model_inputs[4].value()  # Time

        Model = main.BlackScholesModel(S, K, sigma, r, T)
        sens_an = Model.sensitivity_analysis()
        thetas = Model.thetas()
        tval = Model.time_value()
        intval = Model.int_value()
        pcp = Model.put_call_parity()
        bec = Model.breakeven_call()
        bep = Model.breakeven_put()


        self.theta_call_label.setText(f"Theta Call: {thetas[0]:.4f}")
        self.theta_put_label.setText(f"Theta Put: {thetas[1]:.4f}")
        self.theta_c_daily_label.setText(f"Theta Call Daily: {thetas[2]:.4f}")
        self.theta_p_daily_label.setText(f"Theta Put Daily: {thetas[3]:.4f}")
        self.delta_call_label.setText(f"Delta Call: {sens_an[0]:.4f}")
        self.delta_put_label.setText(f"Delta Put: {sens_an[1]:.4f}")
        self.gamma_label.setText(f"Gamma: {sens_an[2]:.4f}")
        self.vega_label.setText(f"Vega: {sens_an[3]:.4f}")
        self.rho_call_label.setText(f"Rho Call: {sens_an[4]:.4f}")
        self.rho_put_label.setText(f"Rho Put: {sens_an[5]:.4f}")
        self.elasticity_call_label.setText(f"Elasticity Call: {sens_an[6]:.4f}")
        self.elasticity_put_label.setText(f"Elasticity Put: {sens_an[7]:.4f}")
        self.t_val_label.setText(f"Time Value: {tval:.4f}")
        self.int_val_label.setText(f"Intrinsic Value: {intval:.4f}")
        self.put_call_parity_label.setText(f"Put-Call Parity: {pcp:.4f}")
        self.breakeven_put_label.setText(f"Breakeven Put: {bep:.4f}")
        self.breakeven_call_label.setText(f"Breakeven Call: {bec:.4f}")



    def plot_theta_graph(self):
        try:
            # Get current input values
            S = self.model_inputs[0].value()
            K = self.model_inputs[1].value()
            sigma = self.model_inputs[2].value()
            r = self.model_inputs[3].value()
            T = self.model_inputs[4].value()

            # Call your model
            Model = main.BlackScholesModel(S, K, sigma, r, T)
            time_values, theta_call, theta_put, _, _ = Model.theta_decay_graph()

            # Clear figure and create 2 subplots side-by-side
            self.theta_fig.clear()
            fig_axes = self.theta_fig.subplots(1, 2)  # (rows=1, cols=2)

            # --- Call Theta subplot --- (Remember you also have the theta decay call graph/365)
            ax1 = fig_axes[0]
            ax1.plot(time_values, theta_call, marker='o', color='cyan', linestyle='-')
            ax1.set_title('Call Theta Decay', color='white')
            ax1.set_xlabel('Time to Expiry', color='white')
            ax1.set_ylabel('Time Value in years', color='white')
            ax1.tick_params(colors='white')
            ax1.set_facecolor('#3E3E3E')
            for spine in ax1.spines.values():
                spine.set_edgecolor('#555555')

            # --- Put Theta subplot --- (Remember you also have the theta decay put graph/365)
            ax2 = fig_axes[1]
            ax2.plot(time_values, theta_put, marker='o', color='magenta', linestyle='-')
            ax2.set_title('Put Theta Decay', color='white')
            ax2.set_xlabel('Time to Expiry', color='white')
            ax2.set_ylabel('Time Value in years', color='white')
            ax2.tick_params(colors='white')
            ax2.set_facecolor('#3E3E3E')
            for spine in ax2.spines.values():
                spine.set_edgecolor('#555555')

            # Apply layout and draw
            self.theta_fig.tight_layout(pad=3.0)
            self.theta_canvas.draw()

        except Exception as e:
            print(f"Theta graph error: {e}")
