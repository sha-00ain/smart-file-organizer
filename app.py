import sys
from pathlib import Path
from collections import Counter
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QTextEdit,
    QMessageBox,
    QLabel,
    QFrame,
    QDialog,
    QListWidget,
    QInputDialog,
    QGridLayout,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
def resource_path(filename):
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / filename
    return Path(__file__).parent / filename
from organizer import (
    organize_files,
    undo_moves,
    CATEGORIES,
    save_categories,
)


# ============================================================
# SETTINGS WINDOW
# ============================================================

class SettingsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setFixedSize(420, 400)

        self.setup_ui()
        self.apply_style()


    def setup_ui(self):

        title = QLabel("File Categories")
        title.setObjectName("settingsTitle")

        info = QLabel(
            "Customize which file extensions belong "
            "to each category."
        )

        info.setWordWrap(True)

        self.category_list = QListWidget()

        self.load_categories()

        add_button = QPushButton("Add Extension")
        remove_button = QPushButton("Remove Extension")
        close_button = QPushButton("Save & Close")

        button_layout = QHBoxLayout()

        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(close_button)

        layout = QVBoxLayout()

        layout.setSpacing(10)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(self.category_list)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        add_button.clicked.connect(
            self.add_extension
        )

        remove_button.clicked.connect(
            self.remove_extension
        )

        close_button.clicked.connect(
            self.save_and_close
        )


    def apply_style(self):

        self.setStyleSheet("""

            QWidget {
                font-family: Segoe UI;
                font-size: 13px;
            }

            QLabel#settingsTitle {
                font-size: 21px;
                font-weight: bold;
            }

            QPushButton {
                padding: 8px 10px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background: #f5f5f5;
            }

            QPushButton:hover {
                background: #e5e5e5;
            }

            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 4px;
            }

        """)


    def load_categories(self):

        self.category_list.clear()

        for category, extensions in CATEGORIES.items():

            for extension in extensions:

                self.category_list.addItem(
                    f"{category}    →    {extension}"
                )


    def add_extension(self):

        extension, ok = QInputDialog.getText(
            self,
            "Add Extension",
            "Enter extension (example: .py):"
        )

        if not ok:
            return

        extension = extension.strip().lower()

        if not extension:
            return

        if not extension.startswith("."):
            extension = "." + extension

        category, ok = QInputDialog.getItem(
            self,
            "Choose Category",
            "Category:",
            list(CATEGORIES.keys()),
            0,
            False
        )

        if not ok:
            return

        for extensions in CATEGORIES.values():

            if extension in extensions:
                extensions.remove(extension)

        CATEGORIES[category].append(extension)

        self.load_categories()


    def remove_extension(self):

        current_item = self.category_list.currentItem()

        if current_item is None:

            QMessageBox.information(
                self,
                "Select Extension",
                "Please select an extension first."
            )

            return

        text = current_item.text()

        extension = text.split("→")[-1].strip()

        for extensions in CATEGORIES.values():

            if extension in extensions:
                extensions.remove(extension)

        self.load_categories()


    def save_and_close(self):

        save_categories(CATEGORIES)

        self.accept()


# ============================================================
# MAIN APPLICATION
# ============================================================

class OrganizerApp(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowIcon(
            QIcon(str(resource_path("icon.ico")))
        )

        self.last_moves = []

        self.setWindowTitle(
            "Smart File Organizer"
        )

        # ----------------------------------------------------
        # FIXED COMPACT WINDOW
        # ----------------------------------------------------

        self.setFixedSize(
            390,
            450
        )

        self.setup_ui()
        self.apply_style()


    # ========================================================
    # MAIN UI
    # ========================================================

    def setup_ui(self):

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = QLabel(
            "Smart File Organizer"
        )

        title.setObjectName(
            "title"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )


        subtitle = QLabel(
            "Organize your files automatically and safely."
        )

        subtitle.setObjectName(
            "subtitle"
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )


        # ----------------------------------------------------
        # LINE
        # ----------------------------------------------------

        line = QFrame()

        line.setFrameShape(
            QFrame.Shape.HLine
        )


        # ----------------------------------------------------
        # FOLDER
        # ----------------------------------------------------

        folder_label = QLabel(
            "Folder"
        )

        folder_label.setObjectName(
            "sectionLabel"
        )


        self.path_input = QLineEdit()

        self.path_input.setPlaceholderText(
            "Select folder..."
        )


        self.browse_button = QPushButton(
            "Browse"
        )


        folder_layout = QHBoxLayout()

        folder_layout.setSpacing(6)

        folder_layout.addWidget(
            self.path_input
        )

        folder_layout.addWidget(
            self.browse_button
        )


        # ----------------------------------------------------
        # ACTION BUTTONS
        # ----------------------------------------------------

        self.preview_button = QPushButton(
            "Preview"
        )

        self.organize_button = QPushButton(
            "Organize"
        )

        self.undo_button = QPushButton(
            "Undo"
        )

        self.settings_button = QPushButton(
            "Settings"
        )


        row1 = QHBoxLayout()

        row1.setSpacing(6)

        row1.addWidget(
            self.preview_button
        )

        row1.addWidget(
            self.organize_button
        )


        row2 = QHBoxLayout()

        row2.setSpacing(6)

        row2.addWidget(
            self.undo_button
        )

        row2.addWidget(
            self.settings_button
        )


        # ----------------------------------------------------
        # DASHBOARD
        # ----------------------------------------------------

        dashboard_label = QLabel(
            "Summary"
        )

        dashboard_label.setObjectName(
            "sectionLabel"
        )


        self.total_value = QLabel(
            "0"
        )

        self.total_value.setObjectName(
            "totalValue"
        )

        self.total_text = QLabel(
            "Files Organized"
        )

        self.total_text.setObjectName(
            "totalText"
        )


        total_box = QVBoxLayout()

        total_box.setSpacing(0)

        total_box.addWidget(
            self.total_value
        )

        total_box.addWidget(
            self.total_text
        )


        # Category labels

        self.image_count = QLabel(
            "Images: 0"
        )

        self.video_count = QLabel(
            "Videos: 0"
        )

        self.audio_count = QLabel(
            "Audio: 0"
        )

        self.document_count = QLabel(
            "Documents: 0"
        )

        self.archive_count = QLabel(
            "Archives: 0"
        )

        self.program_count = QLabel(
            "Programs: 0"
        )

        self.other_count = QLabel(
            "Others: 0"
        )


        category_grid = QGridLayout()

        category_grid.setHorizontalSpacing(12)
        category_grid.setVerticalSpacing(2)


        category_grid.addWidget(
            self.image_count,
            0,
            0
        )

        category_grid.addWidget(
            self.video_count,
            0,
            1
        )

        category_grid.addWidget(
            self.audio_count,
            1,
            0
        )

        category_grid.addWidget(
            self.document_count,
            1,
            1
        )

        category_grid.addWidget(
            self.archive_count,
            2,
            0
        )

        category_grid.addWidget(
            self.program_count,
            2,
            1
        )

        category_grid.addWidget(
            self.other_count,
            3,
            0
        )


        dashboard_layout = QHBoxLayout()

        dashboard_layout.addLayout(
            total_box
        )

        dashboard_layout.addLayout(
            category_grid
        )


        # ----------------------------------------------------
        # ACTIVITY
        # ----------------------------------------------------

        output_label = QLabel(
            "Activity"
        )

        output_label.setObjectName(
            "sectionLabel"
        )


        self.output = QTextEdit()

        self.output.setReadOnly(
            True
        )

        self.output.setPlaceholderText(
            "Activity will appear here..."
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status = QLabel(
            "Ready"
        )

        self.status.setObjectName(
            "status"
        )


        # ----------------------------------------------------
        # DEVELOPER
        # ----------------------------------------------------

        developer = QLabel(
            "Developed by Md. Shakil Hossain  •  "
            "shakil.hossain2417@gmail.com"
        )

        developer.setObjectName(
            "developer"
        )

        developer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        developer.setWordWrap(
            True
        )


        # ----------------------------------------------------
        # MAIN LAYOUT
        # ----------------------------------------------------

        layout = QVBoxLayout()

        layout.setContentsMargins(
            15,
            10,
            15,
            8
        )

        layout.setSpacing(
            6
        )


        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addWidget(
            line
        )

        layout.addWidget(
            folder_label
        )

        layout.addLayout(
            folder_layout
        )

        layout.addLayout(
            row1
        )

        layout.addLayout(
            row2
        )

        layout.addWidget(
            dashboard_label
        )

        layout.addLayout(
            dashboard_layout
        )

        layout.addWidget(
            output_label
        )

        layout.addWidget(
            self.output,
            1
        )

        layout.addWidget(
            self.status
        )

        layout.addWidget(
            developer
        )


        self.setLayout(
            layout
        )


        # ----------------------------------------------------
        # CONNECTIONS
        # ----------------------------------------------------

        self.browse_button.clicked.connect(
            self.browse_folder
        )

        self.preview_button.clicked.connect(
            self.preview
        )

        self.organize_button.clicked.connect(
            self.organize
        )

        self.undo_button.clicked.connect(
            self.undo
        )

        self.settings_button.clicked.connect(
            self.open_settings
        )


    # ========================================================
    # STYLE
    # ========================================================

    def apply_style(self):

        self.setStyleSheet("""

            QWidget {
                font-family: Segoe UI;
                font-size: 12px;
            }


            QLabel#title {
                font-size: 21px;
                font-weight: bold;
            }


            QLabel#subtitle {
                font-size: 10px;
            }


            QLabel#sectionLabel {
                font-size: 12px;
                font-weight: bold;
            }


            QLineEdit {
                padding: 7px;
                border: 1px solid #cccccc;
                border-radius: 6px;
            }


            QLineEdit:focus {
                border: 1px solid #888888;
            }


            QPushButton {
                padding: 7px 10px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background: #f5f5f5;
            }


            QPushButton:hover {
                background: #e5e5e5;
            }


            QPushButton:pressed {
                background: #d5d5d5;
            }


            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px;
            }


            QLabel#totalValue {
                font-size: 25px;
                font-weight: bold;
            }


            QLabel#totalText {
                font-size: 9px;
            }


            QLabel#status {
                font-size: 10px;
            }


            QLabel#developer {
                font-size: 8px;
            }

        """)


    # ========================================================
    # RESET DASHBOARD
    # ========================================================

    def reset_dashboard(self):

        self.total_value.setText(
            "0"
        )

        self.image_count.setText(
            "Images: 0"
        )

        self.video_count.setText(
            "Videos: 0"
        )

        self.audio_count.setText(
            "Audio: 0"
        )

        self.document_count.setText(
            "Documents: 0"
        )

        self.archive_count.setText(
            "Archives: 0"
        )

        self.program_count.setText(
            "Programs: 0"
        )

        self.other_count.setText(
            "Others: 0"
        )


    # ========================================================
    # UPDATE DASHBOARD
    # ========================================================

    def update_dashboard(
        self,
        moved_files
    ):

        counts = Counter()


        for new_path, old_path in moved_files:

            new_path = Path(
                new_path
            )

            category = new_path.parent.name

            counts[category] += 1


        total = sum(
            counts.values()
        )


        self.total_value.setText(
            str(total)
        )


        self.image_count.setText(
            f"Images: {counts['Images']}"
        )

        self.video_count.setText(
            f"Videos: {counts['Videos']}"
        )

        self.audio_count.setText(
            f"Audio: {counts['Audio']}"
        )

        self.document_count.setText(
            f"Documents: {counts['Documents']}"
        )

        self.archive_count.setText(
            f"Archives: {counts['Archives']}"
        )

        self.program_count.setText(
            f"Programs: {counts['Programs']}"
        )

        self.other_count.setText(
            f"Others: {counts['Others']}"
        )


    # ========================================================
    # BROWSE
    # ========================================================

    def browse_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder"
        )


        if folder:

            self.path_input.setText(
                folder
            )

            self.status.setText(
                "Folder selected"
            )


    # ========================================================
    # PREVIEW
    # ========================================================

    def preview(self):

        folder = Path(
            self.path_input.text()
        )


        if not folder.exists() or not folder.is_dir():

            QMessageBox.warning(
                self,
                "Invalid Folder",
                "Please select a valid folder."
            )

            return


        results, _ = organize_files(
            folder,
            dry_run=True
        )


        self.output.clear()


        if not results:

            self.output.setText(
                "No files found."
            )

            self.status.setText(
                "No files found"
            )

            return


        self.output.setText(
            "\n\n".join(results)
        )


        self.status.setText(
            f"{len(results)} file(s) found"
        )


    # ========================================================
    # ORGANIZE
    # ========================================================

    def organize(self):

        folder = Path(
            self.path_input.text()
        )


        if not folder.exists() or not folder.is_dir():

            QMessageBox.warning(
                self,
                "Invalid Folder",
                "Please select a valid folder."
            )

            return


        answer = QMessageBox.question(
            self,
            "Confirm Organization",
            "Are you sure you want to organize these files?"
        )


        if answer != QMessageBox.StandardButton.Yes:

            return


        results, moved_files = organize_files(
            folder,
            dry_run=False
        )


        self.last_moves = moved_files


        self.output.clear()


        if not results:

            self.output.setText(
                "No files were moved."
            )

            self.status.setText(
                "Nothing to organize"
            )

            return


        self.output.setText(
            "\n\n".join(results)
        )


        self.update_dashboard(
            moved_files
        )


        self.status.setText(
            f"Successfully moved "
            f"{len(moved_files)} file(s)"
        )


    # ========================================================
    # UNDO
    # ========================================================

    def undo(self):

        if not self.last_moves:

            QMessageBox.information(
                self,
                "Nothing to Undo",
                "There is no recent organization to undo."
            )

            return


        results = undo_moves(
            self.last_moves
        )


        self.output.clear()


        self.output.setText(
            "\n".join(results)
        )


        self.status.setText(
            f"Restored "
            f"{len(self.last_moves)} file(s)"
        )


        self.last_moves = []


        self.reset_dashboard()


    # ========================================================
    # SETTINGS
    # ========================================================

    def open_settings(self):

        dialog = SettingsDialog(
            self
        )

        dialog.exec()


# ============================================================
# START APPLICATION
# ============================================================

app = QApplication(
    sys.argv
)


window = OrganizerApp()


window.show()


sys.exit(
    app.exec()
)