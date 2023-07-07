
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QColor

class ornekEkran(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("serkan bahtiyar")
        self.setGeometry(100, 100, 600, 600)
        self.setStyleSheet("background-color: blue")

        label = QLabel("al = input('testGerceklestir >girdi okuma işlemi')",self)
        label.setFixedSize(700, 20) 
      
        label.setGeometry(50, 50, 300, 50) 
        label.setStyleSheet("color: black; font-size:20px")

if __name__ == "__main__":
    app = QApplication([])
    baslangic_ekran = ornekEkran()
    baslangic_ekran.show()
    app.exec_()
#burda örnek bir veri girişinin terminalde nasıl olacağı gösterildi    