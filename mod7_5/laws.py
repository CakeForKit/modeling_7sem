# pylint: disable=invalid-name
import abc
import bisect
from math import e, pi, inf
import random
import numpy.random as nr

STEPS_COUNT = 1000


class DistributionLaw(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError("Not realised method init")
    

    @abc.abstractmethod
    def get_value(self) -> float:
        raise NotImplementedError("Not realised method get_value")
    
class UniformDistributionLaw(DistributionLaw):
    def __init__(self, a: float, b: float) -> None:
        if not 0 <= a <= b:
            raise ValueError('The parameters should be in range [a, b]')
        self._a = a
        self._b = b

    def get_value(self) -> float:
        return nr.uniform(self._a, self._b)
    
    def info(self):
        return f"Равномерное распределение: a={self._a}, b={self._b}"

class ConstantDistributionLaw(DistributionLaw):
    def __init__(self, c: float):
        self.c = c

    def get_value(self) -> float:
        return self.c

class DistributionLaw1(abc.ABC):
    def __init__(self, *, left_border, right_border, **parameters):
        for name, value in parameters.items():
            setattr(self, name, value)
        self.left_border = left_border
        self.right_border = right_border
        self.x_list = []
        self.f_list = []
        self.F_list = [0]
        step = (right_border - left_border) / STEPS_COUNT
        for i in range(STEPS_COUNT + 1):
            x = round(left_border + i * step, 10)
            f = self.f(x)
            self.x_list.append(x)
            self.f_list.append(f)
            self.F_list.append(self.F_list[-1] + f * step)
        self.F_list.pop(0)

    def random(self):
        r = random.random()
        if r <= self.F_list[0]:
            return self.x_list[0]
        if r >= self.F_list[-1]:
            return self.x_list[-1]
        index = bisect.bisect_left(self.F_list, r)
        x1, x2, F1, F2 = (
            self.x_list[index - 1], self.x_list[index],
            self.F_list[index - 1], self.F_list[index]
        )
        if F1 == F2:
            return x1
        result = x1 + (x2 - x1) * (r - F1) / (F2 - F1)
        return result

    def F(self, x):
        if x <= self.left_border:
            return 0
        if x >= self.right_border:
            return 1
        index = bisect.bisect_left(self.x_list, x)
        x1, x2, F1, F2 = (
            self.x_list[index - 1], self.x_list[index],
            self.F_list[index - 1], self.F_list[index]
        )
        result = F1 + (F2 - F1) * (x - x1) / (x2 - x1)
        return result

    def sample(self, n):
        return sorted(self.random() for _ in range(n))

    @abc.abstractmethod
    def f(self, x):
        pass


class UniformDistributionLaw1(DistributionLaw):
    a: float
    b: float

    def __init__(self, *, a, b):
        super().__init__(
            a=a, b=b,
            left_border=a, right_border=b
        )

    # def F(self, x):
    #     return (
    #         0 if x < self.a else
    #         (x - self.a) / (self.b - self.a) if x <= self.b else
    #         1
    #     )

    def f(self, x):
        return (
            0 if x < self.a else
            1 / (self.b - self.a) if x <= self.b else
            0
        )


class NormalDistributionLaw(DistributionLaw):
    nu: float
    sigma: float

    def __init__(self, *, nu, sigma):
        super().__init__(
            nu=nu, sigma=sigma,
            left_border=nu - sigma * 3, right_border=nu + sigma * 3
        )

    def f(self, x):
        return (
            e ** -((x - self.nu) ** 2 / 2 / self.sigma ** 2) /
            self.sigma / (2 * pi) ** 0.5
        )


class ConstantDistributionLaw1(DistributionLaw):
    c: float

    def __init__(self, *, c):
        self.c = c

    def random(self):
        return self.c

    def f(self, x):
        if x == self.c:
            return inf
        return 0

    def F(self, x):
        if x < self.c:
            return 0
        return 1




if __name__ == '__main__':
    law = UniformGenerator(2, 10)
    for i in range(10):
        print(law.next())
    # law = ConstantDistributionLaw(c=15)
    # print(law.random())
