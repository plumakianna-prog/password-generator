import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

# Файл для сохранения истории
HISTORY_FILE = "password_history.json"

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")

        # Переменные
        self.length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.history = self.load_history()

        # Интерфейс
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_slider = ttk.Scale(settings_frame, from_=4, to=64, variable=self.length, orient="horizontal")
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)
        self.length_slider.configure(command=lambda x: self.length_label.configure(text=str(int(float(x)))))

        # Чекбоксы
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(settings_frame, text="Буквы (a-z, A-Z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=1, column=2, sticky="w")

        # Кнопка генерации
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Поле вывода пароля
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 14), state="readonly")
        password_entry.pack(fill="x", padx=10, pady=5)

        # Таблица истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("password", "length", "date")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("date", text="Дата и время")
        self.history_tree.pack(fill="both", expand=True)

        # Кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)

    def generate_password(self):
        # Проверка — выбран ли хоть один тип символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_symbols.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return

        length = self.length.get()
        if length < 4:
            messagebox.showerror("Ошибка", "Длина пароля не может быть меньше 4")
            return
        if length > 64:
            messagebox.showerror("Ошибка", "Длина пароля не может быть больше 64")
            return

        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_symbols.get():
            chars += "!@#$%^&*"

        password = "".join(random.choice(chars) for _ in range(length))
        self.password_var.set(password)

        # Сохраняем в историю
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({"password": password, "length": length, "date": now})
        self.save_history()
        self.update_history_table()

    def update_history_table(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for entry in self.history[-20:]:  # показываем последние 20
            self.history_tree.insert("", "end", values=(entry["password"], entry["length"], entry["date"]))

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def clear_history(self):
        self.history = []
        self.save_history()
        self.update_history_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()