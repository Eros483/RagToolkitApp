import sys
from PySide6.QtWidgets import(
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QFormLayout, QSpinBox, QHBoxLayout, QStackedWidget, QSlider
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
import os

from rag_gui import RAGChatWidget

from evaluation_gui import EvaluationChatWidget

from summariser_gui import SummarizerWidget

if getattr(sys, 'frozen', False):
    # Running as a bundled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as a .py file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-App Dashboard")
        self.setMinimumSize(1000, 700)

        self.max_tokens_value=512
        self.setup_ui()

    def setup_ui(self):
        main_layout=QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        self.setLayout(main_layout)

        left_side_panel_widget=QWidget()
        left_side_panel_layout=QVBoxLayout(left_side_panel_widget)
        left_side_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join(BASE_DIR, "assets", "logo.png"))
        logo_pixmap = logo_pixmap.scaledToWidth(160, Qt.SmoothTransformation)  # Resize logo to fit panel width
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_side_panel_layout.addWidget(logo_label)

        left_side_panel_layout.setContentsMargins(10, 10, 10, 10)
        left_side_panel_layout.setSpacing(10)
        left_side_panel_widget.setFixedWidth(200)
        left_side_panel_widget.setStyleSheet("background-color: #021526;")

        button_style = """
            QPushButton {
                padding: 8px;
                font-size: 14px;
                border: none;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4b3a60;
            }
        """

        reset_button_style = """
            QPushButton {
                padding: 6px;
                font-size: 13px;
                border: 1px solid #3137fd; /* Border color updated */
                text-align: center;
                color: white; /* Text color updated to white */
                background-color: #3137fd; /* Background color updated */
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2a30e0; /* Slightly darker blue on hover */
                border: 1px solid #2a30e0;
            }
        """

        def icon(file_name):
            return QIcon(os.path.join(BASE_DIR, "assets", file_name))

        self.rag_button=QPushButton("RAG Chatbot")
        self.rag_button.setIcon(icon("chat_icon.png"))
        self.rag_button.setStyleSheet(button_style)
        self.rag_button.clicked.connect(self.show_rag_page)
        left_side_panel_layout.addWidget(self.rag_button)
        
        self.evaluation_button=QPushButton("Evaluation Assistant")
        self.evaluation_button.setIcon(icon("eval_icon.png"))
        self.evaluation_button.setStyleSheet(button_style)
        self.evaluation_button.clicked.connect(self.show_evaluation_page)
        left_side_panel_layout.addWidget(self.evaluation_button)

        self.summarizer_button=QPushButton("Document Summarizer")
        self.summarizer_button.setIcon(icon("business.png"))
        self.summarizer_button.setStyleSheet(button_style)
        self.summarizer_button.clicked.connect(self.show_summarizer_page)
        left_side_panel_layout.addWidget(self.summarizer_button)

        self.max_tokens_label = QLabel(f"Max Tokens: {self.max_tokens_value}")
        self.max_tokens_label.setStyleSheet("color: #dcdcdc; font-size: 12px; margin-top: 10px;")
        left_side_panel_layout.addWidget(self.max_tokens_label)

        self.max_tokens_slider=QSlider(Qt.Horizontal)
        self.max_tokens_slider.setMinimum(100)
        self.max_tokens_slider.setMaximum(4096)
        self.max_tokens_slider.setValue(self.max_tokens_value)
        self.max_tokens_slider.setTickPosition(QSlider.TicksBelow)
        self.max_tokens_slider.setTickInterval(500)
        self.max_tokens_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 8px;
                background: #2a2a2a;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #8FD6E1; /* Updated handle color */
                border: 1px solid #8FD6E1;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::add-page:horizontal {
                background: #555; /* Retained for contrast on the unfilled part */
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #8FD6E1; /* Updated filled part color */
                border-radius: 4px;
            }
        """)
        self.max_tokens_slider.valueChanged.connect(self.update_max_tokens)
        left_side_panel_layout.addWidget(self.max_tokens_slider)
        
        left_side_panel_layout.addStretch()

        self.reset_all_button=QPushButton("Clear")
        self.reset_all_button.setIcon(icon("reset.png"))
        self.reset_all_button.setStyleSheet(reset_button_style)
        self.reset_all_button.clicked.connect(self.reset_current_page_chat)
        left_side_panel_layout.addWidget(self.reset_all_button)
        
        main_layout.addWidget(left_side_panel_widget, 1)

        self.stack=QStackedWidget()

        self.rag_page=RAGChatWidget(max_tokens=self.max_tokens_value)
        self.stack.addWidget(self.rag_page)

        self.evaluation_page=EvaluationChatWidget(max_tokens=self.max_tokens_value)
        self.stack.addWidget(self.evaluation_page)

        self.summarizer_page=SummarizerWidget(max_tokens=self.max_tokens_value)
        self.stack.addWidget(self.summarizer_page)

        self.welcome_page=QWidget()
        welcome_layout=QVBoxLayout()
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.setContentsMargins(20, 20, 20, 20)

        self.welcome_title=QLabel("Welcome to RAG-Toolkit")
        self.welcome_title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.welcome_subtitle=QLabel("Created by Critical AI")
        self.welcome_subtitle.setStyleSheet("font-size: 14px; color: #aaa;")

        welcome_layout.addWidget(self.welcome_title)
        welcome_layout.addWidget(self.welcome_subtitle)
        self.welcome_page.setLayout(welcome_layout)

        self.stack.addWidget(self.welcome_page)

        self.stack.setCurrentWidget(self.welcome_page)
        main_layout.addWidget(self.stack, 4)

    def update_max_tokens(self, value):
        self.max_tokens_value=value
        self.max_tokens_label.setText(f"Max Tokens: {self.max_tokens_value}")

        self.rag_page.max_tokens = value
        self.evaluation_page.max_tokens = value
        self.summarizer_page.max_tokens = value

        print(f"Global max tokens updated to {value}")

    def show_rag_page(self):
        self.stack.setCurrentWidget(self.rag_page)

    def show_evaluation_page(self):
        self.stack.setCurrentWidget(self.evaluation_page)

    def show_summarizer_page(self):
        self.stack.setCurrentWidget(self.summarizer_page)

    def reset_current_page_chat(self):
        current_widget=self.stack.currentWidget()

        if hasattr(current_widget, 'reset_chat') and callable(current_widget.reset_chat):
            current_widget.reset_chat()
            print(f"Chat on {current_widget.windowTitle()} reset.")
        # For SummarizerWidget (which has specific clear logic)
        elif isinstance(current_widget, SummarizerWidget):
            current_widget.summary_output.clear()
            current_widget.summary_output.setPlaceholderText("Awaiting document selection and summary generation.")
            current_widget.file_label.setText("No files selected")
            current_widget.summarize_button.setEnabled(False)
            current_widget.selected_files = [] # Clear selected files list
            print("Summarizer output cleared.")
        # For the Welcome page (or any other page without specific reset logic)
        elif current_widget == self.welcome_page:
            print("Welcome page does not require reset.")
        else:
            print(f"Current page '{current_widget.windowTitle()}' does not have a specific reset method.")
if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget{
            font-family:Arial;
            font-size:14px;
            color:#fff;
            background-color:#121212;
        }

        QPushButton{
            background-color:#2e2e2e;
            color:white;
            border:1px solid #444;
            padding:6px;
        }

        QPushButton:hover{
            background-color:#3a3a3a;
        }
    """)

    window=MainWindow()
    window.show()
    sys.exit(app.exec())