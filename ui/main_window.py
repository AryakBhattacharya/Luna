from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from ui.controller import UIController

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = UIController()

        self.setWindowTitle("Luna")
        self.resize(500, 700)

        layout = QVBoxLayout()

        self.status = QLabel("Idle")
        layout.addWidget(self.status)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        layout.addWidget(self.chat)

        bottom = QHBoxLayout()

        self.input = QLineEdit()
        bottom.addWidget(self.input)

        self.send_btn = QPushButton("Send")
        bottom.addWidget(self.send_btn)

        self.mic_btn = QPushButton("🎤")
        bottom.addWidget(self.mic_btn)

        layout.addLayout(bottom)
        self.setLayout(layout)

        self.send_btn.clicked.connect(self.handle_text)
        self.mic_btn.clicked.connect(self.handle_voice)

    def handle_text(self):
        text = self.input.text()
        if not text:
            return

        self.chat.append(f"You: {text}")
        self.input.clear()

        self.status.setText("Thinking...")
        response = self.controller.process_text(text)

        self.chat.append(f"Luna: {response}")
        self.status.setText("Idle")

    def handle_voice(self):
        self.status.setText("Listening...")

        text, response = self.controller.process_voice()

        if text:
            self.chat.append(f"You: {text}")
        if response:
            self.chat.append(f"Luna: {response}")

        self.status.setText("Idle")