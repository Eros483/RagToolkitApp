import sys
from PySide6.QtWidgets import(
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog
)
from PySide6.QtCore import Qt, QThreadPool
from rag_backend import process_files, ask_model, RAGWorker

class RAGApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RAG Assistant")
        self.setMinimumSize(600, 400)

        layout=QVBoxLayout()

        self.query_label=QLabel("Enter your question: ")
        self.query_input=QLineEdit()

        self.file_button=QPushButton("Select PDF/JSON File")
        self.file_button.clicked.connect(self.pick_file)
        self.selected_files=[]

        self.run_button=QPushButton("Run Rag")
        self.run_button.clicked.connect(self.run_rag)

        self.output_box=QTextEdit()
        self.output_box.setReadOnly(True)

        layout.addWidget(self.query_label)
        layout.addWidget(self.query_input)
        layout.addWidget(self.file_button)
        layout.addWidget(self.run_button)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output_box)

        self.setLayout(layout)

        self.threadpool=QThreadPool()

    def pick_file(self):
        files, _=QFileDialog.getOpenFileNames(self, "Select Files", "", "Documents (*.pdf *.json)")
        if files:
            self.selected_files=files
            filenames=', '.join([f.split('/')[-1] for f in files])
            self.file_button.setText(f"Selected Files: {filenames}")

    def display_answer(self, answer):
        self.output_box.setText(answer)

    def display_error(self, error):
        self.output_box.setText(f"Error: {error}")

    def done_processing(self):
        print("RAG processing complete.")
        self.output_box.append("\nDone.")

    def run_rag(self):
        question=self.query_input.text()
        if not question:
            self.output_box.setText("Please enter a question.")
            return
        
        if not self.selected_files:
            self.output_box.setText("Please select a PDF or JSON file.")
            return
        
        self.output_box.setText("Processing... Please wait.")

        self.file_button.setEnabled(False)
        self.run_button.setEnabled(False)

        worker=RAGWorker(self.selected_files, question)
        worker.signals.result.connect(self.display_answer)
        worker.signals.error.connect(self.display_error)
        
        def reenable_buttons():
            self.file_button.setEnabled(True)
            self.run_button.setEnabled(True)
            self.done_processing()

        self.threadpool.start(worker)

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=RAGApp()
    window.show()
    sys.exit(app.exec())
