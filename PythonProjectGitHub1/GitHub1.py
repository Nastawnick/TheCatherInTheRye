import os
import time
import threading
import ctypes
from tkinter import messagebox
from customtkinter import CTk, CTkButton, CTkComboBox, CTkLabel, CTkFrame


class SleepTimer:
    def __init__(self):
        self.cancel_event = threading.Event()
        self.lock = threading.Lock()
        self.timer_thread = None
        self.remaining_time = 0
        self.total_time = 0
        self.update_callback = None
        self.active = False
        self.current_timer_id = 0

    def start(self, seconds, callback=None):
        self.cancel()
        self.cancel_event.clear()

        self.current_timer_id += 1
        timer_id = self.current_timer_id

        self.total_time = seconds
        self.remaining_time = seconds
        self.update_callback = callback
        self.active = True

        self.timer_thread = threading.Thread(
            target=self.run_timer,
            args=(seconds, timer_id),
            daemon=True
        )
        self.timer_thread.start()

    def cancel(self):
        with self.lock:
            self.cancel_event.set()
            self.active = False
            self.remaining_time = 0
            if self.update_callback:
                app.after(0, lambda: self.update_callback(0))

    def run_timer(self, seconds, timer_id):
        for i in range(seconds):
            if not self.should_continue(timer_id) or not self.active:
                return

            remaining = int(seconds - i - 1)
            self._update_remaining_time(remaining)
            time.sleep(1)

        if self.should_continue(timer_id):
            self._trigger_sleep()

    def should_continue(self, timer_id):
        return timer_id == self.current_timer_id

    def _update_remaining_time(self, remaining):
        with self.lock:
            if remaining != self.remaining_time:
                self.remaining_time = remaining
                if self.update_callback:
                    app.after(0, lambda: self.update_callback(remaining))

    def _trigger_sleep(self):
        if self.should_continue(self.current_timer_id):
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)


def format_time(seconds):
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

        self.menu = CTkFrame(
            master=parent,
            width=self.menu_width,
            height=parent.winfo_height(),
            corner_radius=3,
            fg_color="#D3D3D3"
        )
        self.menu.lift()
        self.menu.place(x=-self.menu_width, y=0, relheight=1)

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
        self._setup_menu_content()

        parent.bind("<Enter>", self._check_mouse_position)
        parent.bind("<Motion>", self._check_mouse_position)
        parent.bind("<Leave>", self._check_mouse_position)

    def _setup_menu_content(self):
        CTkLabel(
            self.menu,
            text="Меню таймера",
            text_color="#333333",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", padx=10, pady=(15, 5))

        CTkFrame(self.menu, height=2, fg_color="#cccccc").pack(fill="x", pady=5)

        self.timer_label.pack(fill="x", padx=10, pady=(5, 0))
        self.time_left_label.pack(fill="x", padx=10, pady=(0, 10))

        CTkFrame(self.menu, height=2, fg_color="#cccccc").pack(fill="x", pady=5)

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
        stop_timer(True)
        time_str = time_combobox.get()
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

        sleep_timer.cancel()
        display_time = format_time(seconds)
        sleep_timer.start(seconds, sliding_menu.update_timer_display)
        button_cancel.configure(state="normal")
        messagebox.showinfo("Успех", f"Таймер установлен на {display_time}\nДля отмены нажмите 'Отменить'")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректное значение")


def stop_timer(by_start_timer=False):
    sleep_timer.cancel()
    sliding_menu.reset_timer_display()
    button_cancel.configure(state="disabled")
    if not by_start_timer:
        messagebox.showinfo("Отмена", "Таймер отменен!")


app = CTk()
app.title("Таймер сна")
app.geometry("400x250")

sliding_menu = SlidingMenu(app)

main_frame = CTkFrame(master=app)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

label = CTkLabel(master=main_frame, text="Укажите время до сна (в секундах):")
label.pack()

time_options = [
    "3 секунды", "10 секунд", "30 секунд", "1 минута", "5 минут",
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