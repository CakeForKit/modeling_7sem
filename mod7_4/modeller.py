import numpy.random as nr

class UniformGenerator:
    def __init__(self, a, b):
        if not 0 <= a <= b:
            raise ValueError('The parameters should be in range [a, b]')
        self._a = a
        self._b = b

    def next(self):
        return nr.uniform(self._a, self._b)
    
    def info(self):
        return f"Равномерное распределение: a={self._a}, b={self._b}"

class ErlangGenerator:
    def __init__(self, k, lambda_):
        self._scale = 1 / lambda_
        self._shape = k

    def next(self):
        return nr.gamma(self._shape, self._scale)

    def info(self):
        return f"Распределение Эрланга: k={self._shape}, lambda={1/self._scale}"

class NormalGenerator:
    def __init__(self, mean, std):
        self._mean = mean
        self._std = std

    def next(self):
        return nr.normal(self._mean, self._std)

    def info(self):
        return f"Нормальное распределение: m={self._mean}, d={self._std}"

class ExponentialGenerator:
    def __init__(self, lambda_):
        self._lambda = lambda_

    def next(self):
        return nr.exponential(1 / self._lambda)
    
    def info(self):
        return f"Экспоненциальное распределение: lambda={self._lambda}"

class PoissonGenerator:
    def __init__(self, lambda_):
        self._lambda = lambda_

    def next(self):
        return nr.poisson(self._lambda)

    def info(self):
        return f"Распределение Пуассона: lambda={self._lambda}"
    
class RequestGenerator:
    def __init__(self, generator):
        self._generator = generator
        self._receivers = set()

    def add_receiver(self, receiver):
        self._receivers.add(receiver)

    def remove_receiver(self, receiver):
        try:
            self._receivers.remove(receiver)
        except KeyError:
            pass

    def next_time_period(self):
        return self._generator.next()

    def emit_request(self):
        for receiver in self._receivers:
            receiver.receive_request()


class RequestProcessor():
    def __init__(self, generator, reenter_probability=0):
        self._generator = generator
        self._current_queue_size = 0
        self._max_queue_size = 0
        self._processed_requests = 0
        self._reenter_probability = reenter_probability
        self._reentered_requests = 0

    @property
    def processed_requests(self):
        return self._processed_requests

    @property
    def max_queue_size(self):
        return self._max_queue_size

    @property
    def current_queue_size(self):
        return self._current_queue_size

    @property
    def reentered_requests(self):
        return self._reentered_requests

    def process(self):
        if self._current_queue_size > 0:
            self._processed_requests += 1
            self._current_queue_size -= 1
            if nr.random_sample() < self._reenter_probability:
                self._reentered_requests += 1
                self.receive_request()

    def receive_request(self):
        self._current_queue_size += 1
        if self._current_queue_size > self._max_queue_size:
            self._max_queue_size += 1

    def next_time_period(self):
        return self._generator.next()


class Modeller:
    def __init__(self, generatorGenerator, generatorProcessor, reenter_prop):
        self._generator = RequestGenerator(generatorGenerator)
        self._processor = RequestProcessor(generatorProcessor, reenter_prop)
        self._generator.add_receiver(self._processor)

    # def __init__(self, uniform_a, uniform_b, erl_k, erl_lambda, reenter_prop):
    #     self._generator = RequestGenerator(UniformGenerator(uniform_a, uniform_b))
    #     self._processor = RequestProcessor(ErlangGenerator(erl_k, erl_lambda), reenter_prop)
    #     self._generator.add_receiver(self._processor)

    def event_based_modelling(self, request_count):
        generator = self._generator
        processor = self._processor

        gen_period = generator.next_time_period()
        proc_period = gen_period + processor.next_time_period()
        while processor.processed_requests < request_count:
            if gen_period <= proc_period:
                generator.emit_request()
                gen_period += generator.next_time_period()
            else:
                processor.process()
                if processor.current_queue_size > 0:
                    proc_period += processor.next_time_period()
                else:
                    proc_period = gen_period + processor.next_time_period()

        return (processor.processed_requests, processor.reentered_requests,
                processor.max_queue_size, proc_period)

    def time_based_modelling(self, request_count, dt):
        generator = self._generator
        processor = self._processor

        gen_period = generator.next_time_period()
        proc_period = gen_period + processor.next_time_period()
        current_time = 0
        while processor.processed_requests < request_count:
            if gen_period <= current_time:
                generator.emit_request()
                gen_period += generator.next_time_period()
            if current_time >= proc_period:
                processor.process()
                if processor.current_queue_size > 0:
                    proc_period += processor.next_time_period()
                else:
                    proc_period = gen_period + processor.next_time_period()
            current_time += dt

        return processor.processed_requests, processor.reentered_requests, processor.max_queue_size, current_time
    

if __name__ == '__main__':
    # Тестирование всех генераторов
    
    print("=== Равномерное распределение ===")
    uniform_a, uniform_b = 0.5, 10
    k, expo_l = 2, 4
    reenter = 0.5
    
    model = Modeller(
        UniformGenerator(uniform_a, uniform_b), 
        ErlangGenerator(k, expo_l), 
        reenter)
    
    req_count = 100
    delta_t = 0.01
    
    processed_requests, reentered_requests, max_queue_size, current_time = model.time_based_modelling(req_count, delta_t)
    print(f"processed_requests={processed_requests}, reentered_requests={reentered_requests}, max_queue_size={max_queue_size}, current_time={current_time}")
    
    print("\n=== Нормальное распределение ===")
    # Нормальное распределение: mean=5, std=1
    model_normal = Modeller(
        NormalGenerator(5, 1),  # генератор заявок
        NormalGenerator(3, 0.5),  # процессор
        reenter)
    
    processed_requests, reentered_requests, max_queue_size, current_time = model_normal.time_based_modelling(req_count, delta_t)
    print(f"processed_requests={processed_requests}, reentered_requests={reentered_requests}, max_queue_size={max_queue_size}, current_time={current_time}")
    
    print("\n=== Экспоненциальное распределение ===")
    # Экспоненциальное распределение: lambda=0.2
    model_exp = Modeller(
        ExponentialGenerator(0.2),  # генератор заявок
        ExponentialGenerator(0.3),  # процессор
        reenter)
    
    processed_requests, reentered_requests, max_queue_size, current_time = model_exp.time_based_modelling(req_count, delta_t)
    print(f"processed_requests={processed_requests}, reentered_requests={reentered_requests}, max_queue_size={max_queue_size}, current_time={current_time}")
    
    print("\n=== Пуассоновское распределение ===")
    # Пуассоновское распределение: lambda=4
    model_poisson = Modeller(
        PoissonGenerator(4),  # генератор заявок
        PoissonGenerator(3),  # процессор
        reenter)
    
    processed_requests, reentered_requests, max_queue_size, current_time = model_poisson.time_based_modelling(req_count, delta_t)
    print(f"processed_requests={processed_requests}, reentered_requests={reentered_requests}, max_queue_size={max_queue_size}, current_time={current_time}")
    
    # Смешанный пример: разные распределения для генератора и процессора
    print("\n=== Смешанный пример (Нормальный + Экспоненциальный) ===")
    model_mixed = Modeller(
        NormalGenerator(5, 1),  # генератор заявок - нормальное
        ExponentialGenerator(0.3),  # процессор - экспоненциальное
        reenter)
    
    processed_requests, reentered_requests, max_queue_size, proc_period = model_mixed.event_based_modelling(req_count)
    print(f"processed_requests={processed_requests}, reentered_requests={reentered_requests}, max_queue_size={max_queue_size}, proc_period={proc_period}")

'''
if __name__ == '__main__':
    uniform_a, uniform_b = 0.5, 10
    k, expo_l = 2, 4
    reenter = 0.5
    
    model = Modeller(
        UniformGenerator(uniform_a, uniform_b), 
        ErlangGenerator(k, expo_l), 
        reenter)
    
    req_count = 3925
    print("time_based_modelling: ")
    delta_t = 0.01
    processed_requests, reentered_requests, max_queue_size, current_time = model.time_based_modelling(req_count, delta_t)
    print(f"processed_requests={processed_requests}, \n"+
          f"reentered_requests={reentered_requests}, \n"+
          f"max_queue_size={max_queue_size}, \n"+
          f"current_time={current_time}\n")
    
    processed_requests, reentered_requests, max_queue_size, proc_period = model.event_based_modelling(req_count)
    print(f"processed_requests={processed_requests}, \n"+
          f"reentered_requests={reentered_requests}, \n"+
          f"max_queue_size={max_queue_size}, \n"+
          f"proc_period={proc_period}\n")
'''