from PyQt6.QtCore import QThread, pyqtSignal

class Worker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, controller, text):
        super().__init__()
        self.controller = controller
        self.text = text

    def run(self):
        response = self.controller.process_text(self.text)
        self.finished.emit(response)