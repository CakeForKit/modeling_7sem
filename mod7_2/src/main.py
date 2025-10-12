import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import numpy as np
from mproc import calc_stabilization_times_and_probability, plot_results_per_state, print_detailed_analysis

UI_MAINWINDOW_PATH = "./mod7_2/ui/main_window.ui"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_MAINWINDOW_PATH, self)
        self.setWindowTitle("Марковский процесс")
        self.setGeometry(200, 100, 1000, 500)
        
        # Инициализация таблиц
        self.lambda_model = QStandardItemModel()
        self.lambda_tab.setModel(self.lambda_model)
        
        self.res_model = QStandardItemModel()
        self.res_tab.setModel(self.res_model)
        
        # Установка начального размера матрицы
        self.matrix_size_sbox.valueChanged.connect(self.change_matrix_size)
        self.initialize_matrix()  # Инициализация начального размера
        
        self.calc_btn.clicked.connect(self.calc)
        self.exit_pbtn.aboutToShow.connect(self.exit)
    
    def initialize_matrix(self):
        rows, cols = 2, 2
        self.lambda_model.setRowCount(rows)
        self.lambda_model.setColumnCount(cols)
        
        # Заполняем нулями
        for row in range(rows):
            for col in range(cols):
                if row == col:
                    item = QStandardItem("")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.lambda_model.setItem(row, col, item)
                else:
                    item = QStandardItem("0.0")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.lambda_model.setItem(row, col, item)
                
        
        # Настраиваем заголовки
        self.lambda_model.setHorizontalHeaderLabels([str(i+1) for i in range(cols)])
        
        # Настраиваем растяжение столбцов
        header = self.lambda_tab.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
    def change_matrix_size(self):
        new_size = self.matrix_size_sbox.value()
        
        # Сохраняем текущие данные
        old_data = []
        current_rows = self.lambda_model.rowCount()
        current_cols = self.lambda_model.columnCount()
        
        if current_rows > 0 and current_cols > 0:
            for row in range(min(current_rows, new_size)):
                row_data = []
                for col in range(min(current_cols, new_size)):
                    item = self.lambda_model.item(row, col)
                    if item and item.text():
                        try:
                            row_data.append(float(item.text()))
                        except ValueError:
                            row_data.append(0.0)
                    else:
                        row_data.append(0.0)
                old_data.append(row_data)
        
        # Устанавливаем новый размер модели
        self.lambda_model.setRowCount(new_size)
        self.lambda_model.setColumnCount(new_size)
        
        # Восстанавливаем данные
        for row in range(new_size):
            for col in range(new_size):
                if row == col:
                    item = QStandardItem("")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.lambda_model.setItem(row, col, item)
                else:
                    item = QStandardItem("0.0")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.lambda_model.setItem(row, col, item)

        for row in range(min(len(old_data), new_size)):
            for col in range(min(len(old_data[row]), new_size)):
                if row != col:
                    item = QStandardItem(str(old_data[row][col]))
                    self.lambda_model.setItem(row, col, item)
        
        # Настраиваем заголовки
        self.lambda_model.setHorizontalHeaderLabels([f"{i+1}" for i in range(new_size)])
        self.lambda_model.setVerticalHeaderLabels([f"{i+1}" for i in range(new_size)])
        
        # Настраиваем растяжение столбцов
        header = self.lambda_tab.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
    
    def get_matrix_from_table(self):
        """Получает матрицу из таблицы"""
        size = self.matrix_size_sbox.value()
        matrix = np.zeros((size, size))
        
        for row in range(size):
            for col in range(size):
                item = self.lambda_model.item(row, col)
                if item and item.text():
                    try:
                        matrix[row, col] = float(item.text())
                    except ValueError:
                        matrix[row, col] = 0.0
        
        return matrix
    
    def update_result_table(self, p_stationary, settling_time):
        """Обновляет таблицу с результатами"""
        size = len(p_stationary)
        
        # Очищаем модель
        self.res_model.clear()
        self.res_model.setRowCount(size) 
        self.res_model.setColumnCount(2)
        
        # Устанавливаем заголовки
        self.res_model.setHorizontalHeaderLabels(["Предельная вероятность", "Время стабилизации"])
        self.res_model.setVerticalHeaderLabels([f"S{i+1}" for i in range(size)])
        
        # Заполняем стационарные вероятности
        for i in range(size):            
            # Значение вероятности
            prob_item = QStandardItem(f"{p_stationary[i]:.4f}")
            prob_item.setFlags(prob_item.flags() & ~Qt.ItemIsEditable)
            prob_item.setTextAlignment(Qt.AlignCenter)
            self.res_model.setItem(i, 0, prob_item)

            # Добавляем время стабилизации
            time_item = QStandardItem(f"{settling_time[i]:.4f}")
            prob_item.setFlags(prob_item.flags() & ~Qt.ItemIsEditable)
            time_item.setTextAlignment(Qt.AlignCenter)
            self.res_model.setItem(i, 1, time_item)
        
        # Настраиваем растяжение столбцов
        header = self.res_tab.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

    def calc(self):
        try:
            lambda_matrix = self.get_matrix_from_table()
            if np.all(lambda_matrix == 0):
                self.statusbar.showMessage("Ошибка: матрица интенсивностей не заполнена или заполнена неверно!")
                return
            print("Матрица интенсивностей:")
            print(lambda_matrix)
            
            # Вычисляем результаты
            solution, settling_time, p_stationary = calc_stabilization_times_and_probability(Lambda=lambda_matrix)
            self.update_result_table(p_stationary, settling_time)

            # plot_results_per_state(solution, settling_time, p_stationary)
            print_detailed_analysis(solution, p_stationary)
            self.statusbar.showMessage("Расчет завершен успешно!")
            
        except Exception as e:
            self.statusbar.showMessage(f"Ошибка при расчете: {str(e)}")
            print(f"Ошибка: {e}")

    def exit(self):
        sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    