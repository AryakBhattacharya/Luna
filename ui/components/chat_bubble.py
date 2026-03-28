from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout


class ChatBubble(QWidget):
    def __init__(self, text, is_user=True):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(350)

        # 🎯 Typing bubble
        if text == "__typing__":
            self.label.setText("Luna is thinking...")
            self.label.setStyleSheet("""
                background-color: #121826;
                color: #9CA3AF;
                padding: 8px;
                border-radius: 10px;
                font-style: italic;
            """)
            layout.addWidget(self.label)
            layout.addStretch()

        # 🎯 User bubble
        elif is_user:
            self.label.setStyleSheet("""
                background-color: #3B82F6;
                color: white;
                padding: 8px;
                border-radius: 10px;
            """)
            layout.addStretch()
            layout.addWidget(self.label)

        # 🎯 Luna bubble
        else:
            self.label.setStyleSheet("""
                background-color: #121826;
                color: #E5E7EB;
                padding: 8px;
                border-radius: 10px;
            """)
            layout.addWidget(self.label)
            layout.addStretch()

        self.setLayout(layout)