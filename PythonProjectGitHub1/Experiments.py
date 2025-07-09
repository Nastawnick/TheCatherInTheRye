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
            target=self._run_timer,
            args=(seconds,),
            daemon=True
        )
        self.timer_thread.start()

    def cancel(self):
        self.cancel_event.set()

    def _run_timer(self, seconds):
        for _ in range(seconds):
            if self.cancel_event.is_set():
                return
            time.sleep(1)

        if not self.cancel_event.is_set():
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)


sleep_timer = SleepTimer()


def start_timer():
    try:
        seconds = int(time_combobox.get())
        if seconds <= 0:
            messagebox.showerror("Ошибка", "Введите положительное число секунд")
            return

        sleep_timer.start(seconds)
        btn_start.configure(state="disabled")
        btn_cancel.configure(state="normal")
        messagebox.showinfo("Успех", f"Таймер установлен на {seconds} секунд\nДля отмены нажмите кнопку 'Отменить'")

    except ValueError:
        messagebox.showerror("Ошибка", "Введите целое число секунд")


def cancel_timer():
    sleep_timer.cancel()
    btn_start.configure(state="normal")
    btn_cancel.configure(state="disabled")
    messagebox.showinfo("Отмена", "Переход в спящий режим отменён")


app = CTk()
app.title("Таймер сна")
app.geometry("400x250")

# Main frame
main_frame = CTkFrame(master=app)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# Time selection
label = CTkLabel(main_frame, text="Укажите время до сна (в секундах):")
label.pack(pady=(10, 5))

time_options = ["10", "30", "60", "120", "300", "600", "1800"]
time_combobox = CTkComboBox(
    main_frame,
    values=time_options,
    justify="center",
    width=200,
    height=30
)
time_combobox.pack(pady=5)
time_combobox.set("30")

# Buttons frame
buttons_frame = CTkFrame(main_frame, fg_color="transparent")
buttons_frame.pack(pady=15)

btn_start = CTkButton(
    buttons_frame,
    text="Запустить таймер",
    command=start_timer
)
btn_start.pack(side="left", padx=5)

btn_cancel = CTkButton(
    buttons_frame,
    text="Отменить",
    command=cancel_timer,
    state="disabled",
    fg_color="#d9534f",  # Красный цвет для кнопки отмены
    hover_color="#c9302c"
)
btn_cancel.pack(side="left", padx=5)

app.mainloop()