import sys
from PySide6.QtWidgets import(
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QFormLayout, QSpinBox, QHBoxLayout, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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

        self.setup_ui()

    def setup_ui(self):
        main_layout=QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)

        self.setLayout(main_layout)

        left_side_panel_widget=QWidget()
        left_side_panel_layout=QVBoxLayout(left_side_panel_widget)
        left_side_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
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
        
        left_side_panel_layout.addStretch()

        self.reset_all_button=QPushButton("Reset Current Page")
        self.reset_all_button.setIcon(icon("reset.png"))
        self.reset_all_button.setStyleSheet(button_style)
        self.reset_all_button.clicked.connect(self.reset_current_page_chat)
        left_side_panel_layout.addWidget(self.reset_all_button)
        
        main_layout.addWidget(left_side_panel_widget, 1)

        self.stack=QStackedWidget()

        self.rag_page=RAGChatWidget()
        self.stack.addWidget(self.rag_page)

        self.evaluation_page=EvaluationChatWidget()
        self.stack.addWidget(self.evaluation_page)

        self.summarizer_page=SummarizerWidget()
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