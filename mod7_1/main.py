import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import random

from criterion import combined_randomness_criterion

UI_MAINWINDOW_PATH = "./mod7_1/ui/main_window.ui"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_MAINWINDOW_PATH, self)
        self.setWindowTitle("Критерий случайности чисел")
        self.setGeometry(200, 100, 1000, 500)
        
        # Инициализация таблицы
        self.CntRows = 10
        tab1 = [8, 4, 3, 7, 2, 6, 1, 5, 9, 3]
        tab2 = [87, 40, 21, 96, 50, 74, 13, 89, 25, 60]
        tab3 = [174, 829, 365, 207, 941, 853, 620, 971, 483, 502]
        alg1 = [random.randint(0, 9) for _ in range(self.CntRows)]
        alg2 = [random.randint(10, 99) for _ in range(self.CntRows)]
        alg3 = [random.randint(100, 999) for _ in range(self.CntRows)]
        self.tableData = [tab1, tab2, tab3, alg1, alg2, alg3]
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
        total_columns = self.model.columnCount()
        user_columns_start = 6  # Пользовательские столбцы начинаются с 6-го (индекс 5)
        if total_columns <= user_columns_start:
            print("Нет пользовательских столбцов для пересчета")
            return
        for col in range(user_columns_start, total_columns):
            user_data = []
            empty_cells = 0
            filled_cells = 0
            
            result_text = ""
            for row in range(self.CntRows):
                item = self.model.item(row, col)
                if item and item.text().strip():  # Если ячейка не пустая
                    try:
                        value = int(item.text())
                        user_data.append(value)
                        filled_cells += 1
                    except ValueError:
                        result_text = "error (not integer)"
                        empty_cells += 1
                else:
                    empty_cells += 1
            
            if result_text == "":
                if filled_cells == 0:
                    result_text = "error (empty)"
                elif empty_cells > 0:
                    if len(user_data) >= 3:  # Нужно минимум 3 точки для расчета
                        criterion_value = combined_randomness_criterion(user_data)
                        result_text = f"{criterion_value}% (partial)"
                    else:
                        result_text = "error (need 3+ values)"
                else:
                    criterion_value = combined_randomness_criterion(user_data)
                    result_text = f"{criterion_value}%"
            
            last_row = self.model.rowCount() - 1
            if last_row >= 0:
                result_item = QStandardItem(result_text)
                result_item.setFlags(result_item.flags() & ~Qt.ItemIsEditable)  # Только чтение
                self.model.setItem(last_row, col, result_item)
            else:
                row_items = [QStandardItem("") for _ in range(total_columns)]
                row_items[col] = QStandardItem(result_text)
                row_items[col].setFlags(row_items[col].flags() & ~Qt.ItemIsEditable)
                self.model.appendRow(row_items)


    def initTable(self):
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.model = QStandardItemModel(0, 6, self)  # 0 строк, 6 столбцов
        self.model.setHorizontalHeaderLabels(
            [f"Табл. {i+1} разр." for i in range(3)] + 
            [f"Алг. {i+1}разр." for i in range(3)]
        )
        self.tableView.setModel(self.model)
        
        # Заполняем таблицу случайными числами
        for ri in range(self.CntRows):
            row_items = [self.tableData[i][ri] for i in range(len(self.tableData))]
            self.model.appendRow([QStandardItem(str(el)) for el in row_items])
        
        rowCriterion = list()
        for ci in range(len(self.tableData)):
            rowCriterion.append(combined_randomness_criterion(self.tableData[ci]))
        self.model.appendRow([QStandardItem(f"{el}%") for el in rowCriterion])

        # Делаем первые 6 столбцов только для чтения
        for col in range(6):
            for row in range(self.model.rowCount()):
                item = self.model.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def exit(self):
        sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    