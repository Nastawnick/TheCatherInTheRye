import threading
import time


# Класс таймера
class Timer:
    def __init__(self, name):
        self.name = name
        self._running = False
        self._thread = None


    def _run(self, seconds):
        print(f"[{self.name}] Таймер запущен на {seconds} сек")
        for i in range(seconds, 0, -1):
            print(f"Активных потоков: {threading.active_count()}")
            if not self._running:
                print(f"[{self.name}] Досрочная остановка")
                return
            print(f"[{self.name}] Осталось: {i} сек")
            time.sleep(1)
        print(f"[{self.name}] Таймер завершен")

    def start(self, seconds):
        if self._running:
            self.cancel()
        self._running = True
        self._thread = threading.Thread(target=self._run, args=(seconds,))
        self._thread.start()

    def cancel(self):
        self._running = False
        if self._thread:
            self._thread.join()  # Важно: ждем завершения потока
            print(f"[{self.name}] Поток завершен")

    def is_running(self):
        return self._running


# Менеджер таймеров с блокировкой
class TimerManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_timer = None

    def replace_timer(self, name, seconds):
        with self.lock:  # Блокируем доступ на время операции
            print(f"\nНачало замены таймера ({name} на {seconds} сек)")

            # 1. Отменяем предыдущий таймер
            if self.current_timer and self.current_timer.is_running():
                print("Отправляем сигнал отмены...")
                self.current_timer.cancel()  # 2. Посылаем сигнал отмены

    def start_timer(self, name, seconds):
        self.current_timer = Timer(name)
        self.current_timer.start(seconds)

# Демонстрация работы
if __name__ == "__main__":
    manager = TimerManager()

    # Первый таймер (5 сек)
    manager.replace_timer("Таймер A", 5)
    time.sleep(2)  # Ждем 2 сек

    # Пытаемся заменить до завершения (3 сек)
    manager.replace_timer("Таймер B", 3)
    time.sleep(4)  # Ждем завершения
    #
    # # Еще одна замена (2 сек)
    # manager.replace_timer("Таймер C", 2)