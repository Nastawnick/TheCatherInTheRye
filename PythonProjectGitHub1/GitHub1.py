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

    def start(self, seconds):
        self.cancel_event.clear()
        self.timer_thread = threading.Thread(
            target=self.run_timer,
            args=(seconds,),
            daemon=True
        )
        self.timer_thread.start()

    def cancel(self):
        self.cancel_event.set()

    def run_timer(self, seconds):
        for i in range(seconds):
            if self.cancel_event.is_set():
                return
            time.sleep(1)
        if not self.cancel_event.is_set():
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)


class SlidingMenu:
    def __init__(self, parent):
        self.parent = parent
        self.menu_shown = False
        self.menu_width = 200
        self.animation_speed = 15

        # Создаем меню (изначально скрыто за левым краем)
        self.menu = CTkFrame(
            master=parent,
            width=self.menu_width,
            height=parent.winfo_height(),
            corner_radius=0,
            fg_color="#f0f0f0"
        )
        self.menu.place(x=-self.menu_width, y=0, relheight=1)
        self.menu.lift()  # Поднимаем меню на передний план

        # Добавляем содержимое меню
        self._setup_menu_content()

        # Привязываем события мыши
        parent.bind("<Enter>", self._check_mouse_position)
        parent.bind("<Motion>", self._check_mouse_position)
        parent.bind("<Leave>", lambda e: self.hide_menu() if self.menu_shown else None)

    def _setup_menu_content(self):
        # Заголовок меню
        CTkLabel(
            self.menu,
            text="Меню",
            text_color="#333333",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", padx=10, pady=(15, 10))

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
            btn.pack(fill="x", padx=0, pady=0)
            CTkFrame(self.menu, height=1, fg_color="#e0e0e0").pack(fill="x")

    def _check_mouse_position(self, event):
        # Показываем меню только если курсор в левых 10 пикселях окна
        if event.x < 10 and not self.menu_shown:
            self.show_menu()
        elif event.x > self.menu_width and self.menu_shown:
            self.hide_menu()

    def show_menu(self):
        if not self.menu_shown:
            self.menu_shown = True
            self._animate_menu(0)
            self.menu.lift()  # Поднимаем меню на передний план при показе

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
        seconds = int(time_combobox.get())
        if seconds < 0:
            messagebox.showerror("Ошибка", "Введите положительное число секунд")
            return

        sleep_timer.start(seconds)
        button_cancel.configure(state="normal")
        messagebox.showinfo("Успех", f"Таймер установлен на {seconds} секунд\nДля отмены нажмите кнопку 'Отменить'")
    except ValueError:
        messagebox.showerror()


def stop_timer():
    sleep_timer.cancel()
    button_cancel.configure(state="disabled")
    messagebox.showinfo("Отмена", "Таймер отменен!")


app = CTk()
app.title("Таймер сна")
app.geometry("400x250")

# Инициализация выезжающего меню
sliding_menu = SlidingMenu(app)

main_frame = CTkFrame(master=app)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

label = CTkLabel(master=main_frame, text="Укажите время до сна (в секундах):")
label.pack()

time_options = ["10", "30", "60", "120", "300", "600", "1800"]
time_combobox = CTkComboBox(
    master=main_frame,
    values=time_options,
    justify='center',
    width=200,
    height=30
)
time_combobox.pack(pady=5)
time_combobox.set("600")

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
