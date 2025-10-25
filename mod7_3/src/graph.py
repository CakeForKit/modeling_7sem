from PyQt5.QtWidgets import (QDialog, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QSizePolicy)
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from distributions import *

# Класс для окна с графиками
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
        a = self.parameters['a']
        b = self.parameters['b']
        
        # Создаем подграфики
        ax1, ax2 = self.figure.subplots(2, 1)
        
        # График плотности
        x_density = np.linspace(a - (b - a) * 0.2, b + (b - a) * 0.2, 1000)
        y_density = [UniformDensityFunc(x, a, b) for x in x_density]
        
        ax1.plot(x_density, y_density, 'b-', linewidth=2)
        ax1.set_title(f"Функция плотности равномерного распределения R[{a}, {b}]", fontsize=12)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(a - (b - a) * 0.3, b + (b - a) * 0.3)
        
        # График функции распределения
        x_dist = np.linspace(a - (b - a) * 0.2, b + (b - a) * 0.2, 1000)
        y_dist = [UniformDistributionFunc(x, a, b) for x in x_dist]
        
        ax2.plot(x_dist, y_dist, 'r-', linewidth=2)
        ax2.set_title(f"Функция распределения равномерного распределения R[{a}, {b}]", fontsize=12)
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(a - (b - a) * 0.3, b + (b - a) * 0.3)
        ax2.set_ylim(-0.1, 1.1)
    
    def plot_normal(self):
        m = self.parameters['m']
        d = self.parameters['d']
        sigma = sqrt(d)
        
        ax1, ax2 = self.figure.subplots(2, 1)
        
        # График плотности
        x_density = np.linspace(m - 4 * sigma, m + 4 * sigma, 1000)
        y_density = [NormalDensityFunc(x, m, sigma) for x in x_density]
        
        ax1.plot(x_density, y_density, 'b-', linewidth=2)
        ax1.set_title(f"Функция плотности нормального распределения N({m}, {sigma:.2f}²)", fontsize=12)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.grid(True, alpha=0.3)
        
        # График функции распределения
        x_dist = np.linspace(m - 4 * sigma, m + 4 * sigma, 1000)
        y_dist = [NormalDistributionFunc(x, m, sigma) for x in x_dist]
        
        ax2.plot(x_dist, y_dist, 'r-', linewidth=2)
        ax2.set_title(f"Функция распределения нормального распределения N({m}, {sigma:.2f}²)", fontsize=12)
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(-0.1, 1.1)
    
    def plot_exponential(self):
        lambda_param = self.parameters['lambda_param']
        
        ax1, ax2 = self.figure.subplots(2, 1)
        
        # График плотности
        x_max = 5 / lambda_param if lambda_param > 0 else 10
        x_density = np.linspace(0, x_max, 1000)
        y_density = [ExponentialDensityFunc(x, lambda_param) for x in x_density]
        
        ax1.plot(x_density, y_density, 'b-', linewidth=2)
        ax1.set_title(f"Функция плотности экспоненциального распределения (λ={lambda_param})", fontsize=12)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.grid(True, alpha=0.3)
        
        # График функции распределения
        x_dist = np.linspace(0, x_max, 1000)
        y_dist = [ExponentialDistributionFunc(x, lambda_param) for x in x_dist]
        
        ax2.plot(x_dist, y_dist, 'r-', linewidth=2)
        ax2.set_title(f"Функция распределения экспоненциального распределения (λ={lambda_param})", fontsize=12)
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(-0.1, 1.1)
    
    def plot_poisson(self):
        lambda_param = self.parameters['lambda_param']
        
        # Для Пуассона строим только график вероятностей (дискретное распределение)
        ax = self.figure.add_subplot(111)
        
        k_max = min(int(lambda_param * 3) + 5, 50)  # Ограничиваем максимальное k
        k_values = list(range(0, k_max + 1))
        probabilities = [PoissonProbabilityFunc(k, lambda_param) for k in k_values]
        
        ax.bar(k_values, probabilities, width=1.0, align='edge', alpha=0.7, color='blue')
        ax.set_title(f"Распределение Пуассона (λ={lambda_param})", fontsize=12)
        ax.set_xlabel('k')
        ax.set_ylabel('P(X=k)')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(k_values[::max(1, k_max//10)])
    
    def plot_erlang(self):
        k = self.parameters['k']
        lambda_param = self.parameters['lambda_param']
        
        ax1, ax2 = self.figure.subplots(2, 1)
        
        # График плотности
        x_max = (k + 4 * sqrt(k)) / lambda_param if lambda_param > 0 else 10
        x_density = np.linspace(0, x_max, 1000)
        y_density = [ErlangDensityFunc(x, k, lambda_param) for x in x_density]
        
        ax1.plot(x_density, y_density, 'b-', linewidth=2)
        ax1.set_title(f"Функция плотности распределения Эрланга (k={k}, λ={lambda_param})", fontsize=12)
        ax1.set_xlabel('x')
        ax1.set_ylabel('f(x)')
        ax1.grid(True, alpha=0.3)
        
        # График функции распределения
        x_dist = np.linspace(0, x_max, 1000)
        y_dist = [ErlangDistributionFunc(x, k, lambda_param) for x in x_dist]
        
        ax2.plot(x_dist, y_dist, 'r-', linewidth=2)
        ax2.set_title(f"Функция распределения распределения Эрланга (k={k}, λ={lambda_param})", fontsize=12)
        ax2.set_xlabel('x')
        ax2.set_ylabel('F(x)')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(-0.1, 1.1)

'''
def DrawUniformDistrGraphs(a: float, b: float):

    x1, y1 = GetUniformDensityTableFunc(a, b, 1000)
    x2, y2 = GetUniformDistributionTableFunc(a, b, 1000)

    str1 = 'Равномерное распределение ~R[' + str(a) + ';' + str(b) + ']'

    fig, axs = plt.subplots(2, 1, figsize=(5, 5))
    fig.suptitle(str1, fontsize=20, fontweight='bold')
    axs[0].plot(x1, y1)
    axs[0].set_title("График функции плотности f(x)", fontsize=15)
    axs[0].grid(alpha=1)
    axs[1].plot(x2, y2)
    axs[1].set_title("График функции распределения F(x)", fontsize=15)
    axs[1].grid(alpha=1)
    plt.show()

def DrawNormalDistrGraphs(m: float, sigma: float):

    x1, y1 = GetNormalDensityTableFunc(m, sigma, 1000)
    x2, y2 = GetNormalDistributionTableFunc(m, sigma, 1000)

    str1 = 'Нормальное распределение ~N(' + str(m) + ',' + str(sigma) + '^2)'

    fig, axs = plt.subplots(2, 1, figsize=(5, 5))
    fig.suptitle(str1, fontsize=20, fontweight='bold')
    axs[0].plot(x1, y1)
    axs[0].set_title("График функции плотности f(x)", fontsize=15)
    axs[0].grid(alpha=1)
    axs[1].plot(x2, y2)
    axs[1].set_title("График функции распределения F(x)", fontsize=15)
    axs[1].grid(alpha=1)
    plt.show()

def GetTableFunc(function: Callable[..., float],
                 arguments: list[float],
                 xLeft: float,
                 xRight: float,
                 stepsNum: int) -> Tuple[list[float], list[float]]:
    step = (xRight - xLeft) / stepsNum

    xColumn = list(np.arange(xLeft, xRight + step / 2, step))
    yColumn = []

    for x in xColumn:
        yColumn.append(function(x, *arguments))

    return xColumn, yColumn


def GetUniformTableFunc(
        func:      Callable[[float, float, float], float],
        arguments: Tuple[float, float],
        interval:  Tuple[float, float],
        stepsNum:  int) -> Tuple[list[float], list[float]]:

    a, b = arguments

    xLeft, xRight = (2 * a - b, 2 * b - a) if interval is None else interval

    return GetTableFunc(func, [a, b], -10, 10, stepsNum)


def GetNormalTableFunc(
        func:      Callable[[float, float, float], float],
        arguments: Tuple[float, float],
        interval:  Tuple[float, float],
        stepsNum:  int) -> Tuple[list[float], list[float]]:

    m, sigma = arguments

    xLeft, xRight = ((m - 4 * sigma, m + 4 * sigma)
                        if interval is None else interval)

    return GetTableFunc(func, [m, sigma], -10, 10, stepsNum)


def GetUniformDensityTableFunc(
        a: float,
        b: float,
        stepsNum: int,
        interval: Tuple[float, float] = None) -> Tuple[list[float], list[float]]:
    return GetUniformTableFunc(dst.UniformDensityFunc, [a, b], interval, stepsNum)


def GetUniformDistributionTableFunc(
        a: float,
        b: float,
        stepsNum: int,
        interval: Tuple[float, float] = None) -> Tuple[list[float], list[float]]:
    return GetUniformTableFunc(dst.UniformDistributionFunc, [a, b],
                               interval, stepsNum)


def GetNormalDensityTableFunc(
        m:     float,
        sigma: float,
        stepsNum: int,
        interval: Tuple[float, float] = None) -> Tuple[list[float], list[float]]:
    return GetNormalTableFunc(dst.NormalDensityFunc, [m, sigma], interval, stepsNum)


def GetNormalDistributionTableFunc(
        m:     float,
        sigma: float,
        stepsNum: int,
        interval: Tuple[float, float] = None) -> Tuple[list[float], list[float]]:
    return GetNormalTableFunc(dst.NormalDistributionFunc, [m, sigma],
                              interval, stepsNum)
'''