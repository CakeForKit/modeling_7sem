import math
from typing import List

def monotonicity_criterion(sequence: List[int]) -> int:
    """
    Критерий монотонности для оценки случайности последовательности
    Возвращает оценку (0-100%)
    """
    
    if len(sequence) < 3:
        return 0.0, {"error": "Sequence too short"}
    
    # 1. Подсчет длин серий (монотонно возрастающих/убывающих)
    increasing_runs = []
    decreasing_runs = []
    
    current_run_length = 1
    current_direction = 0  # 0: не определен, 1: возрастает, -1: убывает
    
    for i in range(1, len(sequence)):
        if sequence[i] > sequence[i-1]:
            if current_direction == 1:
                current_run_length += 1
            else:
                if current_run_length > 1:
                    if current_direction == 1:
                        increasing_runs.append(current_run_length)
                    elif current_direction == -1:
                        decreasing_runs.append(current_run_length)
                current_run_length = 2
                current_direction = 1
                
        elif sequence[i] < sequence[i-1]:
            if current_direction == -1:
                current_run_length += 1
            else:
                if current_run_length > 1:
                    if current_direction == 1:
                        increasing_runs.append(current_run_length)
                    elif current_direction == -1:
                        decreasing_runs.append(current_run_length)
                current_run_length = 2
                current_direction = -1
        else:
            # Равные числа - прерываем серию
            if current_run_length > 1:
                if current_direction == 1:
                    increasing_runs.append(current_run_length)
                elif current_direction == -1:
                    decreasing_runs.append(current_run_length)
            current_run_length = 1
            current_direction = 0
    
    # Добавляем последнюю серию
    if current_run_length > 1:
        if current_direction == 1:
            increasing_runs.append(current_run_length)
        elif current_direction == -1:
            decreasing_runs.append(current_run_length)
    
    # 2. Статистика по сериям
    all_runs = increasing_runs + decreasing_runs
    total_runs_count = len(all_runs)
    
    if total_runs_count == 0:
        return 100
    
    # 3. Ожидаемое количество серий для случайной последовательности
    n = len(sequence)
    expected_runs_count = (2 * n - 1) / 3  # Математическое ожидание количества серий
    
    # 4. Ожидаемая длина серий
    expected_run_length = 2.0  # В случайной последовательности средняя длина серии ≈ 2
    
    # 5. Расчет отклонений
    runs_count_deviation = abs(total_runs_count - expected_runs_count) / expected_runs_count
    
    # Отклонение по длине серий
    if all_runs:
        avg_run_length = sum(all_runs) / len(all_runs)
        length_deviation = abs(avg_run_length - expected_run_length) / expected_run_length
    else:
        length_deviation = 0
    
    # 6. Штраф за слишком длинные серии
    long_runs_penalty = 0
    max_expected_length = 4  # В случайной последовательности серии длиннее 4 маловероятны
    for run_length in all_runs:
        if run_length > max_expected_length:
            long_runs_penalty += (run_length - max_expected_length) * 0.1
    
    # 7. Финальная оценка (0-1, где 1 - идеальная случайность)
    score = 1.0 - min(1.0, (
        0.5 * runs_count_deviation +
        0.3 * length_deviation +
        0.2 * min(1.0, long_runs_penalty)
    ))
    
    # 8. Детальная статистика
    statistics = {
        'total_runs': total_runs_count,
        'expected_runs': round(expected_runs_count, 2),
        'increasing_runs': increasing_runs,
        'decreasing_runs': decreasing_runs,
        'avg_run_length': round(avg_run_length, 2) if all_runs else 0,
        'expected_run_length': expected_run_length,
        'runs_count_deviation': round(runs_count_deviation, 3),
        'length_deviation': round(length_deviation, 3),
        'long_runs_penalty': round(long_runs_penalty, 3),
        'score_components': {
            'runs_count': round(1 - runs_count_deviation, 3),
            'length': round(1 - length_deviation, 3),
            'long_runs': round(1 - min(1.0, long_runs_penalty), 3)
        }
    }
    
    return int(max(0.0, min(1.0, score)) * 100)