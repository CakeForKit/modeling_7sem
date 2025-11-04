from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import modeller 

UI_MAINWINDOW_PATH = "./mod7_4/ui/choose_dialog.ui"

class ChooseDistribution(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_MAINWINDOW_PATH, self)
        self.setWindowTitle("Распределения случайных величин")
        
        self.setup_initial_values()
        self.connect_buttons()

        self.generator = None
    
    def setup_initial_values(self):
        self.uniform_a_spb.setValue(2.0)    # Отдельный параметр a для равномерного распределения
        self.uniform_b_spb.setValue(8.0)    # Отдельный параметр b для равномерного распределения
        self.poisson_lambda_spb.setValue(1.0)
        self.exponential_lambda_spb.setValue(1.0)
        self.normal_m_spb.setValue(0.0)
        self.normal_d_spb.setValue(1.0)
        self.erlang_k_spb.setValue(2)
        self.erlang_lambda_spb.setValue(1.0)
        
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
    
    def show_uniform_distribution(self):
        uniform_a = self.uniform_a_spb.value()
        uniform_b = self.uniform_b_spb.value()
        if uniform_a >= uniform_b:
            self.statusBar.setText("Ошибка: a должно быть меньше b!")
            return
        self.generator = modeller.UniformGenerator(uniform_a, uniform_b)
        self.statusBar.setText("")
        self.accept()
        
    def show_normal_distribution(self):
        m = self.normal_m_spb.value()
        d = self.normal_d_spb.value()
        self.generator = modeller.NormalGenerator(m, d)
        self.statusBar.setText("")
        self.accept()

    def show_exponential_distribution(self):
        lambda_param = self.exponential_lambda_spb.value()
        self.generator = modeller.ExponentialGenerator(lambda_param)
        self.statusBar.setText("")
        self.accept()

    def show_poisson_distribution(self):
        lambda_param = self.poisson_lambda_spb.value()
        self.generator = modeller.PoissonGenerator(lambda_param)
        self.statusBar.setText("")
        self.accept()

    def show_erlang_distribution(self):
        k = self.erlang_k_spb.value()
        lambda_param = self.erlang_lambda_spb.value()
        self.generator = modeller.ErlangGenerator(k, lambda_param)
        self.statusBar.setText("")
        self.accept()


    def get_generator(self):
        return self.generator