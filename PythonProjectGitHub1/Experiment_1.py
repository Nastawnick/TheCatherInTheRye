import threading
class SleepTimer:
    def __init__(self):
        self.cancel_event = threading.Event()
        self.timer_thread = None

a = SleepTimer()
print(a.cancel_event.set())

a = ''
def f():
    a = 1

f()
print(a)