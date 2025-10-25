from PyQt5.QtWidgets import (QApplication, QMainWindow)
from PyQt5 import uic
import sys
from graph import DistributionGraphWindow

UI_MAINWINDOW_PATH = "./mod7_3/ui/main_window.ui"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_MAINWINDOW_PATH, self)
        self.setWindowTitle("Распределения случайных величин")
        
        # Настраиваем начальные значения
        self.setup_initial_values()
        
        # Подключаем кнопки
        self.connect_buttons()
        
        # Переменная для хранения окон с графиками
        self.graph_windows = []
    
    def setup_initial_values(self):
        # Начальные значения для общих спинбоксов диапазона
        self.a_spb.setValue(0.0)
        self.b_spb.setValue(10.0)
        
        # Начальные значения для параметров распределений
        self.uniform_a_spb.setValue(2.0)    # Отдельный параметр a для равномерного распределения
        self.uniform_b_spb.setValue(8.0)    # Отдельный параметр b для равномерного распределения
        self.poisson_lambda_spb.setValue(1.0)
        self.exponential_lambda_spb.setValue(1.0)
        self.normal_m_spb.setValue(0.0)
        self.normal_d_spb.setValue(1.0)
        self.erlang_k_spb.setValue(2)
        self.erlang_lambda_spb.setValue(1.0)
        
        # Диапазоны значений
        self.a_spb.setRange(-1000, 1000)
        self.b_spb.setRange(-1000, 1000)
        self.uniform_a_spb.setRange(-1000, 1000)
        self.uniform_b_spb.setRange(-1000, 1000)
        self.poisson_lambda_spb.setRange(0.1, 100)
        self.exponential_lambda_spb.setRange(0.1, 100)
        self.normal_m_spb.setRange(-1000, 1000)
        self.normal_d_spb.setRange(0.1, 1000)
        self.erlang_k_spb.setRange(1, 100)
        self.erlang_lambda_spb.setRange(0.1, 100)

    def connect_buttons(self):
        self.uniform_show_btn.clicked.connect(self.show_uniform_distribution)
        self.poisson_show_btn.clicked.connect(self.show_poisson_distribution)
        self.exponential_show_btn.clicked.connect(self.show_exponential_distribution)
        self.normal_show_btn.clicked.connect(self.show_normal_distribution)
        self.erlang_show_btn.clicked.connect(self.show_erlang_distribution)
        self.exit_pbtn.aboutToShow.connect(self.exit)
    
    def show_uniform_distribution(self):
        # Используем отдельные параметры для равномерного распределения
        uniform_a = self.uniform_a_spb.value()
        uniform_b = self.uniform_b_spb.value()
        
        if uniform_a >= uniform_b:
            self.statusBar().showMessage("Ошибка: a должно быть меньше b!")
            return
        
        # Передаем общие a и b для диапазона отображения и специфичные для равномерного распределения
        a = self.a_spb.value()  # Общий диапазон отображения
        b = self.b_spb.value()  # Общий диапазон отображения
        
        if a >= b:
            self.statusBar().showMessage("Ошибка: начало должно быть меньше конца!")
            return
        
        parameters = {
            'uniform_a': uniform_a,  # Параметры самого распределения
            'uniform_b': uniform_b,  # Параметры самого распределения
            'a': a,                  # Диапазон отображения графика
            'b': b                   # Диапазон отображения графика
        }
        window = DistributionGraphWindow("uniform", parameters, self)
        window.show()
        self.graph_windows.append(window)
        self.statusBar().showMessage("График равномерного распределения построен")

    def show_normal_distribution(self):
        m = self.normal_m_spb.value()
        d = self.normal_d_spb.value()
        a = self.a_spb.value()
        b = self.b_spb.value()
        
        if a >= b:
            self.statusBar().showMessage("Ошибка: a должно быть меньше b!")
            return
        
        parameters = {'m': m, 'd': d, 'a': a, 'b': b}
        window = DistributionGraphWindow("normal", parameters, self)
        window.show()
        self.graph_windows.append(window)
        self.statusBar().showMessage("График нормального распределения построен")

    def show_exponential_distribution(self):
        lambda_param = self.exponential_lambda_spb.value()
        a = self.a_spb.value()
        b = self.b_spb.value()
        
        if a >= b:
            self.statusBar().showMessage("Ошибка: a должно быть меньше b!")
            return
        
        parameters = {'lambda_param': lambda_param, 'a': a, 'b': b}
        window = DistributionGraphWindow("exponential", parameters, self)
        window.show()
        self.graph_windows.append(window)
        self.statusBar().showMessage("График экспоненциального распределения построен")

    def show_poisson_distribution(self):
        lambda_param = self.poisson_lambda_spb.value()
        a = self.a_spb.value()
        b = self.b_spb.value()
        
        if a >= b:
            self.statusBar().showMessage("Ошибка: a должно быть меньше b!")
            return
        
        # Для Пуассона преобразуем в целые числа, так как это дискретное распределение
        parameters = {'lambda_param': lambda_param, 'a': int(a), 'b': int(b)}
        window = DistributionGraphWindow("poisson", parameters, self)
        window.show()
        self.graph_windows.append(window)
        self.statusBar().showMessage("График распределения Пуассона построен")

    def show_erlang_distribution(self):
        k = self.erlang_k_spb.value()
        lambda_param = self.erlang_lambda_spb.value()
        a = self.a_spb.value()
        b = self.b_spb.value()
        
        if a >= b:
            self.statusBar().showMessage("Ошибка: a должно быть меньше b!")
            return
        
        parameters = {'k': k, 'lambda_param': lambda_param, 'a': a, 'b': b}
        window = DistributionGraphWindow("erlang", parameters, self)
        window.show()
        self.graph_windows.append(window)
        self.statusBar().showMessage("График распределения Эрланга построен")
    
    def exit(self):
        # Закрываем все окна с графиками перед выходом
        for window in self.graph_windows:
            window.close()
        sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())