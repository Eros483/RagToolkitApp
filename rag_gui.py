import sys

from PySide6.QtWidgets import(
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QScrollArea, QTextBrowser, QSizePolicy
)

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QTextOption

from rag_backend import RAGWorker

class ChatBubble(QTextBrowser):
    def __init__(self, message, sender="user"):
        super().__init__()
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setWordWrapMode(QTextOption.WrapMode.WordWrap)

        line_height=self.fontMetrics().height()

        if sender=="user":
            self.setStyleSheet("""
                QTextBrowser{
                    background-color:#2e86de;
                    color:white;
                    border-radius:10px;
                    padding 8px;
                    border:none;
                }
            """)
            self.setMinimumHeight(int(line_height*1.5))
            self.setMaximumHeight(int(line_height*3.5))
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        else:
            self.setStyleSheet("""
                QTextBrowser{
                    background-color:#333;
                    color:#dcdcdc;
                    border-radius:10px;
                    padding:8px;
                    border: none;
                }
            """)
            self.setMinimumHeight(int(line_height * 3))
            self.setMaximumHeight(16777215)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setText(message)

class RAGChatWidget(QWidget):
    def __init__(self, max_tokens: int=512):
        super().__init__()

        self.setWindowTitle("Rag Chat Assistant")
        self.setMinimumSize(800, 600)
        self.conversation_history=[]
        self.max_tokens=max_tokens
        self.threadpool=QThreadPool()
        self.selected_files=[]

        self.setup_ui()

    def setup_ui(self):
        outer_layout=QHBoxLayout()

        main_chat_area_layout=QVBoxLayout()

        file_layout=QHBoxLayout()
        self.file_button=QPushButton("Select PDF Files")
        self.file_button.clicked.connect(self.pick_file)
        file_layout.addWidget(self.file_button)

        self.run_button=QPushButton("Run RAG")
        self.run_button.clicked.connect(self.run_rag)
        file_layout.addWidget(self.run_button)

        main_chat_area_layout.addLayout(file_layout)

        self.chat_scroll=QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_container=QWidget()
        self.chat_layout=QVBoxLayout()
        self.chat_container.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_container)
        self.chat_scroll.setStyleSheet("background-color: #1e1e1e;")

        main_chat_area_layout.addWidget(self.chat_scroll)

        # Input area
        input_layout=QHBoxLayout()
        self.query_input=QLineEdit()
        self.query_input.setPlaceholderText("Ask a question...")
        input_layout.addWidget(self.query_input)

        self.ask_button=QPushButton("Ask")
        self.ask_button.clicked.connect(self.run_rag)
        input_layout.addWidget(self.ask_button)

        main_chat_area_layout.addLayout(input_layout)

        outer_layout.addLayout(main_chat_area_layout, 4)
        
        self.setLayout(outer_layout)

    def pick_file(self):
        files, _=QFileDialog.getOpenFileNames(self, "select Files", "", "PDF Files (*.pdf);;JSON Files (*.json)")
        if files:
            self.selected_files=files
            self.file_button.setText(f"Selected Files: {len(files)}")
    
    def add_message(self, text, sender):
        bubble=ChatBubble(text, sender)
        h_layout=QHBoxLayout()

        if sender=="user":   
            h_layout.addStretch(1)
            h_layout.addWidget(bubble)
            h_layout.addStretch(0.2)
        
        else:
            h_layout.addStretch(0.2)
            h_layout.addWidget(bubble)
            h_layout.addStretch(1)

        self.chat_layout.addLayout(h_layout)
        self.chat_layout.addSpacing(5)
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    def display_error(self, error):
        self.add_message(f"Error:\n{error}", "assistant")

    def done_processing(self):
        print("RAG processing complete.")

    def run_rag(self):
        question=self.query_input.text().strip()
        if not question:
            self.add_message("Please enter a message.", "assistant")
            return

        if not self.selected_files:
            self.add_message("Please select a PDF or a JSON file.", "assistant")
            return
        
        self.ask_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.file_button.setEnabled(False)

        self.add_message(question, "user")
        worker=RAGWorker(self.selected_files, question, self.conversation_history, self.max_tokens)

        worker.signals.result.connect(self.update_chat)
        worker.signals.error.connect(self.display_error)
        worker.signals.finished.connect(self.reenable_buttons)

        self.threadpool.start(worker)

    def update_chat(self, result_tuple):
        answer, history=result_tuple
        self.conversation_history=history
        self.add_message(answer, "assistant")

    def reenable_buttons(self):
        self.ask_button.setEnabled(True)
        self.run_button.setEnabled(True)
        self.file_button.setEnabled(True)
        self.done_processing()

    def reset_chat(self): # Keep this method as it will be called from MainWindow
        while self.chat_layout.count():
            item=self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

        self.conversation_history=[]
    
    

