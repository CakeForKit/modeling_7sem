import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

UI_MAINWINDOW_PATH = "./mod7_1/ui/main_window.ui"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_MAINWINDOW_PATH, self)
        self.setWindowTitle("PyQt5 в WSL2")
        self.setGeometry(200, 100, 1000, 500)
        
        # Инициализация таблицы
        self.initTable()

        self.add_column_btn.clicked.connect(self.addColumn)
        self.calc_btn.clicked.connect(self.calc)
        self.exit_pbtn.aboutToShow.connect(self.exit)
    
    def addColumn(self):
        # Получаем текущее количество столбцов
        current_col_count = self.model.columnCount()
        
        # Добавляем новый столбец
        self.model.setColumnCount(current_col_count + 1)
        self.model.setHorizontalHeaderItem(current_col_count, QStandardItem(f"Пользовательский {current_col_count - 5}"))
        
        # Заполняем новый столбец пустыми значениями
        for row in range(self.model.rowCount()):
            item = QStandardItem("")
            # Разрешаем редактирование только для нового столбца
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.model.setItem(row, current_col_count, item)
        
        # Прокручиваем таблицу к новому столбцу
        self.tableView.scrollTo(self.model.index(0, current_col_count))
    
    def calc(self):
        # пересчет 
        return

    def initTable(self):
        # Создаем модель данных
        self.model = QStandardItemModel(0, 6, self)  # 0 строк, 6 столбцов
        self.model.setHorizontalHeaderLabels([f"Столбец {i+1}" for i in range(6)])
        
        # Устанавливаем модель в таблицу
        self.tableView.setModel(self.model)
        
        # Заполняем таблицу случайными числами
        self.fillTableWithRandomNumbers()
        
        # Делаем первые 6 столбцов только для чтения
        for col in range(6):
            for row in range(self.model.rowCount()):
                item = self.model.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def fillTableWithRandomNumbers(self):
        import random
        
        # Добавляем 10 строк с случайными числами
        for row in range(10):
            row_items = []
            for col in range(6):
                # Генерируем случайное число от 1 до 100
                random_number = random.randint(1, 100)
                item = QStandardItem(str(random_number))
                row_items.append(item)
            self.model.appendRow(row_items)

    def exit(self):
        sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    