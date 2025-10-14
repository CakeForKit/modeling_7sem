from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy)
import numpy as np

# Добавляем импорты для matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class GraphWindow(QDialog):
    def __init__(self, solution, settling_times, p_stationary, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Графики вероятностей состояний")
        self.setGeometry(100, 100, 800, 500)
        
        # Создаем layout
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Создаем canvas для matplotlib
        self.figure = Figure(figsize=(10, 6))
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
        
        # Строим график
        self.plot_results_per_state(solution, settling_times, p_stationary)
        
        # Обновляем canvas после отображения окна
        self.canvas.draw()
    
    def plot_results_per_state(self, solution, settling_times, p_stationary):
        # Очищаем предыдущий график
        self.figure.clear()
        
        # Используем subplots для лучшего контроля над layout
        ax = self.figure.add_subplot(111)
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        line_styles = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        
        num_states = len(p_stationary)
        
        # Графики вероятностей для всех состояний
        for state in range(num_states):
            ax.plot(solution.t, solution.y[state], 
                   label=f'P{state}(t)', 
                   linewidth=2.5, 
                   color=colors[state % len(colors)],
                   linestyle=line_styles[state % len(line_styles)])
            
            # Стационарные значения
            ax.axhline(y=p_stationary[state], 
                      color=colors[state % len(colors)], 
                      linestyle='--', 
                      alpha=0.6,
                      linewidth=1.5)
            
            # Маркеры времени установления
            settling_time = settling_times[state]
            idx = np.argmin(np.abs(solution.t - settling_time))
            y_val = solution.y[state, idx]
            ax.plot(settling_time, y_val, 
                   marker=markers[state % len(markers)], 
                   markersize=10,
                   color=colors[state % len(colors)],
                   markeredgecolor='black',
                   markeredgewidth=1,
                   label=f'S{state} стаб.: t={settling_time:.2f}')

        # Настройки графика
        ax.set_xlabel('Время', fontsize=12)
        ax.set_ylabel('Вероятность', fontsize=12)
        # ax.set_title('Динамика вероятностей состояний системы', fontsize=14, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        # ax.set_xlim(0, 5)
        # ax.set_ylim(-0.05, 1.05)

        # Добавляем информацию о стационарных значениях
        '''
        text_str = "Стационарные значения:\n"
        for state in range(num_states):
            text_str += f"P{state}* = {p_stationary[state]:.3f}\n"

        ax.text(0.02, 0.98, text_str, transform=ax.transAxes, 
               verticalalignment='top', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        '''
        # Настраиваем адаптивный layout
        self.figure.tight_layout(pad=3.0)
        self.canvas.draw()