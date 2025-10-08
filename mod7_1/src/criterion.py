import math
from typing import List

def combined_randomness_criterion(sequence: List[int]) -> int:
    """
    Комбинированный критерий случайности, объединяющий:
    - монотонность (серии)
    - уникальность (разнообразие)
    """
    if len(sequence) < 3:
        return 0
    
    # Вычисляем оба критерия
    monotonicity_score = monotonicity_criterion(sequence)
    uniqueness_score = uniqueness_criterion(sequence)
    
    # Весовые коэффициенты (можно настроить)
    weights = {
        'monotonicity': 0.6,  # 60% вес - анализ серий
        'uniqueness': 0.4     # 40% вес - разнообразие
    }
    
    # Комбинированная оценка
    combined_score = (
        weights['monotonicity'] * (monotonicity_score / 100.0) +
        weights['uniqueness'] * (uniqueness_score / 100.0)
    )
    
    return int(combined_score * 100)

def monotonicity_criterion(sequence: List[int]) -> int:
    """
    Критерий монотонности для оценки случайности последовательности
    Исправленная версия - учитывает одинаковые элементы
    """
    
    if len(sequence) < 3:
        return 0
    
    # 1. Подсчет длин серий (монотонно возрастающих/убывающих/постоянных)
    increasing_runs = []
    decreasing_runs = []
    constant_runs = []  # НОВОЕ: серии одинаковых чисел
    
    current_run_length = 1
    current_direction = 0  # 0: не определен, 1: возрастает, -1: убывает, 2: постоянен
    
    for i in range(1, len(sequence)):
        if sequence[i] > sequence[i-1]:
            if current_direction == 1:
                current_run_length += 1
            else:
                # Завершаем предыдущую серию
                if current_run_length > 1:
                    if current_direction == 1:
                        increasing_runs.append(current_run_length)
                    elif current_direction == -1:
                        decreasing_runs.append(current_run_length)
                    elif current_direction == 2:  # постоянная серия
                        constant_runs.append(current_run_length)
                current_run_length = 2
                current_direction = 1
                
        elif sequence[i] < sequence[i-1]:
            if current_direction == -1:
                current_run_length += 1
            else:
                # Завершаем предыдущую серию
                if current_run_length > 1:
                    if current_direction == 1:
                        increasing_runs.append(current_run_length)
                    elif current_direction == -1:
                        decreasing_runs.append(current_run_length)
                    elif current_direction == 2:  # постоянная серия
                        constant_runs.append(current_run_length)
                current_run_length = 2
                current_direction = -1
        else:
            # РАВНЫЕ ЧИСЛА - теперь это ОТДЕЛЬНЫЙ ТИП СЕРИИ
            if current_direction == 2:
                current_run_length += 1
            else:
                # Завершаем предыдущую серию
                if current_run_length > 1:
                    if current_direction == 1:
                        increasing_runs.append(current_run_length)
                    elif current_direction == -1:
                        decreasing_runs.append(current_run_length)
                    elif current_direction == 2:
                        constant_runs.append(current_run_length)
                current_run_length = 2
                current_direction = 2  # серия постоянных значений
    
    # Добавляем последнюю серию
    if current_run_length > 1:
        if current_direction == 1:
            increasing_runs.append(current_run_length)
        elif current_direction == -1:
            decreasing_runs.append(current_run_length)
        elif current_direction == 2:
            constant_runs.append(current_run_length)
    
    # 2. Статистика по сериям (теперь включаем постоянные серии)
    all_runs = increasing_runs + decreasing_runs + constant_runs
    total_runs_count = len(all_runs)
    
    # 3. ШТРАФ ЗА ПОСТОЯННЫЕ СЕРИИ - ОЧЕНЬ ВАЖНО!
    constant_penalty = 0
    for run_length in constant_runs:
        # Постоянные серии - явный признак неслучайности
        constant_penalty += run_length * 0.3  # серьезный штраф
    
    if total_runs_count == 0:
        # Если вообще нет серий - значит все числа одинаковые → 0% случайности
        return 0
    
    # 4. Ожидаемое количество серий для случайной последовательности
    n = len(sequence)
    expected_runs_count = (2 * n - 1) / 3
    
    # 5. Ожидаемая длина серий
    expected_run_length = 2.0
    
    # 6. Расчет отклонений
    runs_count_deviation = abs(total_runs_count - expected_runs_count) / expected_runs_count
    
    # Отклонение по длине серий
    if all_runs:
        avg_run_length = sum(all_runs) / len(all_runs)
        length_deviation = abs(avg_run_length - expected_run_length) / expected_run_length
    else:
        length_deviation = 0
    
    # 7. Штраф за слишком длинные серии (всех типов)
    long_runs_penalty = 0
    max_expected_length = 4
    for run_length in all_runs:
        if run_length > max_expected_length:
            long_runs_penalty += (run_length - max_expected_length) * 0.1
    
    # 8. Финальная оценка с учетом штрафа за постоянные серии
    score = 1.0 - min(1.0, (
        0.4 * runs_count_deviation +        # 40% вес - количество серий
        0.3 * length_deviation +            # 30% вес - длина серий  
        0.2 * min(1.0, long_runs_penalty) + # 20% вес - длинные серии
        0.1 * min(1.0, constant_penalty)    # 10% вес - постоянные серии (НОВОЕ!)
    ))
    
    return int(max(0.0, min(1.0, score)) * 100)


def uniqueness_criterion(sequence: List[int]) -> int:
    """
    Критерий уникальности оценивает разнообразие чисел в последовательности
    Возвращает оценку 0-100%
    """
    if len(sequence) < 2:
        return 0
    
    # 1. Подсчет уникальных чисел
    unique_numbers = len(set(sequence))
    total_numbers = len(sequence)
    
    # 2. Коэффициент уникальности (0-1)
    uniqueness_ratio = unique_numbers / total_numbers
    
    # 3. Энтропия Шеннона (мера разнообразия)
    from collections import Counter
    
    counter = Counter(sequence)
    entropy = 0.0
    for count in counter.values():
        probability = count / total_numbers
        entropy -= probability * (probability and math.log2(probability))
    
    # Максимальная возможная энтропия (при равномерном распределении)
    max_entropy = math.log2(unique_numbers) if unique_numbers > 0 else 0
    
    # Нормализованная энтропия (0-1)
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    # 4. Штраф за слишком мало уникальных чисел
    diversity_penalty = 0
    if unique_numbers < total_numbers * 0.3:  # Меньше 30% уникальных чисел
        diversity_penalty = 1 - (unique_numbers / (total_numbers * 0.3))
    
    # 5. Финальная оценка
    score = (
        0.6 * uniqueness_ratio +          # 60% - доля уникальных чисел
        0.4 * normalized_entropy          # 40% - равномерность распределения
    ) * (1 - diversity_penalty * 0.5)     # Штраф за низкое разнообразие
    
    return int(max(0.0, min(1.0, score)) * 100)