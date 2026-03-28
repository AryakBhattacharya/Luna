from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QHBoxLayout, QScrollArea
)
from PyQt6.QtCore import QTimer
from ui.controller import UIController
from ui.components.chat_bubble import ChatBubble
from ui.worker import Worker


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = UIController()

        self.setWindowTitle("Luna")
        self.resize(500, 700)

        layout = QVBoxLayout()

        # Status
        self.status = QLabel("Idle")
        layout.addWidget(self.status)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()

        self.chat_container.setLayout(self.chat_layout)
        self.scroll.setWidget(self.chat_container)

        layout.addWidget(self.scroll)

        # Bottom bar
        bottom = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message...")
        bottom.addWidget(self.input)

        self.send_btn = QPushButton("Send")
        bottom.addWidget(self.send_btn)

        self.mic_btn = QPushButton("🎤")
        bottom.addWidget(self.mic_btn)

        layout.addLayout(bottom)
        self.setLayout(layout)

        # Events
        self.send_btn.clicked.connect(self.handle_text)
        self.input.returnPressed.connect(self.handle_text)

    # ------------------------
    # Typing Bubble
    # ------------------------
    def show_typing(self):
        self.typing_bubble = ChatBubble("__typing__", False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.typing_bubble)

        self.chat_container.adjustSize()
        QTimer.singleShot(10, self.scroll_to_bottom)

    def remove_typing(self):
        if hasattr(self, "typing_bubble"):
            self.typing_bubble.setParent(None)
            self.typing_bubble.deleteLater()

    # ------------------------
    # TEXT INPUT (THREADING)
    # ------------------------
    def handle_text(self):
        text = self.input.text()
        if not text:
            return

        self.add_message(text, True)
        self.input.clear()

        self.status.setText("Thinking...")
        self.show_typing()

        self.worker = Worker(self.controller, text)
        self.worker.finished.connect(self.on_response)
        self.worker.start()

    # ------------------------
    # RESPONSE HANDLER
    # ------------------------
    def on_response(self, response):
        self.remove_typing()

        if isinstance(response, list):
            for r in response:
                self.typewriter_effect(r)
        else:
            self.typewriter_effect(response)

        self.status.setText("Idle")

    # ------------------------
    # TYPEWRITER EFFECT
    # ------------------------
    def typewriter_effect(self, text):
        bubble = ChatBubble("", False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)

        self.current_text = ""
        self.full_text = text
        self.current_index = 0

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self._update_typing(bubble))
        self.timer.start(15)

    def _update_typing(self, bubble):
        if self.current_index < len(self.full_text):
            self.current_text += self.full_text[self.current_index]
            bubble.label.setText(self.current_text)
            self.current_index += 1

            self.scroll_to_bottom()
        else:
            self.timer.stop()

    # ------------------------
    # ADD MESSAGE
    # ------------------------
    def add_message(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)

        # 🔥 force layout update first
        self.chat_container.adjustSize()

        # 🔥 delayed scroll (slightly longer delay)
        QTimer.singleShot(10, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        QTimer.singleShot(0, self._do_scroll)

    def _do_scroll(self):
        scrollbar = self.scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())