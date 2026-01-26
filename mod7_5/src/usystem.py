import laws
from typing import List
from icecream import ic 

CLIENT_EVENT = 0    # "client_event"
OP1_EVENT = 1       # "operator 1 event"
OP2_EVENT = 2       # "operator 2 event"
OP3_EVENT = 3       # "operator 3 event"
COMP1_EVENT = 4     # "computer 1 event"
COMP2_EVENT = 5     # "computer 2 event"

def type_str(type: int):
    text = ""
    if type == CLIENT_EVENT:
        text = "CLIENT_EVENT"
    elif type == OP1_EVENT:
        text = "OP1_EVENT"
    elif type == OP2_EVENT:
        text = "OP2_EVENT"
    elif type == OP3_EVENT:
        text = "OP3_EVENT"
    elif type == COMP1_EVENT:
        text = "COMP1_EVENT"
    elif type == COMP2_EVENT:
        text = "COMP2_EVENT"
    else:
        text = "UNKNOWN_EVENT"
    return text
    

class Event:
    def __init__(self, time: float, type: str):
        self.time = time
        self.type = type

    def nextTime(self, time):
        self.time = time

    def __lt__(self, other):
        if self.time == other.time:
            return self.type > other._type
        return self.time < other.time
    
    def __eq__(self, other):
        return self.time == other.time and self.type == other._type
    
    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"(type={type_str(self.type)}, time={self.time:.1f})"

class Queue:
    def __init__(self):
        self.queue = [] # список времени прихода

    def add(self, time: float) -> None:
        self.queue.append(time)
        self.queue.sort()
    
    def first(self) -> float:
        return self.queue[0]
    
    def pop(self) -> float:
        return self.queue.pop(0)

    def empty(self) -> bool:
        return len(self.queue) == 0

class Operator:
    def __init__(self, distributionLaw: laws.DistributionLaw, type_event: int):
        self.distributionLaw = distributionLaw
        self.type_event = type_event
        # self.queue = queue
        self.end_work_time = 0.0

    def start_work(self, timeStart) -> float:
        if self.is_busy(timeStart):
            raise Exception("try to start work - operator is busy!")
        self.end_work_time = timeStart + self.distributionLaw.get_value()
        return self.end_work_time
        # self.queue.add(self.end_work_time)

    def is_busy(self, timeCheck) -> bool:
        return self.end_work_time >= timeCheck
    
class Computer:
    def __init__(self, distributionLaw: laws.DistributionLaw, type_event: int):
        self.distributionLaw = distributionLaw
        self.type_event = type_event
        self.end_work_time = 0.0

    def start_work(self, timeStart) -> float:
        if self.is_busy(timeStart):
            raise Exception("try to start work - computer is busy!")
        self.end_work_time = timeStart + self.distributionLaw.get_value()
        return self.end_work_time

    def is_busy(self, timeCheck) -> bool:
        return self.end_work_time > timeCheck

class System:
    def __init__(
            self, clientLaw: laws.DistributionLaw,
            operators: List[Operator],
            computer1: Computer, computer2: Computer,
            NprocClients: int,
    ):
        self.clientLaw = clientLaw  
        self.operators = operators  # уже отсортированы по произоводительности
        self.computer1 = computer1
        self.computer2 = computer2
        self.NprocClients = NprocClients
        self.queue1 = Queue()
        self.queue2 = Queue()

        # self.simulate()

    def simulate(self):
        self.events_list = [
            Event(self.clientLaw.get_value(), CLIENT_EVENT),
            # Event(0, OP1_EVENT),
            # Event(0, OP2_EVENT),
            # Event(0, OP3_EVENT),
            # Event(0, COMP1_EVENT),
            # Event(0, COMP2_EVENT),
        ]
        self.generated_count = 0
        self.processed_count = 0
        self.rejected_count = 0

        while self.processed_count < self.NprocClients:
            event = self.events_list.pop(0)
            self.process_event(event)

    def process_event(self, event):
        if event.type == CLIENT_EVENT:
            self.generated_count += 1

            workStarted = False
            for op in self.operators:
                if not op.is_busy(event.time):
                    end_work_time = op.start_work(event.time)
                    self.events_list.append(Event(end_work_time, op.type_event))
                    workStarted = True
                    break
            if not workStarted:
                self.rejected_count += 1

            self.events_list.append(Event(event.time + self.clientLaw.get_value(), CLIENT_EVENT))
        
        elif event.type == OP1_EVENT or event.type == OP2_EVENT:
            self.queue1.add(event.time)
            if not self.computer1.is_busy(self.queue1.first()):
                end_work_time = self.computer1.start_work(self.queue1.pop())
                self.events_list.append(Event(end_work_time, self.computer1.type_event))

        elif event.type == OP3_EVENT:
            self.queue2.add(event.time)
            if not self.computer2.is_busy(self.queue2.first()):
                end_work_time = self.computer2.start_work(self.queue2.pop())
                self.events_list.append(Event(end_work_time, self.computer2.type_event))

        elif event.type == COMP1_EVENT:
            self.processed_count += 1
            if not self.queue1.empty():
                start_work_time = max(self.queue1.pop(), event.time)
                end_work_time = self.computer1.start_work(start_work_time)
                self.events_list.append(Event(end_work_time, self.computer1.type_event))

        elif event.type == COMP2_EVENT:
            self.processed_count += 1
            if not self.queue2.empty():
                start_work_time = max(self.queue2.pop(), event.time)
                end_work_time = self.computer2.start_work(start_work_time)
                self.events_list.append(Event(end_work_time, self.computer2.type_event))
        else:
            raise Exception("UNKNOWN_EVENT")
        self.events_list.sort()
        # print(self.events_list)
    

if __name__ == '__main__':
    clientLaw = laws.UniformDistributionLaw(8, 12)
    operators = [
        Operator(laws.UniformDistributionLaw(15, 25), OP1_EVENT),
        Operator(laws.UniformDistributionLaw(30, 50), OP2_EVENT),
        Operator(laws.UniformDistributionLaw(20, 60), OP3_EVENT),
    ]
    computer1 = Computer(laws.ConstantDistributionLaw(15), COMP1_EVENT)
    computer2 = Computer(laws.ConstantDistributionLaw(30), COMP2_EVENT)
    N = 300
    system = System(clientLaw, operators, computer1, computer2, N)

    system.simulate()
    print(f"generated_count = {system.generated_count}\n")
    print(f"processed_count = {system.processed_count}\n")
    print(f"rejected_count = {system.rejected_count}\n")
    p = system.rejected_count / (system.processed_count + system.rejected_count)
    print(f"p = {p}\n")
