import sys

from PySide6.QtWidgets import(
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QScrollArea, QTextBrowser, QSizePolicy
)

from PySide6.QtCore import Qt, QThreadPool
from rag_backend import RAGWorker

class ChatBubble(QTextBrowser):
    def __init__(self, message, sender="user"):
        super().__init__()
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        if sender=="user":
            self.setStyleSheet("""
                QTextBrowser{
                    background-color:#2e86de;
                    color:white;
                    border-radius:10px;
                    padding 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QTextBrowser{
                    background-color:#333;
                    color:#dcdcdc;
                    border-radius:10px;
                    padding:8px;
                }
            """)

        self.setText(message)
        self.setMaximumWidth(500)
        self.setMinimumWidth(200)

class RAGApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rag Chat Assistant")
        self.setMinimumSize(700, 600)
        self.conversation_history=[]

        self.threadpool=QThreadPool()
        self.selected_files=[]

        self.setup_ui()

    def setup_ui(self):
        main_layout=QVBoxLayout()

        file_layout=QHBoxLayout()
        self.file_button=QPushButton("Select PDF/JSON Files")
        self.file_button.clicked.connect(self.pick_file)
        file_layout.addWidget(self.file_button)

        self.run_button=QPushButton("Run RAG")
        self.run_button.clicked.connect(self.run_rag)
        file_layout.addWidget(self.run_button)

        main_layout.addLayout(file_layout)

        self.chat_scroll=QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_container=QWidget()
        self.chat_layout=QVBoxLayout()
        self.chat_container.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_container)
        self.chat_scroll.setStyleSheet("background-color: #1e1e1e;")

        main_layout.addWidget(self.chat_scroll)

        # Input area
        input_layout=QHBoxLayout()
        self.query_input=QLineEdit()
        self.query_input.setPlaceholderText("Ask a question...")
        input_layout.addWidget(self.query_input)

        self.ask_button=QPushButton("Ask")
        self.ask_button.clicked.connect(self.run_rag)
        input_layout.addWidget(self.ask_button)

        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

    def pick_file(self):
        files, _=QFileDialog.getOpenFileNames(self, "select Files", "", "PDF Files (*.pdf);;JSON Files (*.json)")
        if files:
            self.selected_files=files
            self.file_button.setText(f"Selected Files: {len(files)}")
    
    def add_message(self, text, sender):
        bubble=ChatBubble(text, sender)
        self.chat_layout.addWidget(bubble)
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

        if not self.selected_files:
            self.add_message("Please select a PDF or a JSON file.", "assistant")
            return
        
        self.ask_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.file_button.setEnabled(False)

        self.add_message(question, "user")
        worker=RAGWorker(self.selected_files, question, self.conversation_history)

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


if __name__ == "__main__":
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

        QLineEdit{
            background-color:#1e1e1e;
            border:1px solid #444;
            padding:6px;
            color:white;
        }
    """)

    window=RAGApp()
    window.show()
    sys.exit(app.exec_())
