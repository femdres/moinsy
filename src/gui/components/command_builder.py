from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QScrollArea, QWidget, QGridLayout,
    QLineEdit, QCheckBox, QTabWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
import os
import json

class CommandBuilder(QDialog):
    """Dialog window for building and learning Linux commands"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Command Builder")
        self.setMinimumSize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with title and close button
        self.setup_header(layout)

        # Main content area with categories, commands, and details
        self.setup_content_area(layout)

        # Command playground at the bottom
        self.setup_command_playground(layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #1e293b;
                color: white;
            }
            QFrame {
                border-radius: 8px;
                background-color: #334155;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QLineEdit {
                border-radius: 4px;
                padding: 8px;
                background-color: #1e293b;
                color: #4ade80;
                border: none;
            }
        """)

    def setup_header(self, layout):
        """Setup the header with title and close button"""
        header_layout = QHBoxLayout()

        title = QLabel("Command Builder")
        title.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #4ade80;")
        header_layout.addWidget(title)

        subtitle = QLabel("Build and learn Linux commands with proper syntax and options")
        subtitle.setStyleSheet("color: #94a3b8;")
        header_layout.addWidget(subtitle)

        header_layout.addStretch()

        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setFont(QFont('Segoe UI', 16))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        close_button.clicked.connect(self.close)
        header_layout.addWidget(close_button)

        layout.addLayout(header_layout)

    def setup_content_area(self, layout):
        """Setup the main content area with categories, commands, and details"""
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # Left panel - Categories
        category_frame = QFrame()
        category_layout = QVBoxLayout(category_frame)

        category_label = QLabel("Command Categories")
        category_label.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        category_label.setStyleSheet("color: #94a3b8;")
        category_layout.addWidget(category_label)

        self.category_list = QListWidget()
        self.category_list.setStyleSheet("""
            QListWidget {
                background-color: #334155;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 4px;
            }
            QListWidget::item:selected {
                background-color: #475569;
                color: #4ade80;
            }
            QListWidget::item:hover {
                background-color: #475569;
            }
        """)

        # Load categories from JSON
        commands_data = self.load_commands_json()
        categories = []

        for category in commands_data.get("categories", []):
            categories.append((
                f"{category.get('icon', '⚙️')} {category.get('name', 'Unknown')}",
                category.get('id', 'unknown')
            ))

        # Add categories with icons
        for label, data in categories:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.category_list.addItem(item)

        self.category_list.setCurrentRow(0)
        self.category_list.currentItemChanged.connect(self.on_category_changed)
        category_layout.addWidget(self.category_list)

        category_frame.setFixedWidth(200)
        content_layout.addWidget(category_frame)

        # Middle panel - Commands
        command_frame = QFrame()
        command_layout = QVBoxLayout(command_frame)

        command_label = QLabel("Available Commands")
        command_label.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        command_label.setStyleSheet("color: #94a3b8;")
        command_layout.addWidget(command_label)

        command_search = QLineEdit()
        command_search.setPlaceholderText("Search commands...")
        command_search.textChanged.connect(self.filter_commands)
        command_layout.addWidget(command_search)

        self.command_list = QListWidget()
        self.command_list.setStyleSheet("""
            QListWidget {
                background-color: #334155;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 4px;
            }
            QListWidget::item:selected {
                background-color: #064e3b;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #475569;
            }
        """)

        self.command_list.currentItemChanged.connect(self.on_command_changed)
        command_layout.addWidget(self.command_list)

        command_frame.setFixedWidth(220)
        content_layout.addWidget(command_frame)

        # Right panel - Command details
        details_frame = QFrame()
        self.details_layout = QVBoxLayout(details_frame)

        details_label = QLabel("Command Details")
        details_label.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        details_label.setStyleSheet("color: #94a3b8;")
        self.details_layout.addWidget(details_label)

        # Tab widget for command details
        self.details_tabs = QTabWidget()
        self.details_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #334155;
            }
            QTabBar::tab {
                background-color: #475569;
                color: #94a3b8;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #334155;
                color: white;
            }
        """)

        # Create tabs for different sections
        self.usage_tab = QWidget()
        self.options_tab = QWidget()
        self.examples_tab = QWidget()

        self.details_tabs.addTab(self.usage_tab, "Usage")
        self.details_tabs.addTab(self.options_tab, "Options")
        self.details_tabs.addTab(self.examples_tab, "Examples")

        # Setup individual tab content
        self.setup_usage_tab()
        self.setup_options_tab()
        self.setup_examples_tab()

        self.details_layout.addWidget(self.details_tabs)
        content_layout.addWidget(details_frame, 1)  # Give more space to details

        layout.addLayout(content_layout)

    def setup_usage_tab(self):
        """Setup the Usage tab content"""
        layout = QVBoxLayout(self.usage_tab)

        # Description section
        desc_label = QLabel("Description")
        desc_label.setStyleSheet("color: #94a3b8; font-weight: bold;")
        layout.addWidget(desc_label)

        self.description_text = QLabel("Select a command to view its description.")
        self.description_text.setWordWrap(True)
        self.description_text.setStyleSheet("color: white; margin-bottom: 16px;")
        layout.addWidget(self.description_text)

        # Syntax section
        syntax_label = QLabel("Basic Syntax")
        syntax_label.setStyleSheet("color: #94a3b8; font-weight: bold;")
        layout.addWidget(syntax_label)

        self.syntax_frame = QFrame()
        self.syntax_frame.setStyleSheet("background-color: #1e293b; padding: 8px;")
        syntax_layout = QVBoxLayout(self.syntax_frame)

        self.syntax_text = QLabel("Command syntax will appear here.")
        self.syntax_text.setStyleSheet("color: #4ade80; font-family: 'Consolas', 'Courier New', monospace;")
        syntax_layout.addWidget(self.syntax_text)

        layout.addWidget(self.syntax_frame)
        layout.addStretch()

    def setup_options_tab(self):
        """Setup the Options tab content"""
        layout = QVBoxLayout(self.options_tab)

        options_intro = QLabel("Command options and flags:")
        options_intro.setStyleSheet("color: #94a3b8;")
        layout.addWidget(options_intro)

        # Options grid
        self.options_grid = QGridLayout()
        self.options_grid.setSpacing(10)
        layout.addLayout(self.options_grid)

        # Placeholder text when no command is selected
        self.options_placeholder = QLabel("Select a command to view available options.")
        self.options_placeholder.setStyleSheet("color: #94a3b8; padding: 20px;")
        self.options_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.options_placeholder)

        layout.addStretch()

    def setup_examples_tab(self):
        """Setup the Examples tab content"""
        layout = QVBoxLayout(self.examples_tab)

        examples_intro = QLabel("Common usage examples:")
        examples_intro.setStyleSheet("color: #94a3b8;")
        layout.addWidget(examples_intro)

        # Examples container
        self.examples_container = QWidget()
        self.examples_layout = QVBoxLayout(self.examples_container)

        layout.addWidget(self.examples_container)

        # Placeholder text when no command is selected
        self.examples_placeholder = QLabel("Select a command to view usage examples.")
        self.examples_placeholder.setStyleSheet("color: #94a3b8; padding: 20px;")
        self.examples_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.examples_placeholder)

        layout.addStretch()

    def setup_command_playground(self, layout):
        """Setup the command playground section"""
        playground_frame = QFrame()
        playground_layout = QVBoxLayout(playground_frame)

        # Title
        playground_label = QLabel("Command Playground")
        playground_label.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        playground_label.setStyleSheet("color: #94a3b8;")
        playground_layout.addWidget(playground_label)

        # Command input with terminal style
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #1e293b; border-radius: 4px;")
        input_layout = QHBoxLayout(input_frame)

        prompt_label = QLabel("$")
        prompt_label.setStyleSheet(
            "color: #a78bfa; font-family: 'Consolas', 'Courier New', monospace; font-weight: bold;")
        input_layout.addWidget(prompt_label)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Build your command here...")
        self.command_input.setStyleSheet("""
            background-color: transparent;
            color: #4ade80;
            border: none;
            font-family: 'Consolas', 'Courier New', monospace;
        """)
        input_layout.addWidget(self.command_input)

        playground_layout.addWidget(input_frame)

        # Buttons and options
        buttons_layout = QHBoxLayout()

        copy_button = QPushButton("Copy Command")
        copy_button.setStyleSheet("""
            background-color: #3b82f6;
            color: white;
        """)
        copy_button.clicked.connect(self.copy_command)
        buttons_layout.addWidget(copy_button)

        execute_button = QPushButton("Execute Command")
        execute_button.setStyleSheet("""
            background-color: #4ade80;
            color: white;
        """)
        execute_button.clicked.connect(self.execute_command)
        buttons_layout.addWidget(execute_button)

        self.sudo_checkbox = QCheckBox("Run with sudo (requires password)")
        self.sudo_checkbox.setStyleSheet("color: white;")
        buttons_layout.addWidget(self.sudo_checkbox)

        playground_layout.addLayout(buttons_layout)
        layout.addWidget(playground_frame)

    def load_commands_json(self):
        """Load commands data from JSON file"""
        try:
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     "resources", "data", "commands.json")
            with open(json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading commands JSON: {str(e)}")
            return {"categories": []}

    def load_commands_for_category(self, category_id):
        """Load commands for the selected category from JSON file"""
        self.command_list.clear()

        # Get commands data from JSON
        commands_data = self.load_commands_json()

        # Find the selected category
        selected_category = None
        for category in commands_data.get("categories", []):
            if category.get("id") == category_id:
                selected_category = category
                break

        # If category found, add its commands to the list
        if selected_category and "commands" in selected_category:
            for cmd in selected_category.get("commands", []):
                item = QListWidgetItem(f"{cmd['name']}")
                font = QFont('Consolas', 10)
                item.setFont(font)
                # Store command data for display
                item.setData(Qt.ItemDataRole.UserRole, cmd)
                # Create a tool tip with description
                item.setToolTip(cmd.get("description", ""))
                self.command_list.addItem(item)

    def display_command_details(self, command_name):
        """Display details for the selected command from JSON data"""
        # Load commands data
        commands_data = self.load_commands_json()

        # Find command data
        selected_command = None
        for category in commands_data.get("categories", []):
            for cmd in category.get("commands", []):
                if cmd.get("name") == command_name:
                    selected_command = cmd
                    break
            if selected_command:
                break

        if selected_command:
            # Update description
            self.description_text.setText(selected_command.get("description", "No description available."))

            # Update syntax
            self.syntax_text.setText(selected_command.get("syntax", f"{command_name} [options] [arguments]"))

            # Update options
            self.clear_options_grid()
            self.options_placeholder.setVisible(False)

            options = selected_command.get("options", [])
            for i, option in enumerate(options):
                option_frame = QFrame()
                option_frame.setStyleSheet("background-color: #1e293b; border-radius: 4px; padding: 6px;")
                option_layout = QVBoxLayout(option_frame)

                flag = option.get("flag", "")
                description = option.get("description", "")

                option_name = QLabel(flag)
                option_name.setStyleSheet("color: #fbbf24; font-family: 'Consolas', 'Courier New', monospace;")
                option_layout.addWidget(option_name)

                option_desc = QLabel(description)
                option_desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
                option_desc.setWordWrap(True)
                option_layout.addWidget(option_desc)

                row = i // 2
                col = i % 2
                self.options_grid.addWidget(option_frame, row, col)

            # Update examples
            examples = [(ex.get("command", ""), ex.get("description", ""))
                        for ex in selected_command.get("examples", [])]
            self.update_examples(examples)
        else:
            # Show default content for unknown command
            self.description_text.setText(f"Description for '{command_name}' command not found.")
            self.syntax_text.setText(f"{command_name} [options] [arguments]")
            self.clear_options_grid()
            self.options_placeholder.setVisible(True)
            self.examples_placeholder.setVisible(True)
            self.examples_container.setVisible(False)

    def on_category_changed(self, current, previous):
        """Handle category selection change"""
        if current:
            category_id = current.data(Qt.ItemDataRole.UserRole)
            self.load_commands_for_category(category_id)
            # Reset command selection
            self.clear_command_details()

    def on_command_changed(self, current, previous):
        """Handle command selection change"""
        if current:
            cmd_data = current.data(Qt.ItemDataRole.UserRole)
            self.display_command_details(cmd_data["name"])
            # Auto-fill command in playground
            self.command_input.setText(cmd_data["name"] + " ")

    def clear_options_grid(self):
        """Clear the options grid layout"""
        # Remove all widgets from the grid
        while self.options_grid.count():
            item = self.options_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_examples(self, examples):
        """Update the examples tab with provided examples"""
        # Clear previous examples
        while self.examples_layout.count():
            item = self.examples_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.examples_placeholder.setVisible(False)
        self.examples_container.setVisible(True)

        # Add new examples
        for cmd, desc in examples:
            example_frame = QFrame()
            example_frame.setStyleSheet("background-color: #1e293b; border-radius: 4px; margin-bottom: 8px;")
            example_layout = QVBoxLayout(example_frame)

            cmd_label = QLabel(cmd)
            cmd_label.setStyleSheet("color: #4ade80; font-family: 'Consolas', 'Courier New', monospace;")
            example_layout.addWidget(cmd_label)

            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
            desc_label.setWordWrap(True)
            example_layout.addWidget(desc_label)

            self.examples_layout.addWidget(example_frame)

        self.examples_layout.addStretch()

    def clear_command_details(self):
        """Clear command details when no command is selected"""
        self.description_text.setText("Select a command to view its description.")
        self.syntax_text.setText("Command syntax will appear here.")

        # Clear options
        self.clear_options_grid()
        self.options_placeholder.setVisible(True)

        # Clear examples
        while self.examples_layout.count():
            item = self.examples_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.examples_placeholder.setVisible(True)
        self.examples_container.setVisible(False)

    def filter_commands(self, text):
        """Filter commands based on search text"""
        for i in range(self.command_list.count()):
            item = self.command_list.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def copy_command(self):
        """Copy the command to clipboard"""
        command = self.command_input.text()
        if command:
            clipboard = self.parent().clipboard() if self.parent() else None
            if clipboard:
                clipboard.setText(command)

    def execute_command(self):
        """Execute the command in terminal"""
        command = self.command_input.text()
        if command:
            # Here you would typically send the command to a terminal
            # or execute it via subprocess
            use_sudo = self.sudo_checkbox.isChecked()
            full_command = f"sudo {command}" if use_sudo else command
            print(f"Executing: {full_command}")
            # For a real implementation, you would connect this to your terminal or
            # execute via subprocess