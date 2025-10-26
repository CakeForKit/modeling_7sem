from PyQt5.QtWidgets import (QDialog, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QSizePolicy)
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from distributions import *

class DistributionGraphWindow(QDialog):
    def __init__(self, distribution_type: str, parameters: dict, parent=None):
        super().__init__(parent)
        self.distribution_type = distribution_type
        self.parameters = parameters
        
        self.setWindowTitle(f"Графики {distribution_type} распределения")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем layout
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Создаем canvas для matplotlib
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        
        # Настраиваем политику размера для адаптивности
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        
        # Добавляем панель инструментов для навигации
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Кнопка закрытия
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Строим графики
        self.plot_distribution()
        
        # Обновляем canvas после отображения окна
        self.canvas.draw()
    
    def plot_distribution(self):
        self.figure.clear()
        
        if self.distribution_type == "uniform":
            self.plot_uniform()
        elif self.distribution_type == "normal":
            self.plot_normal()
        elif self.distribution_type == "exponential":
            self.plot_exponential()
        elif self.distribution_type == "poisson":
            self.plot_poisson()
        elif self.distribution_type == "erlang":
            self.plot_erlang()
        
        self.figure.tight_layout(pad=3.0)
    
    def plot_uniform(self):
        # Берем параметры распределения и диапазон отображения
        uniform_a = self.parameters['uniform_a']  # Параметр a распределения
        uniform_b = self.parameters['uniform_b']  # Параметр b распределения
        display_a = self.parameters['a']          # Начало диапазона отображения
        display_b = self.parameters['b']          # Конец диапазона отображения
        
        # Создаем подграфики
        ax1, ax2 = self.figure.subplots(2, 1)
        
        # График плотности - используем диапазон от display_a до display_b
        x_density = np.linspace(display_a, display_b, 1000)
        y_density = [UniformDensityFunc(x, uniform_a, uniform_b) for x in x_density]
        
        ax1.plot(x_density, y_density, 'b-', linewidth=2)
        ax1.set_title(f"Функция плотности равномерного распределения R[{uniform_a}, {uniform_b}]", fontsize=12)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(display_a, display_b)
        
        # График функции распределения - используем диапазон от display_a до display_b
        x_dist = np.linspace(display_a, display_b, 1000)
        y_dist = [UniformDistributionFunc(x, uniform_a, uniform_b) for x in x_dist]
        
        ax2.plot(x_dist, y_dist, 'r-', linewidth=2)
        ax2.set_title(f"Функция равномерного распределения R[{uniform_a}, {uniform_b}]", fontsize=12)
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(display_a, display_b)
        ax2.set_ylim(-0.1, 1.1)
    
    def plot_normal(self):
        m = self.parameters['m']
        d = self.parameters['d']
        a = self.parameters.get('a', m - 4 * sqrt(d))  # Если a не передан, используем автоматический расчет
        b = self.parameters.get('b', m + 4 * sqrt(d))  # Если b не передан, используем автоматический расчет
        sigma = sqrt(d)
        
        ax1, ax2 = self.figure.subplots(2, 1)
        
        # График плотности - используем диапазон от a до b
        x_density = np.linspace(a, b, 1000)
        y_density = [NormalDensityFunc(x, m, sigma) for x in x_density]
        
        ax1.plot(x_density, y_density, 'b-', linewidth=2)
        ax1.set_title(f"Функция плотности нормального распределения N({m}, {sigma:.2f}²)", fontsize=12)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(a, b)
        
        # График функции распределения - используем диапазон от a до b
        x_dist = np.linspace(a, b, 1000)
        y_dist = [NormalDistributionFunc(x, m, sigma) for x in x_dist]
        
        ax2.plot(x_dist, y_dist, 'r-', linewidth=2)
        ax2.set_title(f"Функция нормального распределения N({m}, {sigma:.2f}²)", fontsize=12)
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(a, b)
        ax2.set_ylim(-0.1, 1.1)
    
    def plot_exponential(self):
        lambda_param = self.parameters['lambda_param']
        a = self.parameters.get('a', 0)  # Если a не передан, используем 0
        b = self.parameters.get('b', 5 / lambda_param if lambda_param > 0 else 10)  # Если b не передан, используем автоматический расчет
        
        ax1, ax2 = self.figure.subplots(2, 1)
        
        # График плотности - используем диапазон от a до b
        x_density = np.linspace(a, b, 1000)
        y_density = [ExponentialDensityFunc(x, lambda_param) for x in x_density]
        
        ax1.plot(x_density, y_density, 'b-', linewidth=2)
        ax1.set_title(f"Функция плотности экспоненциального распределения (λ={lambda_param})", fontsize=12)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(a, b)
        
        # График функции распределения - используем диапазон от a до b
        x_dist = np.linspace(a, b, 1000)
        y_dist = [ExponentialDistributionFunc(x, lambda_param) for x in x_dist]
        
        ax2.plot(x_dist, y_dist, 'r-', linewidth=2)
        ax2.set_title(f"Функция экспоненциального распределения (λ={lambda_param})", fontsize=12)
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(a, b)
        ax2.set_ylim(-0.1, 1.1)
    
    def plot_poisson(self):
        lambda_param = self.parameters['lambda_param']
        a = int(self.parameters.get('a', 0))  # Если a не передан, используем 0
        b = int(self.parameters.get('b', min(int(lambda_param * 3) + 5, 50)))  # Если b не передан, используем автоматический расчет
        
        # Для Пуассона строим только график вероятностей (дискретное распределение)
        ax = self.figure.add_subplot(111)
        
        # Ограничиваем k значениями от a до b
        k_min = max(0, a)
        k_max = min(int(lambda_param * 3) + 5, b, 50)  # Ограничиваем максимальное k
        k_values = list(range(k_min, k_max + 1))
        probabilities = [PoissonProbabilityFunc(k, lambda_param) for k in k_values]
        
        ax.bar(k_values, probabilities, width=1.0, align='center', alpha=0.7, color='blue')
        ax.set_title(f"Распределение Пуассона (λ={lambda_param})", fontsize=12)
        ax.set_xlabel('k')
        ax.set_ylabel('P(X=k)')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(k_min, k_max + 1)
        ax.set_xticks(k_values[::max(1, len(k_values)//10)])
    
    def plot_erlang(self):
        k = self.parameters['k']
        lambda_param = self.parameters['lambda_param']
        a = self.parameters.get('a', 0)  # Если a не передан, используем 0
        b = self.parameters.get('b', (k + 4 * sqrt(k)) / lambda_param if lambda_param > 0 else 10)  # Если b не передан, используем автоматический расчет
        
        ax1, ax2 = self.figure.subplots(2, 1)
        
        # График плотности - используем диапазон от a до b
        x_density = np.linspace(a, b, 1000)
        y_density = [ErlangDensityFunc(x, k, lambda_param) for x in x_density]
        
        ax1.plot(x_density, y_density, 'b-', linewidth=2)
        ax1.set_title(f"Функция плотности распределения Эрланга (k={k}, λ={lambda_param})", fontsize=12)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(a, b)
        
        # График функции распределения - используем диапазон от a до b
        x_dist = np.linspace(a, b, 1000)
        y_dist = [ErlangDistributionFunc(x, k, lambda_param) for x in x_dist]
        
        ax2.plot(x_dist, y_dist, 'r-', linewidth=2)
        ax2.set_title(f"Функция распределения Эрланга (k={k}, λ={lambda_param})", fontsize=12)
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(a, b)
        ax2.set_ylim(-0.1, 1.1)
