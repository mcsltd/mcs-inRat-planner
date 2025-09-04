from PySide6.QtWidgets import QMainWindow, QApplication


from ui.main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("InRat")





if __name__ == "__main__":

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()