import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

def kolmogorov_system(t, p, Lambda):
    p0, p1, p2 = p
    dp0 = -(Lambda[0,1] + Lambda[0,2])*p0 + Lambda[1,0]*p1 + Lambda[2,0]*p2
    dp1 = -(Lambda[1,0] + Lambda[1,2])*p1 + Lambda[0,1]*p0 + Lambda[2,1]*p2
    dp2 = -(Lambda[2,0] + Lambda[2,1])*p2 + Lambda[0,2]*p0 + Lambda[1,2]*p1
    return [dp0, dp1, dp2]

def find_settling_time(t, p, p_stationary, tolerance=0.01):
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
    
    return t[-1], max_error  # если не достигли точности

def stationary_solution(Lambda):
    """
    Нахождение стационарных вероятностей решением системы:
    P × Λ = 0, Σpi = 1
    """
    n = Lambda.shape[0]
    # Создаем расширенную систему: P·Λ = 0 и Σpi = 1
    A = np.vstack([Lambda.T, np.ones(n)])
    b = np.zeros(n + 1)
    b[-1] = 1   # условие нормировки

    # Решаем методом наименьших квадратов
    p_star = np.linalg.lstsq(A, b, rcond=None)[0]
    return p_star

def analyze_settling_behavior(Lambda, initial_conditions, t_max=20, tolerance=0.01):
    """Полный анализ времени установления"""
    
    # 1. Находим стационарное решение
    p_stationary = stationary_solution(Lambda)
    print("Стационарные вероятности:", p_stationary)
    
    # 2. Решаем динамическую систему
    t_span = (0, t_max)
    t_eval = np.linspace(0, t_max, 1000)
    
    solution = solve_ivp(
        kolmogorov_system, 
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
    slowest_decay = np.min(np.abs(nonzero_eigenvals))
    theoretical_time = 3.0 / slowest_decay  # 3 временные константы для 95% установления
    
    print(f"Теоретическое время (3τ): {theoretical_time:.3f}")
    print(f"Самое медленное затухание: {slowest_decay:.3f}")
    
    return solution, settling_time, p_stationary

# Параметры системы
Lambda = np.array([
    [-0.5,     0.3,   0.2],
    [0.4,   -0.7,     0.3], 
    [0.1,   0.2,   -0.3]
])

initial_conditions = [1.0, 0.0, 0.0]  # Начинаем в состоянии S0

# Запускаем анализ
solution, settling_time, p_stationary = analyze_settling_behavior(
    Lambda, initial_conditions, t_max=15, tolerance=0.01
)

# Визуализация с маркером времени установления
plt.figure(figsize=(12, 8))

# График вероятностей
plt.subplot(2, 1, 1)
plt.plot(solution.t, solution.y[0], label='p0(t)', linewidth=2)
plt.plot(solution.t, solution.y[1], label='p1(t)', linewidth=2) 
plt.plot(solution.t, solution.y[2], label='p2(t)', linewidth=2)

# Стационарные значения
plt.axhline(y=p_stationary[0], color='blue', linestyle='--', alpha=0.7, label='p0*')
plt.axhline(y=p_stationary[1], color='orange', linestyle='--', alpha=0.7, label='p1*')
plt.axhline(y=p_stationary[2], color='green', linestyle='--', alpha=0.7, label='p2*')

# Время установления
plt.axvline(x=settling_time, color='red', linestyle='-', 
           label=f'Время установления: {settling_time:.2f}')

plt.xlabel('Время')
plt.ylabel('Вероятность')
plt.title('Динамика вероятностей и время установления')
plt.legend()
plt.grid(True, alpha=0.3)

# График ошибки
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

plt.tight_layout()
plt.show()

# Детальный анализ для каждого состояния
print("\n" + "="*50)
print("ДЕТАЛЬНЫЙ АНАЛИЗ ПО СОСТОЯНИЯМ:")
print("="*50)

for state in range(3):
    # Находим время установления для каждого состояния отдельно
    state_errors = np.abs(solution.y[state] - p_stationary[state])
    settling_idx = np.argmax(state_errors <= 0.01)
    state_settling_time = solution.t[settling_idx] if settling_idx > 0 else solution.t[-1]
    
    print(f"Состояние S{state}:")
    print(f"  Стационарная вероятность: {p_stationary[state]:.4f}")
    print(f"  Время установления: {state_settling_time:.3f}")
    print(f"  Начальное значение: {solution.y[state, 0]:.4f}")
    print(f"  Финальное значение: {solution.y[state, -1]:.4f}")
    print()