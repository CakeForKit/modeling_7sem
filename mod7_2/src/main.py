import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Умеет решать ЛЮБУЮ систему ОДУ вида dy/dt = f(t, y)
def kolmogorov_system(t, p, Lambda):
    """
    Система уравнений Колмогорова
    p = [p0, p1, p2] - вектор вероятностей
    Lambda - матрица интенсивностей 3x3
    """
    p0, p1, p2 = p
    
    # Уравнения из системы (1)
    dp0 = -(Lambda[0,1] + Lambda[0,2])*p0 + Lambda[1,0]*p1 + Lambda[2,0]*p2
    dp1 = -(Lambda[1,0] + Lambda[1,2])*p1 + Lambda[0,1]*p0 + Lambda[2,1]*p2
    dp2 = -(Lambda[2,0] + Lambda[2,1])*p2 + Lambda[0,2]*p0 + Lambda[1,2]*p1
    
    return [dp0, dp1, dp2]

# Параметры (пример)
Lambda = np.array([
    [0,     0.3,   0.2],   # λ01=0.3, λ02=0.2
    [0.4,   0,     0.1],   # λ10=0.4, λ12=0.1
    [0.2,   0.3,   0]      # λ20=0.2, λ21=0.3
])

# Начальные условия: система начинает в состоянии 0
p0_initial = [1.0, 0.0, 0.0]

# Временной интервал
t_span = (0, 10)
t_eval = np.linspace(0, 10, 1000)

# Решение системы
solution = solve_ivp(
    kolmogorov_system, 
    t_span,             #  интервал интегрирования (t_start, t_end)
    p0_initial,         #  начальные условия (вектор)
    args=(Lambda,),     # дополнительные аргументы для функции fun
    t_eval=t_eval,      #  точки, в которых нужно вычислить решение
    method='RK45'       # метод решения (по умолчанию 'RK45')
)

# Построение графиков
plt.figure(figsize=(10, 6))
plt.plot(solution.t, solution.y[0], label='p0(t)')
plt.plot(solution.t, solution.y[1], label='p1(t)')
plt.plot(solution.t, solution.y[2], label='p2(t)')
plt.xlabel('Время')
plt.ylabel('Вероятность')
plt.title('Динамика вероятностей состояний')
plt.legend()
plt.grid(True)
plt.show()


# def stationary_solution(Lambda):
#     """
#     Нахождение стационарных вероятностей решением системы:
#     P × Λ = 0, Σpi = 1
#     """
#     n = Lambda.shape[0]
    
#     # Создаем расширенную систему: P·Λ = 0 и Σpi = 1
#     A = np.vstack([Lambda.T, np.ones(n)])
#     b = np.zeros(n + 1)
#     b[-1] = 1  # условие нормировки
    
#     # Решаем методом наименьших квадратов
#     p_star, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
    
#     return p_star

# # Стационарное решение
# p_stationary = stationary_solution(Lambda)
# print("Стационарные вероятности:", p_stationary)


# def verify_solution(p, Lambda):
#     """
#     Проверка корректности решения:
#     1. Сумма вероятностей = 1
#     2. Производные удовлетворяют уравнениям
#     """
#     # Проверка нормировки
#     sum_p = np.sum(p, axis=0)
#     norm_error = np.max(np.abs(sum_p - 1))
#     print(f"Ошибка нормировки: {norm_error:.2e}")
    
#     # Проверка стационарности (для последней точки)
#     p_final = p[:, -1]
#     derivative = kolmogorov_system(0, p_final, Lambda)
#     derivative_error = np.max(np.abs(derivative))
#     print(f"Ошибка стационарности: {derivative_error:.2e}")

# verify_solution(solution.y, Lambda)