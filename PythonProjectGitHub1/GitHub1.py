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
            args=(seconds),
            daemon=True
        )
        self.timer_thread.start()

    def cancel(self):
        self.cancel_event.set()

    def run_timer(self, seconds):
        for i in range(seconds):
            if self.cancel_events.is_set():
                return
            time.sleep(1)
        if not self.cancel_event.is_set():
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)


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

main_frame = CTkFrame(master=app)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

label = CTkLabel(master=main_frame, text="Укажите время до сна (в секундах):")
label.pack()

time_options = ["10", "30", "60", "120", "300", "600", "1800"]
time_combobox = CTkComboBox(
    master=main_frame, values=time_options, justify='center', width=200, height=30
)
time_combobox.pack(pady=5)
time_combobox.set("600")

buttons_frame = CTkFrame(main_frame, fg_color="transparent")
buttons_frame.pack(pady=15)

button_start = CTkButton(master=buttons_frame, text="Запустить таймер", command=start_timer)
button_start.pack(side="left", padx=5)

button_cancel = CTkButton(master=buttons_frame, text="Отменить", command=stop_timer, fg_color="#d9534f",
                          hover_color="#c9302c", state="disabled")
button_cancel.pack(side="right", padx=5)

app.mainloop()
