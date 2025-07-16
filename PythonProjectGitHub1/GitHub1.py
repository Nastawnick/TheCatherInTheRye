import os
import time
import threading
import ctypes
from tkinter import messagebox
from customtkinter import CTk, CTkButton, CTkComboBox, CTkLabel, CTkFrame


class SleepTimer:
    def __init__(self):
        self.cancel_event = threading.Event()
        self.timer_thread = None
        self.remaining_time = 0
        self.total_time = 0
        self.update_callback = None

    def start(self, seconds, callback=None):
        # Отменяем предыдущий таймер
        self.cancel()

        self.cancel_event.clear()
        self.total_time = seconds
        self.remaining_time = seconds
        self.update_callback = callback
        self.active = True

        self.timer_thread = threading.Thread(
            target=self.run_timer,
            args=(seconds,),
            daemon=True
        )
        self.timer_thread.start()

    def cancel(self):
        self.cancel_event.set()
        self.active = False
        self.remaining_time = 0
        if self.update_callback:
            app.after(0, lambda: self.update_callback(0))  # Обновление в основном потоке

    def run_timer(self, seconds):
        for i in range(seconds):
            if self.cancel_event.is_set():
                return
            time.sleep(1)
            if not self.active:  # Проверка на активность
                return
            self.remaining_time = seconds - i - 1
            if self.update_callback:
                self.update_callback(self.remaining_time)

        if self.active and not self.cancel_event.is_set():  # Дополнительная проверка
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)

def format_time(seconds):
    """Форматирует время в удобочитаемый формат"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        if minutes > 0:
            return f"{hours} час {minutes} мин"
        return f"{hours} час"
    elif minutes > 0:
        return f"{minutes} мин"
    return f"{seconds} сек"

class SlidingMenu:
    def __init__(self, parent):
        self.parent = parent
        self.menu_shown = False
        self.menu_width = 200
        self.animation_speed = 15
        self.sensor = ""

        # Создаем меню (изначально скрыто за левым краем)
        self.menu = CTkFrame(
            master=parent,
            width=self.menu_width,
            height=parent.winfo_height(),
            corner_radius=3,
            fg_color="#D3D3D3"
        )
        self.menu.place(x=-self.menu_width, y=0, relheight=1)
        self.menu.lift()  # Поднимаем меню на передний план

        # Элементы для отображения таймера
        self.timer_label = CTkLabel(
            self.menu,
            text="Таймер не активен",
            text_color="#333333",
            font=("Arial", 12),
            anchor="w"
        )
        self.time_left_label = CTkLabel(
            self.menu,
            text="00:00:00",
            text_color="#333333",
            font=("Arial", 14, "bold"),
            anchor="w"
        )

        # Добавляем содержимое меню
        self._setup_menu_content()

        # Привязываем события мыши
        parent.bind("<Enter>", self._check_mouse_position)
        parent.bind("<Motion>", self._check_mouse_position)
        parent.bind("<Leave>", self._check_mouse_position)

    def _setup_menu_content(self):
        # Заголовок меню
        CTkLabel(
            self.menu,
            text="Меню таймера",
            text_color="#333333",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", padx=10, pady=(15, 5))

        # Разделитель
        CTkFrame(self.menu, height=2, fg_color="#cccccc").pack(fill="x", pady=5)

        # Метка состояния таймера
        self.timer_label.pack(fill="x", padx=10, pady=(5, 0))

        # Метка оставшегося времени
        self.time_left_label.pack(fill="x", padx=10, pady=(0, 10))

        # Разделитель
        CTkFrame(self.menu, height=2, fg_color="#cccccc").pack(fill="x", pady=5)

        # Пункты меню
        menu_items = [
            ("О программе", lambda: messagebox.showinfo("О программе", "Таймер сна v1.0")),
            ("Помощь", lambda: messagebox.showinfo("Помощь", "Выберите время и нажмите 'Запустить таймер'")),
            ("Выход", app.quit)
        ]

        for text, command in menu_items:
            btn = CTkButton(
                self.menu,
                text=text,
                command=command,
                fg_color="transparent",
                hover_color="#e0e0e0",
                text_color="#333333",
                anchor="w",
                corner_radius=0
            )
            #btn.pack(fill="x", padx=0, pady=0)
            CTkFrame(self.menu, height=1, fg_color="#e0e0e0").pack(fill="x")

    def update_timer_display(self, remaining_seconds):
        if remaining_seconds > 0:
            self.timer_label.configure(text="До выключения:")
            hours, remainder = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_left_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            self.reset_timer_display()

    def reset_timer_display(self):
        self.timer_label.configure(text="Таймер не активен")
        self.time_left_label.configure(text="00:00:00")


    def _check_mouse_position(self, event):
        if event.x < 10 and not self.menu_shown:
            self.show_menu()
        elif event.x == self.menu_width and self.menu_shown:
            self.hide_menu()
        elif event.x > self.menu_width and self.menu_shown:
            self.hide_menu()

    def show_menu(self):
        if not self.menu_shown:
            self.menu_shown = True
            self._animate_menu(0)
            self.menu.lift()

    def hide_menu(self):
        if self.menu_shown:
            self.menu_shown = False
            self._animate_menu(-self.menu_width)

    def _animate_menu(self, target_x):
        current_x = self.menu.winfo_x()
        if current_x < target_x:
            step = min(self.animation_speed, target_x - current_x)
            self.menu.place(x=current_x + step)
            self.parent.after(10, lambda: self._animate_menu(target_x))
        elif current_x > target_x:
            step = min(self.animation_speed, current_x - target_x)
            self.menu.place(x=current_x - step)
            self.parent.after(10, lambda: self._animate_menu(target_x))


sleep_timer = SleepTimer()

def start_timer():
    try:
        time_str = time_combobox.get()
        print(sliding_menu.time_left_label._text)
        stop_timer(1)
        print("stop_timer")

        if "секунд" in time_str:
            seconds = int(time_str.split()[0])
        elif "минут" in time_str:
            seconds = int(float(time_str.split()[0]) * 60)
        elif "час" in time_str:
            parts = time_str.split()
            seconds = int(float(parts[0]) * 3600)
        else:
            seconds = int(time_str)

        if seconds <= 0:
            messagebox.showerror("Ошибка", "Введите положительное время")
            return

        display_time = format_time(seconds)
        sleep_timer.start(seconds, sliding_menu.update_timer_display)
        button_cancel.configure(state="normal")
        messagebox.showinfo("Успех", f"Таймер установлен на {display_time}\nДля отмены нажмите 'Отменить'")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректное значение")


def stop_timer(a=0): #если сейчас эту функция вызывает start_timer, то True, иначе - False
    if a == 0:
        print("FALSE")
        sleep_timer.cancel()
        sliding_menu.reset_timer_display()  # Сбрасываем отображение
        button_cancel.configure(state="disabled")
        messagebox.showinfo("Отмена", "Таймер отменен!")
    if a == 1:
        print(sliding_menu.time_left_label._text)
        print("TRUE")
        sleep_timer.cancel()
        sliding_menu.reset_timer_display()  # Сбрасываем отображение
        print(sliding_menu.time_left_label._text)
        # time.sleep(1)


app = CTk()
app.title("Таймер сна")
app.geometry("400x250")

# Инициализация выезжающего меню
sliding_menu = SlidingMenu(app)

main_frame = CTkFrame(master=app)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

label = CTkLabel(master=main_frame, text="Укажите время до сна (в секундах):")
label.pack()

time_options = [
    "10 секунд", "30 секунд", "1 минута", "5 минут",
    "10 минут", "15 минут", "30 минут", "1 час",
    "1.5 часа", "2 часа", "3 часа", "4 часа",
    "5 часов", "6 часов", "7 часов", "8 часов"
]
time_combobox = CTkComboBox(
    master=main_frame,
    values=time_options,
    justify='center',
    width=200,
    height=30
)
time_combobox.pack(pady=5)
time_combobox.set("30 минут")

buttons_frame = CTkFrame(main_frame, fg_color="transparent")
buttons_frame.pack(pady=15)

button_start = CTkButton(master=buttons_frame, text="Запустить таймер", command=start_timer)
button_start.pack(side="left", padx=5)

button_cancel = CTkButton(
    master=buttons_frame,
    text="Отменить",
    command=stop_timer,
    fg_color="#d9534f",
    hover_color="#c9302c",
    state="disabled"
)
button_cancel.pack(side="right", padx=5)

app.mainloop()