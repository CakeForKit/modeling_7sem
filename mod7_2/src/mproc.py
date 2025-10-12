import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

def kolmogorov_system(t, p, Lambda):
    """
    Система уравнений Колмогорова для произвольного числа состояний
    p - вектор вероятностей [p0, p1, ..., p_{n-1}]
    Lambda - матрица интенсивностей n x n
    """
    n = len(p)
    dp = np.zeros(n)
    
    for i in range(n):
        # Сумма входящих потоков
        incoming = 0
        for j in range(n):
            if j != i:
                incoming += Lambda[j, i] * p[j]
        
        # Сумма исходящих потоков
        outgoing = 0
        for j in range(n):
            if j != i:
                outgoing += Lambda[i, j]
        outgoing *= p[i]
        
        dp[i] = incoming - outgoing
    
    return dp

def find_proper_settling_times(t, p, p_stationary, tolerance=0.01):
    """
    Находит время установления для каждого состояния
    Ищет момент, после которого вероятность остается в области допуска
    """
    n_states = p.shape[0]
    settling_times = {}
    
    for state in range(n_states):
        state_errors = np.abs(p[state, :] - p_stationary[state])
        
        # Ищем последний момент выхода за пределы допуска
        last_exit_index = -1
        for i in range(len(t)-1, -1, -1):  # идем с конца к началу
            if state_errors[i] > tolerance:
                last_exit_index = i
                break
        
        # Время установления = момент после последнего выхода + небольшой запас
        if last_exit_index >= 0:
            settling_time = t[last_exit_index] + 0.1  # небольшой запас
            # Убедимся, что не вышли за границы массива
            settling_time = min(settling_time, t[-1])
        else:
            settling_time = 0  # всегда в пределах допуска
        
        settling_times[state] = settling_time
    
    return settling_times

def stationary_solution(Lambda):
    """Нахождение стационарных вероятностей"""
    n = Lambda.shape[0]
    A = np.vstack([Lambda.T, np.ones(n)])
    b = np.zeros(n + 1)
    b[-1] = 1
    p_star = np.linalg.lstsq(A, b, rcond=None)[0]
    return p_star

def analyze_settling_behavior(Lambda, initial_conditions, t_max, tolerance):
    """Полный анализ времени установления для произвольной системы"""
    
    n = Lambda.shape[0]
    
    # Проверяем согласованность размеров
    if len(initial_conditions) != n:
        raise ValueError(f"Размер initial_conditions ({len(initial_conditions)}) не совпадает с размером Lambda ({n})")
    
    # 1. Находим стационарное решение
    p_stationary = stationary_solution(Lambda)
    print(f"Стационарные вероятности: {p_stationary}")
    print(f"Сумма вероятностей: {np.sum(p_stationary):.10f}")
    
    # 2. Решаем динамическую систему
    t_span = (0, t_max)
    t_eval = np.linspace(0, t_max, 1000)
    
    solution = solve_ivp(
        kolmogorov_system, # kolmogorov_system_vectorized, 
        t_span, 
        initial_conditions, 
        args=(Lambda,),
        t_eval=t_eval,
        method='RK45'
    )
    
    # 3. Находим время установления для каждого состояния
    settling_times = find_proper_settling_times(
        solution.t, solution.y, p_stationary, tolerance
    )
    
    print(f"\nВремя установления для каждого состояния (точность {tolerance}):")
    for state in range(len(initial_conditions)):
        print(f"  Состояние S{state}: t = {settling_times[state]:.3f}")
    
    # 4. Анализ по собственным значениям
    eigenvalues, eigenvectors = np.linalg.eig(Lambda.T)
    nonzero_eigenvals = eigenvalues[np.abs(eigenvalues) > 1e-10]
    
    if len(nonzero_eigenvals) > 0:
        slowest_decay = np.min(np.abs(nonzero_eigenvals))
        theoretical_time = 3.0 / slowest_decay
        print(f"Теоретическое время (3τ): {theoretical_time:.3f}")
        print(f"Самое медленное затухание: {slowest_decay:.3f}")
    else:
        print("Не удалось найти ненулевые собственные значения")
        theoretical_time = None
    
    return solution, settling_times, p_stationary

def plot_results_per_state(solution, settling_times, p_stationary):
    # Визуализация всех состояний на одном графике
    plt.figure(figsize=(12, 8))

    colors = ['blue', 'red', 'green', 'orange']
    line_styles = ['-', '-', '-', '-']
    markers = ['o', 's', '^', 'D']

    # Графики вероятностей для всех состояний
    for state in range(4):
        plt.plot(solution.t, solution.y[state], 
                label=f'P{state}(t)', 
                linewidth=2.5, 
                color=colors[state],
                linestyle=line_styles[state])
        
        # Стационарные значения
        plt.axhline(y=p_stationary[state], 
                    color=colors[state], 
                    linestyle='--', 
                    alpha=0.6,
                    linewidth=1.5)
        
        # Маркеры времени установления
        settling_time = settling_times[state]
        y_val = solution.y[state, np.argmin(np.abs(solution.t - settling_time))]
        plt.plot(settling_time, y_val, 
                marker=markers[state], 
                markersize=10,
                color=colors[state],
                markeredgecolor='black',
                markeredgewidth=1,
                label=f'S{state} стаб.: t={settling_time:.2f}')

    # Настройки графика
    plt.xlabel('Время', fontsize=12)
    plt.ylabel('Вероятность', fontsize=12)
    plt.title('Динамика вероятностей состояний системы', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 10)
    plt.ylim(-0.05, 1.05)

    # Добавляем информацию о стационарных значениях
    text_str = "Стационарные значения:\n"
    for state in range(4):
        text_str += f"P{state}* = {p_stationary[state]:.3f}\n"

    plt.text(0.02, 0.98, text_str, transform=plt.gca().transAxes, 
            verticalalignment='top', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    plt.show()


def print_detailed_analysis(solution, p_stationary, tolerance=0.01):
    """Детальный анализ для каждого состояния"""
    n = solution.y.shape[0]
    
    print("\n" + "="*60)
    print("ДЕТАЛЬНЫЙ АНАЛИЗ ПО СОСТОЯНИЯМ:")
    print("="*60)

    for state in range(n):
        state_errors = np.abs(solution.y[state] - p_stationary[state])
        settling_indices = np.where(state_errors <= tolerance)[0]
        
        if len(settling_indices) > 0:
            settling_idx = settling_indices[0]
            state_settling_time = solution.t[settling_idx]
        else:
            state_settling_time = solution.t[-1]
        
        print(f"Состояние S{state}:")
        print(f"  Стационарная вероятность: {p_stationary[state]:.4f}")
        print(f"  Время установления: {state_settling_time:.3f}")
        print(f"  Начальное значение: {solution.y[state, 0]:.4f}")
        print(f"  Финальное значение: {solution.y[state, -1]:.4f}")
        print()


def calc_stabilization_times_and_probability(Lambda):
    for i in range(Lambda.shape[0]):
        s = 0
        for j in range(Lambda.shape[0]):
            s += Lambda[i][j]
        Lambda[i][i] = -s
    print(Lambda)
    initial = [0.0] * Lambda.shape[0] 
    initial[0] = 1.0
    
    solution, settling_time, p_stationary = analyze_settling_behavior(
        Lambda, initial, t_max=10, tolerance=1e-2
    )           
    return solution, settling_time, p_stationary

# Пример использования с произвольной матрицей
if __name__ == "__main__":

    # print("\n=== СИСТЕМА С 4 СОСТОЯНИЯМИ ===")
    # Lambda_4 = np.array([
    #     [-2,    2,    0,    0],   # S₀: уходит в S₁ с интенсивностью 2
    #     [ 0,   -3,    3,    0],   # S₁: уходит в S₂ с интенсивностью 3
    #     [ 0,    0,   -3,    3],   # S₂: уходит в S₃ с интенсивностью 3
    #     [ 3,    0,    0,   -3]    # S₃: уходит в S₀ с интенсивностью 3
    # ])
    # initial_4 = [1.0, 0.0, 0.0, 0.0]
    
    # solution, settling_time, p_stationary = analyze_settling_behavior(
    #     Lambda_4, initial_4, t_max=5, tolerance=1e-3
    # )

    print("\n=== СИСТЕМА С 5 СОСТОЯНИЯМИ ===")
    Lambda_5 = np.array([
        [0, 0.5, 0, 0, 0],
        [0, 0, 2, 0, 0],
        [0, 0, 0, 1.5, 1.5],
        [0.8, 0, 0, 0, 0],
        [2, 0, 0, 0, 0]
    ])
    solution, settling_time, p_stationary = calc_stabilization_times_and_probability(Lambda=Lambda_5)
    plot_results_per_state(solution, settling_time, p_stationary)
    print_detailed_analysis(solution, p_stationary)
    
