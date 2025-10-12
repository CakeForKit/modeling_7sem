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

def find_settling_time(t, p, p_stationary, tolerance):
    """
    Находит время установления, когда все вероятности 
    отличаются от стационарных не более чем на tolerance
    """
    n_states = p.shape[0]
    
    for i in range(len(t)):
        # Проверяем все состояния
        max_error = 0
        for state in range(n_states):
            error = abs(p[state, i] - p_stationary[state])
            max_error = max(max_error, error)
        
        if max_error <= tolerance:
            return t[i], max_error
    
    return t[-1], max_error

def stationary_solution(Lambda):
    """
    Нахождение стационарных вероятностей решением системы:
    P × Λ = 0, Σpi = 1
    """
    n = Lambda.shape[0]
    
    # Проверяем корректность матрицы
    for i in range(n):
        row_sum = np.sum(Lambda[i, :])
        if abs(row_sum) > 1e-10:
            print(f"Предупреждение: Сумма строки {i} = {row_sum:.2e} (должна быть 0)")
    
    # Создаем расширенную систему: P·Λ = 0 и Σpi = 1
    A = np.vstack([Lambda.T, np.ones(n)])
    b = np.zeros(n + 1)
    b[-1] = 1  # условие нормировки

    # Решаем методом наименьших квадратов
    p_star, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    
    # Проверяем неотрицательность вероятностей
    if np.any(p_star < -1e-10):
        print("Внимание: найдены отрицательные вероятности! Проверьте матрицу Λ.")
    
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
    
    # 3. Находим время установления
    settling_time, final_error = find_settling_time(
        solution.t, solution.y, p_stationary, tolerance
    )
    
    print(f"Время установления (точность {tolerance}): {settling_time:.3f}")
    print(f"Финальная ошибка: {final_error:.6f}")
    
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
    
    return solution, settling_time, p_stationary

def plot_results(solution, settling_time, p_stationary, Lambda):
    """Визуализация результатов для произвольного числа состояний"""
    n = Lambda.shape[0]
    
    plt.figure(figsize=(12, 8))

    # График вероятностей
    plt.subplot(1, 1, 1)
    
    colors = plt.cm.tab10(np.linspace(0, 1, n))
    for state in range(n):
        plt.plot(solution.t, solution.y[state], 
                label=f'p{state}(t)', linewidth=2, color=colors[state])
        plt.axhline(y=p_stationary[state], color=colors[state], 
                   linestyle='--', alpha=0.7, label=f'p{state}*')

    # Время установления
    plt.axvline(x=settling_time, color='red', linestyle='-', 
               label=f'Время установления: {settling_time:.2f}')

    plt.xlabel('Время')
    plt.ylabel('Вероятность')
    plt.title(f'Динамика вероятностей ({n} состояний)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # График ошибки
    '''
    plt.subplot(2, 1, 2)
    errors = np.max(np.abs(solution.y - p_stationary.reshape(-1, 1)), axis=0)
    plt.plot(solution.t, errors, 'r-', linewidth=2, label='Максимальная ошибка')
    plt.axhline(y=0.01, color='black', linestyle='--', label='Порог 0.01')
    plt.axvline(x=settling_time, color='red', linestyle='-')
    plt.xlabel('Время')
    plt.ylabel('Ошибка')
    plt.title('Отклонение от стационарного режима')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    '''
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

# Пример использования с произвольной матрицей
if __name__ == "__main__":
    '''
    # Пример 1: 3 состояния (оригинальная система)
    print("=== СИСТЕМА С 3 СОСТОЯНИЯМИ ===")
    Lambda_3 = np.array([
        [-0.5,   0.3,   0.2],
        [0.4,   -0.7,   0.3], 
        [0.1,   0.2,   -0.3]
    ])
    initial_3 = [1.0, 0.0, 0.0]
    
    solution_3, settling_time_3, p_stationary_3 = analyze_settling_behavior(
        Lambda_3, initial_3, t_max=15, tolerance=0.01
    )
    plot_results(solution_3, settling_time_3, p_stationary_3, Lambda_3)
    print_detailed_analysis(solution_3, p_stationary_3)
    '''
    # Пример 2: 4 состояния
    print("\n=== СИСТЕМА С 4 СОСТОЯНИЯМИ ===")
    Lambda_4 = np.array([
        [-2,    2,    0,    0],   # S₀: уходит в S₁ с интенсивностью 2
        [ 0,   -3,    3,    0],   # S₁: уходит в S₂ с интенсивностью 3
        [ 0,    0,   -3,    3],   # S₂: уходит в S₃ с интенсивностью 3
        [ 3,    0,    0,   -3]    # S₃: уходит в S₀ с интенсивностью 3
        # [-2,   0,   0,   3],
        # [2,   -3,   0,   0],
        # [0,   3,   -3,   0],
        # [0,   0,   3,   -3]
    ])
    initial_4 = [1.0, 0.0, 0.0, 0.0]
    
    solution_4, settling_time_4, p_stationary_4 = analyze_settling_behavior(
        Lambda_4, initial_4, t_max=5, tolerance=1e-3
    )
    plot_results(solution_4, settling_time_4, p_stationary_4, Lambda_4)
    print_detailed_analysis(solution_4, p_stationary_4)
    
    '''
    # Пример 3: 5 состояний
    print("\n=== СИСТЕМА С 5 СОСТОЯНИЯМИ ===")
    Lambda_5 = np.array([
        [-1.0,   0.4,   0.3,   0.2,   0.1],
        [0.3,   -0.9,   0.3,   0.2,   0.1],
        [0.2,   0.2,   -0.8,   0.2,   0.2],
        [0.3,   0.1,   0.1,   -0.7,   0.2],
        [0.2,   0.2,   0.1,   0.1,   -0.6]
    ])
    initial_5 = [1.0, 0.0, 0.0, 0.0, 0.0]
    
    solution_5, settling_time_5, p_stationary_5 = analyze_settling_behavior(
        Lambda_5, initial_5, t_max=25, tolerance=0.01
    )
    plot_results(solution_5, settling_time_5, p_stationary_5, Lambda_5)
    print_detailed_analysis(solution_5, p_stationary_5)
    '''