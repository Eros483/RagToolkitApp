import sys
from PySide6.QtWidgets import(
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QFormLayout, QSpinBox, QHBoxLayout, QStackedWidget
)
from PySide6.QtCore import Qt

from rag_gui import RAGChatWidget

from evaluation_gui import EvaluationChatWidget

from summariser_gui import SummarizerWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-App Dashboard")
        self.setMinimumSize(1200, 800)

        self.setup_ui()

    def setup_ui(self):
        main_layout=QHBoxLayout()
        self.setLayout(main_layout)

        left_side_panel_widget=QWidget()
        left_side_panel_layout=QVBoxLayout(left_side_panel_widget)
        left_side_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_side_panel_widget.setStyleSheet("background-color: #3F3351;")

        self.rag_button=QPushButton("RAG Chatbot")
        self.rag_button.clicked.connect(self.show_rag_page)
        left_side_panel_layout.addWidget(self.rag_button)
        
        self.evaluation_button=QPushButton("Evaluation Assistant")
        self.evaluation_button.clicked.connect(self.show_evaluation_page)
        left_side_panel_layout.addWidget(self.evaluation_button)

        self.summarizer_button=QPushButton("Document Summarizer")
        self.summarizer_button.clicked.connect(self.show_summarizer_page)
        left_side_panel_layout.addWidget(self.summarizer_button)
        
        left_side_panel_layout.addStretch()
        
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

        self.welcome_title=QLabel("Welcome to RAG-Toolkit")
        self.welcome_title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.welcome_subtitle=QLabel("Created by Critical AI")
        self.welcome_subtitle.setStyleSheet("font-size: 16px; color: #aaa;")

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