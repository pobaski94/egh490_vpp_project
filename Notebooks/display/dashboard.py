import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# ============================================================
# COLOURS
# ============================================================

BACKGROUND = "#0B1120"
PANEL = "#111827"
PANEL_ALT = "#182235"

BORDER = "#263247"

TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"

GREEN = "#22C55E"
BLUE = "#38BDF8"
ORANGE = "#F59E0B"
RED = "#EF4444"
PURPLE = "#A78BFA"


# ============================================================
# KPI CARD
# ============================================================

class KPICard(QFrame):

    def __init__(
        self,
        title,
        value="0.00",
        unit="",
        colour=BLUE,
    ):
        super().__init__()

        self.setObjectName("kpiCard")

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        layout.setSpacing(4)

        self.title_label = QLabel(title)

        self.title_label.setObjectName(
            "secondaryText"
        )

        value_row = QHBoxLayout()

        value_row.setSpacing(5)

        self.value_label = QLabel(value)

        self.value_label.setStyleSheet(
            f"""
            color: {colour};
            font-size: 27px;
            font-weight: 700;
            """
        )

        self.unit_label = QLabel(unit)

        self.unit_label.setObjectName(
            "secondaryText"
        )

        self.unit_label.setAlignment(
            Qt.AlignBottom
        )

        value_row.addWidget(
            self.value_label
        )

        value_row.addWidget(
            self.unit_label
        )

        value_row.addStretch()

        layout.addWidget(
            self.title_label
        )

        layout.addLayout(
            value_row
        )

    def set_value(self, value):
        self.value_label.setText(
            str(value)
        )


# ============================================================
# STATUS BADGE
# ============================================================

class StatusBadge(QLabel):

    def __init__(
        self,
        text,
        colour=GREEN
    ):
        super().__init__(text)

        self.colour = colour

        self.setAlignment(
            Qt.AlignCenter
        )

        self.setMinimumHeight(30)

        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {colour};
                color: #081018;
                border-radius: 8px;
                padding: 5px 12px;
                font-weight: 700;
            }}
            """
        )

    def set_status(
        self,
        text,
        colour
    ):
        self.setText(text)

        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {colour};
                color: #081018;
                border-radius: 8px;
                padding: 5px 12px;
                font-weight: 700;
            }}
            """
        )


# ============================================================
# HOUSE CARD
# ============================================================

class HouseCard(QFrame):

    def __init__(
        self,
        house_name,
        has_battery=True
    ):
        super().__init__()

        self.setObjectName(
            "houseCard"
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        layout.setSpacing(9)

        # --------------------------------------------
        # HEADER
        # --------------------------------------------

        header = QHBoxLayout()

        self.name_label = QLabel(
            house_name
        )

        self.name_label.setObjectName(
            "houseTitle"
        )

        self.state_label = StatusBadge(
            "IDLE",
            BLUE
        )

        header.addWidget(
            self.name_label
        )

        header.addStretch()

        header.addWidget(
            self.state_label
        )

        layout.addLayout(
            header
        )

        # --------------------------------------------
        # HOUSE POWER VALUES
        # --------------------------------------------

        self.load_label = QLabel(
            "Load       0.00 kW"
        )

        self.pv_label = QLabel(
            "PV         0.00 kW"
        )

        self.grid_label = QLabel(
            "Grid       0.00 kW"
        )

        self.battery_label = QLabel(
            "Battery    0.00 kW"
        )

        for label in [
            self.load_label,
            self.pv_label,
            self.grid_label,
            self.battery_label,
        ]:
            label.setObjectName(
                "houseValue"
            )

            layout.addWidget(
                label
            )

        # --------------------------------------------
        # BATTERY SOC
        # --------------------------------------------

        self.soc_title = QLabel(
            "Battery SOC"
        )

        self.soc_title.setObjectName(
            "secondaryText"
        )

        self.soc_bar = QProgressBar()

        self.soc_bar.setRange(
            0,
            100
        )

        self.soc_bar.setValue(
            50 if has_battery else 0
        )

        self.soc_bar.setTextVisible(
            True
        )

        if not has_battery:

            self.soc_title.setText(
                "No Battery"
            )

            self.soc_bar.setEnabled(
                False
            )

        layout.addWidget(
            self.soc_title
        )

        layout.addWidget(
            self.soc_bar
        )

        # --------------------------------------------
        # EVENT
        # --------------------------------------------

        self.event_label = QLabel(
            "Event: 0.00 / 0.00 kW"
        )

        self.event_label.setObjectName(
            "secondaryText"
        )

        layout.addWidget(
            self.event_label
        )


# ============================================================
# PLACEHOLDER CHART PANEL
# ============================================================

class ChartPlaceholder(QFrame):

    def __init__(
        self,
        title
    ):
        super().__init__()

        self.setObjectName(
            "chartPanel"
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "panelTitle"
        )

        placeholder = QLabel(
            "Live chart will be added here"
        )

        placeholder.setAlignment(
            Qt.AlignCenter
        )

        placeholder.setObjectName(
            "secondaryText"
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            placeholder,
            1
        )


# ============================================================
# MAIN WINDOW
# ============================================================

class VPPDashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "EGH490 Virtual Power Plant Demonstrator"
        )

        self.resize(
            1600,
            950
        )

        self.setMinimumSize(
            1250,
            800
        )

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        root = QVBoxLayout(
            central_widget
        )

        root.setContentsMargins(
            22,
            18,
            22,
            18
        )

        root.setSpacing(
            16
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = QHBoxLayout()

        title_section = QVBoxLayout()

        title = QLabel(
            "VIRTUAL POWER PLANT"
        )

        title.setObjectName(
            "mainTitle"
        )

        subtitle = QLabel(
            "EGH490 Residential DER Demonstrator"
        )

        subtitle.setObjectName(
            "secondaryText"
        )

        title_section.addWidget(
            title
        )

        title_section.addWidget(
            subtitle
        )

        header.addLayout(
            title_section
        )

        header.addStretch()

        self.time_label = QLabel(
            "DAY 1  •  16:00"
        )

        self.time_label.setObjectName(
            "timeLabel"
        )

        header.addWidget(
            self.time_label
        )

        root.addLayout(
            header
        )

        # ====================================================
        # STATUS BAR
        # ====================================================

        status_panel = QFrame()

        status_panel.setObjectName(
            "panel"
        )

        status_layout = QHBoxLayout(
            status_panel
        )

        status_layout.setContentsMargins(
            16,
            10,
            16,
            10
        )

        status_layout.addWidget(
            QLabel("VPP MODE")
        )

        self.mode_badge = StatusBadge(
            "SELF CONSUMPTION",
            BLUE
        )

        self.event_badge = StatusBadge(
            "VPP EVENT OFF",
            TEXT_SECONDARY
        )

        self.sharing_badge = StatusBadge(
            "PV SHARING ON",
            GREEN
        )

        self.economic_badge = StatusBadge(
            "ECONOMIC EXPORT ON",
            PURPLE
        )

        status_layout.addWidget(
            self.mode_badge
        )

        status_layout.addSpacing(
            12
        )

        status_layout.addWidget(
            self.event_badge
        )

        status_layout.addWidget(
            self.sharing_badge
        )

        status_layout.addWidget(
            self.economic_badge
        )

        status_layout.addStretch()

        root.addWidget(
            status_panel
        )

        # ====================================================
        # VPP KPI CARDS
        # ====================================================

        kpi_layout = QGridLayout()

        kpi_layout.setSpacing(
            12
        )

        self.grid_import_card = KPICard(
            "GRID IMPORT",
            "0.00",
            "kW",
            RED
        )

        self.grid_export_card = KPICard(
            "GRID EXPORT",
            "0.00",
            "kW",
            GREEN
        )

        self.event_request_card = KPICard(
            "EVENT REQUEST",
            "0.00",
            "kW",
            ORANGE
        )

        self.event_delivery_card = KPICard(
            "EVENT DELIVERED",
            "0.00",
            "kW",
            GREEN
        )

        self.battery_card = KPICard(
            "BATTERY ENERGY",
            "0.00",
            "kWh",
            PURPLE
        )

        self.cost_card = KPICard(
            "VPP NET COST",
            "$0.00",
            "",
            BLUE
        )

        cards = [
            self.grid_import_card,
            self.grid_export_card,
            self.event_request_card,
            self.event_delivery_card,
            self.battery_card,
            self.cost_card,
        ]

        for index, card in enumerate(
            cards
        ):
            kpi_layout.addWidget(
                card,
                0,
                index
            )

        root.addLayout(
            kpi_layout
        )

        # ====================================================
        # HOUSE CARDS
        # ====================================================

        houses_title = QLabel(
            "HOUSEHOLD DER STATUS"
        )

        houses_title.setObjectName(
            "sectionTitle"
        )

        root.addWidget(
            houses_title
        )

        houses_layout = QHBoxLayout()

        houses_layout.setSpacing(
            12
        )

        self.house_cards = {
            "House 1": HouseCard(
                "HOUSE 1"
            ),

            "House 2": HouseCard(
                "HOUSE 2"
            ),

            "House 3": HouseCard(
                "HOUSE 3",
                has_battery=False
            ),

            "House 4": HouseCard(
                "HOUSE 4"
            ),

            "House 5": HouseCard(
                "HOUSE 5"
            ),
        }

        for card in (
            self.house_cards.values()
        ):
            houses_layout.addWidget(
                card
            )

        root.addLayout(
            houses_layout
        )

        # ====================================================
        # LOWER DASHBOARD
        # ====================================================

        lower_layout = QHBoxLayout()

        lower_layout.setSpacing(
            12
        )

        vpp_chart = ChartPlaceholder(
            "VPP POWER FLOW"
        )

        event_chart = ChartPlaceholder(
            "VPP EVENT RESPONSE"
        )

        comparison_chart = ChartPlaceholder(
            "SCENARIO COMPARISON"
        )

        lower_layout.addWidget(
            vpp_chart,
            2
        )

        lower_layout.addWidget(
            event_chart,
            2
        )

        lower_layout.addWidget(
            comparison_chart,
            1
        )

        root.addLayout(
            lower_layout,
            1
        )

        self.apply_theme()


    # ========================================================
    # THEME
    # ========================================================

    def apply_theme(self):

        self.setStyleSheet(
            f"""
            QMainWindow,
            QWidget {{
                background-color: {BACKGROUND};
                color: {TEXT_PRIMARY};
                font-family:
                    "Segoe UI",
                    "Arial";
                font-size: 13px;
            }}

            QFrame#panel,
            QFrame#kpiCard,
            QFrame#houseCard,
            QFrame#chartPanel {{
                background-color: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}

            QLabel#mainTitle {{
                color: {TEXT_PRIMARY};
                font-size: 28px;
                font-weight: 800;
                letter-spacing: 2px;
            }}

            QLabel#sectionTitle {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
            }}

            QLabel#panelTitle {{
                color: {TEXT_PRIMARY};
                font-size: 15px;
                font-weight: 700;
            }}

            QLabel#houseTitle {{
                color: {TEXT_PRIMARY};
                font-size: 17px;
                font-weight: 700;
            }}

            QLabel#houseValue {{
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}

            QLabel#secondaryText {{
                color: {TEXT_SECONDARY};
            }}

            QLabel#timeLabel {{
                color: {BLUE};
                font-size: 18px;
                font-weight: 700;
            }}

            QProgressBar {{
                background-color: {PANEL_ALT};
                border: 1px solid {BORDER};
                border-radius: 7px;
                height: 17px;
                text-align: center;
                color: {TEXT_PRIMARY};
            }}

            QProgressBar::chunk {{
                background-color: {PURPLE};
                border-radius: 6px;
            }}

            QPushButton {{
                background-color: {PANEL_ALT};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 8px 14px;
                color: {TEXT_PRIMARY};
            }}

            QPushButton:hover {{
                border-color: {BLUE};
                background-color: #1E293B;
            }}
            """
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def run_dashboard():

    app = QApplication(
        sys.argv
    )

    dashboard = VPPDashboard()

    dashboard.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    run_dashboard()