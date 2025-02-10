from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QTabWidget, QHeaderView,
    QAbstractItemView, QInputDialog, QMessageBox, QProgressBar, QFileDialog, QComboBox,
    QGraphicsDropShadowEffect, QCheckBox, QTimeEdit
)
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt, QTimer, QSettings, QTime
from PyQt5.QtGui import QIcon, QLinearGradient, QBrush, QColor, QPixmap, QFont
import csv
import os
from datetime import datetime
from typing import List, Dict

# File to store records
DATA_FILE = "accumulative_hour.csv"
SETTINGS_FILE = "app_settings.ini"
USER_DATA_DIR = "user_data"


class CSVHandler:
    @staticmethod
    def initialize_csv(user_id: str = "default"):
        """Initialize the CSV file with headers if it doesn't exist."""
        user_file = os.path.join(USER_DATA_DIR, f"{user_id}_data.csv")
        if not os.path.exists(user_file):
            os.makedirs(USER_DATA_DIR, exist_ok=True)
            with open(user_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Category", "Activity", "TimeSpent"])

    @staticmethod
    def read_all_activities(user_id: str = "default") -> List[Dict[str, str]]:
        """Read all activities from the CSV file."""
        user_file = os.path.join(USER_DATA_DIR, f"{user_id}_data.csv")
        activities = []
        try:
            with open(user_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    row.setdefault("Category", "Other")
                    activities.append(row)
        except FileNotFoundError:
            QMessageBox.warning(None, "File Not Found", "No data file found. A new one will be created.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while reading the file: {e}")
        return activities

    @staticmethod
    def read_activities_for_today(user_id: str = "default") -> List[Dict[str, str]]:
        """Read activities logged for today."""
        user_file = os.path.join(USER_DATA_DIR, f"{user_id}_data.csv")
        today = datetime.now().strftime("%Y-%m-%d")
        activities = []
        try:
            with open(user_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["Date"] == today:
                        row.setdefault("Category", "Other")
                        activities.append(row)
        except FileNotFoundError:
            pass
        return activities

    @staticmethod
    def write_activities(activities: List[Dict[str, str]], user_id: str = "default"):
        """Write activities to the CSV file."""
        user_file = os.path.join(USER_DATA_DIR, f"{user_id}_data.csv")
        try:
            with open(user_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Category", "Activity", "TimeSpent"])
                for activity in activities:
                    writer.writerow([activity["Date"], activity["Category"], activity["Activity"], activity["TimeSpent"]])
        except IOError as e:
            QMessageBox.critical(None, "File Error", f"Failed to write to file: {e}")

    @staticmethod
    def clear_history(user_id: str = "default"):
        """Clear all history from the CSV file."""
        user_file = os.path.join(USER_DATA_DIR, f"{user_id}_data.csv")
        try:
            with open(user_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Category", "Activity", "TimeSpent"])
        except IOError as e:
            QMessageBox.critical(None, "File Error", f"Failed to clear history: {e}")


class AccumulativeHourApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accumulative Hour Tracker")
        self.setGeometry(100, 100, 1200, 800)
        self.daily_goal = 60  # Default daily goal in minutes
        self.user_id = "default"
        self.settings = QSettings(SETTINGS_FILE, QSettings.IniFormat)
        self.load_settings()

        # Initialize UI components
        self.tabs = QTabWidget()
        self.home_tab = QWidget()
        self.stats_tab = QWidget()
        self.settings_tab = QWidget()
        self.activity_input = QLineEdit()
        self.duration_input = QSpinBox()
        self.submit_button = QPushButton("Submit")
        self.activities_table = QTableWidget()
        self.progress_label = QLabel()
        self.progress_bar = QProgressBar()
        self.chart_view = QChartView()
        self.stats_label = QLabel()
        self.stats_data = QLabel()
        self.history_button = QPushButton("Show History")
        self.clear_history_button = QPushButton("Clear History")
        self.export_button = QPushButton("Export History")
        self.history_section = QTableWidget()
        self.category_input = QComboBox()
        self.goal_input = QSpinBox()
        self.dark_mode_toggle = QCheckBox("Dark Mode")
        self.reminder_checkbox = QCheckBox("Enable Reminders")
        self.reminder_time = QTimeEdit()
        self.backup_button = QPushButton("Backup Data")
        self.sync_button = QPushButton("Sync Data")
        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")
        self.user_label = QLabel("Guest")

        # Create a timer for reminders
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminder)
        self.reminder_timer.start(60000)  # Check every minute

        self.init_ui()

    def init_ui(self):
        """Initialize the main UI components."""
        self.setup_tabs()
        self.setCentralWidget(self.tabs)
        self.apply_styles()
        self.setup_animations()
        self.load_user_data()

    def apply_styles(self):
        """Apply styles to the application with improved contrast."""
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        if dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #121212;
                }
                QTabWidget::pane {
                    border: 1px solid #333;
                    border-radius: 10px;
                    background-color: #1e1e1e;
                }
                QTabBar::tab {
                    background: #1e1e1e;
                    color: #FFFFFF;
                    padding: 10px 20px;
                    font-size: 14px;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }
                QTabBar::tab:selected {
                    background: #333333;
                    font-weight: bold;
                }
                QTabBar::tab:hover {
                    background: #444444;
                }
                QPushButton {
                    background-color: #333333;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #FFFFFF;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #222222;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                }
                QTableWidget {
                    background-color: #1e1e1e;
                    color: #FFFFFF;
                    border: none;
                    gridline-color: #444444;
                }
                QHeaderView::section {
                    background-color: #333333;
                    color: #FFFFFF;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                }
                QProgressBar {
                    background-color: #222222;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #00aaff;
                    border-radius: 5px;
                }
                QCheckBox {
                    color: #FFFFFF;
                }
                QMessageBox {
                    background-color: #000000;
                    color: #FFFFFF;
                }
                QInputDialog {
                    background-color: #000000;
                    color: #FFFFFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    background-color: #f8f8f8;
                }
                QTabBar::tab {
                    background: #0087f5;
                    color: white;
                    padding: 10px 20px;
                    font-size: 14px;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }
                QTabBar::tab:selected {
                    background: #299fff;
                    font-weight: bold;
                }
                QTabBar::tab:hover {
                    background: #0070cc;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #005bb5;
                }
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #000000;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                }
                QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: none;
                    gridline-color: #ccc;
                }
                QHeaderView::section {
                    background-color: #0078d7;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                }
                QProgressBar {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #0078d7;
                    border-radius: 5px;
                }
            """)

    def setup_animations(self):
        """Set up animations for UI elements."""
        self.submit_button.setGraphicsEffect(self.create_shadow_effect())
        self.history_button.setGraphicsEffect(self.create_shadow_effect())
        self.clear_history_button.setGraphicsEffect(self.create_shadow_effect())
        self.export_button.setGraphicsEffect(self.create_shadow_effect())

    def create_shadow_effect(self):
        """Create a shadow effect for buttons."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(2, 2)
        return shadow

    def setup_tabs(self):
        """Set up the Home, Stats, and Settings tabs."""
        self.tabs.addTab(self.home_tab, "Home")
        self.setup_home_tab()

        self.tabs.addTab(self.stats_tab, "Stats")
        self.setup_stats_tab()

        self.tabs.addTab(self.settings_tab, "Settings")
        self.setup_settings_tab()

    def setup_home_tab(self):
        """Set up the Home tab with input fields, activity table, and pie chart."""
        layout = QVBoxLayout()

        # Input Section
        input_layout = QHBoxLayout()
        self.category_input.addItems(["Work", "Leisure", "Exercise", "Other"])
        self.activity_input.setPlaceholderText("Enter activity name")
        self.duration_input.setRange(1, 300)
        self.submit_button.clicked.connect(self.add_activity)

        input_layout.addWidget(QLabel("Category:"))
        input_layout.addWidget(self.category_input)
        input_layout.addWidget(QLabel("Activity:"))
        input_layout.addWidget(self.activity_input)
        input_layout.addWidget(QLabel("Duration (mins):"))
        input_layout.addWidget(self.duration_input)
        input_layout.addWidget(self.submit_button)

        # Activities Table
        self.activities_table.setColumnCount(5)
        self.activities_table.setHorizontalHeaderLabels(["Category", "Activity", "Duration", "Edit", "Delete"])
        self.activities_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activities_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.load_activities()

        # Progress Visualization
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_bar.setMaximum(self.daily_goal)
        self.update_pie_chart()

        layout.addLayout(input_layout)
        layout.addWidget(QLabel("Today's Activities:"))
        layout.addWidget(self.activities_table)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.chart_view)
        self.home_tab.setLayout(layout)

    def setup_stats_tab(self):
        """Set up the Stats tab with statistics and history."""
        layout = QVBoxLayout()

        # Statistics Section
        self.stats_label.setText("<h2>Statistics</h2>")
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)

        self.stats_data.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_data)

        self.update_stats()

        # History Section
        self.history_button.clicked.connect(self.toggle_history)
        layout.addWidget(self.history_button)

        self.clear_history_button.clicked.connect(self.clear_history)
        layout.addWidget(self.clear_history_button)

        self.export_button.clicked.connect(self.export_history)
        layout.addWidget(self.export_button)

        self.history_section.setColumnCount(4)
        self.history_section.setHorizontalHeaderLabels(["Date", "Category", "Activity", "Time Spent (mins)"])
        self.history_section.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_section.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_section.setVisible(False)  # Initially hidden
        layout.addWidget(self.history_section)

        self.stats_tab.setLayout(layout)

    def toggle_history(self):
        """Toggle the visibility of the history section."""
        if self.history_section.isVisible():
            self.history_section.setVisible(False)
            self.history_button.setText("Show History")
        else:
            self.history_section.setVisible(True)
            self.history_button.setText("Hide History")
            self.show_history()

    def setup_settings_tab(self):
        """Set up the Settings tab with user preferences."""
        layout = QVBoxLayout()

        # Dark Mode Toggle
        self.dark_mode_toggle.setChecked(self.settings.value("dark_mode", False, type=bool))
        self.dark_mode_toggle.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_toggle)

        # Reminder Settings
        self.reminder_checkbox.setChecked(self.settings.value("reminders_enabled", False, type=bool))
        self.reminder_checkbox.stateChanged.connect(self.toggle_reminders)
        self.reminder_time.setTime(self.settings.value("reminder_time", QTime(18, 0)))
        self.reminder_time.setEnabled(self.reminder_checkbox.isChecked())
        layout.addWidget(self.reminder_checkbox)
        layout.addWidget(QLabel("Reminder Time:"))
        layout.addWidget(self.reminder_time)

        # Backup and Sync
        self.backup_button.clicked.connect(self.backup_data)
        self.sync_button.clicked.connect(self.sync_data)
        layout.addWidget(self.backup_button)
        layout.addWidget(self.sync_button)

        # User Authentication
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.user_label)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.settings_tab.setLayout(layout)

    def toggle_dark_mode(self):
        """Toggle dark mode."""
        dark_mode = self.dark_mode_toggle.isChecked()
        self.settings.setValue("dark_mode", dark_mode)
        self.apply_styles()
        self.update_pie_chart()

    def toggle_reminders(self):
        """Toggle reminders."""
        reminders_enabled = self.reminder_checkbox.isChecked()
        self.settings.setValue("reminders_enabled", reminders_enabled)
        self.reminder_time.setEnabled(reminders_enabled)

    def backup_data(self):
        """Backup user data."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Backup Data", "", "CSV Files (*.csv)")
        if file_name:
            if os.path.exists(file_name):
                confirm = QMessageBox.question(self, "Confirm Overwrite", "The file already exists. Do you want to overwrite it?",
                                              QMessageBox.Yes | QMessageBox.No)
                if confirm != QMessageBox.Yes:
                    return
            activities = CSVHandler.read_all_activities(self.user_id)
            with open(file_name, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Category", "Activity", "TimeSpent"])
                for activity in activities:
                    writer.writerow([activity["Date"], activity["Category"], activity["Activity"], activity["TimeSpent"]])
            QMessageBox.information(self, "Backup Successful", "Data backed up successfully!")

    def sync_data(self):
        """Sync user data with cloud."""
        QMessageBox.information(self, "Sync", "Sync feature is not implemented yet.")

    def login(self):
        """Login user."""
        user_id, ok = QInputDialog.getText(self, "Login", "Enter your user ID:")
        if ok and user_id:
            self.user_id = user_id
            self.user_label.setText(f"Logged in as: {user_id}")
            self.load_user_data()

    def register(self):
        """Register new user."""
        user_id, ok = QInputDialog.getText(self, "Register", "Enter a new user ID:")
        if ok and user_id:
            self.user_id = user_id
            self.user_label.setText(f"Logged in as: {user_id}")
            CSVHandler.initialize_csv(user_id)
            self.load_user_data()

    def load_user_data(self):
        """Load user-specific data."""
        CSVHandler.initialize_csv(self.user_id)
        self.load_activities()
        self.update_pie_chart()
        self.update_stats()

    def load_activities(self):
        """Load today's activities into the table."""
        activities = CSVHandler.read_activities_for_today(self.user_id)
        self.activities_table.setRowCount(len(activities))
        for row_idx, activity in enumerate(activities):
            self.activities_table.setItem(row_idx, 0, QTableWidgetItem(activity["Category"]))
            self.activities_table.setItem(row_idx, 1, QTableWidgetItem(activity["Activity"]))
            self.activities_table.setItem(row_idx, 2, QTableWidgetItem(activity["TimeSpent"]))

            edit_button = QPushButton()
            edit_icon = QIcon("assets/icons/edit_icon.png")
            if edit_icon.isNull():
                edit_button.setText("Edit")
            else:
                edit_button.setIcon(edit_icon)
            edit_button.setStyleSheet("background-color: #f39c12; border-radius: 5px;")
            edit_button.clicked.connect(lambda _, r=row_idx: self.edit_activity(r))
            self.activities_table.setCellWidget(row_idx, 3, edit_button)

            delete_button = QPushButton()
            delete_icon = QIcon("assets/icons/delete_icon.png")
            if delete_icon.isNull():
                delete_button.setText("Delete")
            else:
                delete_button.setIcon(delete_icon)
            delete_button.setStyleSheet("background-color: #e74c3c; border-radius: 5px;")
            delete_button.clicked.connect(lambda _, r=row_idx: self.delete_activity(r))
            self.activities_table.setCellWidget(row_idx, 4, delete_button)

    def update_pie_chart(self):
        """Update the pie chart with today's progress."""
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        activities = CSVHandler.read_activities_for_today(self.user_id)
        total_time = sum(int(activity["TimeSpent"]) for activity in activities)
        remaining_time = max(self.daily_goal - total_time, 0)

        series = QPieSeries()
        completed_slice = series.append("Completed", total_time)
        remain_slice = series.append("Remaining", remaining_time)


        # Force labels to be white with a bold font for better contrast
        label_font = QFont("Arial", 10, QFont.Bold)
        completed_slice.setLabelColor(QColor("white"))
        completed_slice.setLabelFont(label_font)
        remain_slice.setLabelColor(QColor("white"))
        remain_slice.setLabelFont(label_font)
        completed_slice.setLabelVisible(True)
        remain_slice.setLabelVisible(True)

        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # For light mode, use a lighter gradient so white labels remain visible
        if dark_mode:
            gradient = QLinearGradient(0.0, 0.0, 1.0, 1.0)
            gradient.setColorAt(0, QColor("#34495e"))
            gradient.setColorAt(1, QColor("#2c3e50"))
            chart.legend().setLabelColor(QColor("white"))
            completed_slice.setLabelColor(QColor("white"))
            remain_slice.setLabelColor(QColor("white"))
            chart.setTitle(f"<h2 style='color: white;'>Progress Towards Daily Goal</h2>")
            self.progress_label.setText(
                f"<h3 style='color: white;'>Completed: {total_time} mins, Remaining: {remaining_time} mins</h3>")
        else:
            gradient = QLinearGradient(0.0, 0.0, 1.0, 1.0)
            gradient.setColorAt(0, QColor("#7FB3D5"))
            gradient.setColorAt(1, QColor("#AED6F1"))
            completed_slice.setLabelColor(QColor("black"))
            remain_slice.setLabelColor(QColor("black"))
            chart.setTitle(f"<h2 style='color: black;'>Progress Towards Daily Goal</h2>")
            self.progress_label.setText(
                f"<h3 style='color: black;'>Completed: {total_time} mins, Remaining: {remaining_time} mins</h3>")
        chart.setBackgroundBrush(QBrush(gradient))

        self.chart_view.setChart(chart)
        self.progress_bar.setValue(total_time)

        # Notify if daily goal is reached
        if total_time >= self.daily_goal and not self.settings.value("goal_reached_today", False, type=bool):
            QMessageBox.information(self, "Goal Reached", "Congratulations! You've reached your daily goal.")
            self.settings.setValue("goal_reached_today", True)
        elif total_time < self.daily_goal:
            self.settings.setValue("goal_reached_today", False)

    def update_stats(self):
        """Update the statistics section."""
        activities = CSVHandler.read_all_activities(self.user_id)
        total_activities = len(activities)
        unique_activities = len(set(activity["Activity"] for activity in activities))
        total_time = sum(int(activity["TimeSpent"]) for activity in activities)
        days_logged = len(set(activity["Date"] for activity in activities))
        days_completed_goal = len(
            {activity["Date"] for activity in activities if sum(int(a["TimeSpent"]) for a in activities if a["Date"] == activity["Date"]) >= self.daily_goal}
        )

        stats_html = f"""
        <h3>Total Activities: {total_activities}</h3>
        <h3>Unique Activities: {unique_activities}</h3>
        <h3>Total Time Spent: {total_time} mins</h3>
        <h3>Total Days Logged: {days_logged}</h3>
        <h3>Days Meeting Daily Goal: {days_completed_goal}</h3>
        """
        self.stats_data.setText(stats_html)

    def export_history(self):
        """Export all historical activities to a CSV file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Export History", "", "CSV Files (*.csv)")
        if file_name:
            if os.path.exists(file_name):
                confirm = QMessageBox.question(self, "Confirm Overwrite",
                                               "The file already exists. Do you want to overwrite it?",
                                               QMessageBox.Yes | QMessageBox.No)
                if confirm != QMessageBox.Yes:
                    return
            activities = CSVHandler.read_all_activities(self.user_id)
            with open(file_name, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Category", "Activity", "TimeSpent"])
                for activity in activities:
                    writer.writerow(
                        [activity["Date"], activity["Category"], activity["Activity"], activity["TimeSpent"]])
            QMessageBox.information(self, "Export Successful", "History exported successfully!")

    def clear_history(self):
        """Clear all history from the CSV file."""
        confirm = QMessageBox.question(self, "Confirm Clear History", "Are you sure you want to clear all history?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            CSVHandler.clear_history(self.user_id)
            self.load_activities()  # Reload activities to reflect the cleared history
            self.update_pie_chart()  # Update the pie chart
            self.update_stats()  # Update the statistics
            QMessageBox.information(self, "History Cleared", "All history has been cleared.")

    def show_history(self):
        """Load and display all historical activities."""
        activities = CSVHandler.read_all_activities(self.user_id)
        self.history_section.setRowCount(len(activities))
        for row_idx, activity in enumerate(activities):
            self.history_section.setItem(row_idx, 0, QTableWidgetItem(activity["Date"]))
            self.history_section.setItem(row_idx, 1, QTableWidgetItem(activity["Category"]))
            self.history_section.setItem(row_idx, 2, QTableWidgetItem(activity["Activity"]))
            self.history_section.setItem(row_idx, 3, QTableWidgetItem(activity["TimeSpent"]))

    def check_reminder(self):
        """Check if it's time for a reminder."""
        if self.settings.value("reminders_enabled", False, type=bool):
            reminder_time = self.reminder_time.time()  # QTime object from QTimeEdit
            current_time = QTime.currentTime()
            # If current time matches the reminder time (allowing minute-level precision)
            if (current_time.hour() == reminder_time.hour() and
                    current_time.minute() == reminder_time.minute()):
                QMessageBox.information(self, "Reminder", "This is your reminder!")

    def add_activity(self):
        """Add a new activity to the CSV file."""
        category = self.category_input.currentText()
        activity = self.activity_input.text().strip()
        duration = self.duration_input.value()
        if activity:
            today = datetime.now().strftime("%Y-%m-%d")
            with open(os.path.join(USER_DATA_DIR, f"{self.user_id}_data.csv"), "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([today, category, activity, duration])
            self.activity_input.clear()
            self.duration_input.setValue(1)
            self.load_activities()
            self.update_pie_chart()

    def edit_activity(self, row_idx):
        """Edit an existing activity."""
        activity_item = self.activities_table.item(row_idx, 1)
        time_item = self.activities_table.item(row_idx, 2)

        new_activity, ok_activity = QInputDialog.getText(self, "Edit Activity", "Enter new activity:", text=activity_item.text())
        new_time, ok_time = QInputDialog.getInt(self, "Edit Duration", "Enter new duration:", value=int(time_item.text()), min=1, max=300)

        if ok_activity and ok_time:
            activities = CSVHandler.read_activities_for_today(self.user_id)
            activities[row_idx]["Activity"] = new_activity
            activities[row_idx]["TimeSpent"] = str(new_time)
            CSVHandler.write_activities(activities, self.user_id)
            self.load_activities()
            self.update_pie_chart()

    def delete_activity(self, row_idx):
        """Delete an activity after confirmation."""
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this activity?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            activities = CSVHandler.read_activities_for_today(self.user_id)
            del activities[row_idx]
            CSVHandler.write_activities(activities, self.user_id)
            self.load_activities()
            self.update_pie_chart()

    def load_settings(self):
        """Load user settings."""
        self.daily_goal = self.settings.value("daily_goal", 60, type=int)
        self.user_id = self.settings.value("user_id", "default")

    def save_settings(self):
        """Save user settings."""
        self.settings.setValue("daily_goal", self.daily_goal)
        self.settings.setValue("user_id", self.user_id)

    def closeEvent(self, event):
        """Save settings when the application is closed."""
        confirm = QMessageBox.question(self, "Confirm Exit", "Are you sure you want to exit?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.save_settings()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication([])
    window = AccumulativeHourApp()
    window.show()
    app.exec_()
