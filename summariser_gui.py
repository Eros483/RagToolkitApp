import sys

from PySide6.QtWidgets import(
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QScrollArea, QTextBrowser, QSizePolicy
)

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QTextOption

from summariser_backend import SummarizationWorker

class SummarizerWidget(QWidget):
    def __init__(self, max_tokens: int=512):
        super().__init__()

        self.setWindowTitle("Document Summarization")
        self.setMinimumSize(800, 600)
        self.max_tokens=max_tokens

        self.threadpool=QThreadPool()
        self.selected_files=[]

        self.setup_ui()

    def setup_ui(self):
        main_layout=QVBoxLayout()
        self.setLayout(main_layout)

        file_selection_layout=QHBoxLayout()
        self.file_button=QPushButton("Select Document for Summary")
        self.file_button.clicked.connect(self.pick_file)
        file_selection_layout.addWidget(self.file_button)

        self.file_label=QLabel("No files selected")
        file_selection_layout.addWidget(self.file_label)
        file_selection_layout.addStretch(1)

        self.summarize_button=QPushButton("Generate Summary")
        self.summarize_button.clicked.connect(self.start_summarization)
        self.summarize_button.setEnabled(False)
        file_selection_layout.addWidget(self.summarize_button)
        main_layout.addLayout(file_selection_layout)

        self.summary_output=QTextBrowser()
        self.summary_output.setPlaceholderText("Awaiting PDF selection and subsequent summarization")
        self.summary_output.setStyleSheet("""
            QTextBrowser{
                background-color:#1e1e1e;
                color:#dcdcdc;
                border:1px solid #444;
                border-radius:5px;
                padding:8px;
            }
        """)
        main_layout.addWidget(self.summary_output)

    def pick_file(self):
        files, _=QFileDialog.getOpenFileNames(self, "select Files", "", "PDF Files (*.pdf);;JSON Files (*.json)")
        if files:
            self.selected_files=files
            self.file_button.setText(f"Selected Files: {len(files)}")
            self.summarize_button.setEnabled(True)
            self.summary_output.clear()
        else:
            self.selected_files=[]
            self.file_button.setText("Select Document for Summary")
            self.summarize_button.setEnabled(False)

    def display_error(self, error):
        self.summary_output.setText(f"Error: \n<pre>{error}</pre>")
        self.reenable_buttons()

    def done_processing(self):
        print("Summarization complete.")

    def start_summarization(self):
        if not self.selected_files:
            self.summary_output.setText("Please select a document to summarize")
            return
        
        self.summarize_button.setEnabled(False)
        self.file_button.setEnabled(False)
        self.summary_output.setPlaceholderText("Generating summary....")
        self.summary_output.clear()

        worker=SummarizationWorker(filepaths=self.selected_files, max_tokens=self.max_tokens)

        worker.signals.result.connect(self.display_summary)
        worker.signals.error.connect(self.display_error)
        worker.signals.finished.connect(self.summarization_finished)

        self.threadpool.start(worker)

    def display_summary(self, summary_text):
        self.summary_output.setText(summary_text)

    def summarization_finished(self):
        self.summarize_button.setEnabled(True)
        self.file_button.setEnabled(True)
        self.summary_output.setPlaceholderText("Awaiting PDF selection and subsequent summarization")
        self.done_processing()

