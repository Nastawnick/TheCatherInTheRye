import os
import tkinter as tk
from tkinter import messagebox
import subprocess

VBS_SCRIPT = 'sleep.vbs'


def create_vbs_script():
    if not os.path.exists(VBS_SCRIPT):
        vbs_content = ('''seconds = WScript.Arguments.Item(0)

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c timeout /t " & seconds & " /nobreak && rundll32.exe powrprof.dll,SetSuspendState 0,1,0", 0, False''')
        with open(VBS_SCRIPT, 'w') as f:
            f.write(vbs_content)


def start_timer():
    try:
        seconds = int(entry.get())
        if seconds < 0:
            messagebox.showerror("Ошибка значения", "Введите положительное число секунд")
            return
        subprocess.Popen(['wscript.exe', VBS_SCRIPT, str(seconds)])
        messagebox.showinfo("Успех",f"Таймер установлен на {seconds} секунд\nПриложение можно закрыть")
        root.destroy()
    except ValueError:
        messagebox.showerror("Ошибка", "Введите целое число секунд")


root = tk.Tk()
root.title('Таймер сна')
root.geometry('300x150')

create_vbs_script()

tk.Label(root, text="Через сколько секунд перевести компьютер в сон?").pack(pady=10)
entry = tk.Entry(root)
entry.pack(pady=5)
entry.insert(0, '30')

tk.Button(root, text="Запустить таймер", command=start_timer).pack(pady=15)

root.mainloop()
