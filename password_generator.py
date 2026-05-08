import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
import datetime

# Файл для сохранения истории
HISTORY_FILE = "password_history.json"

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("720x550")
        self.root.resizable(True, True)

        # Переменные
        self.length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.history = self.load_history_with_exception_handling()

        # Интерфейс
        self.create_widgets()
        self.update_history_table()

    def load_history_with_exception_handling(self):
        """Загрузка истории с обработкой всех возможных ошибок"""
        if not os.path.exists(HISTORY_FILE):
            return []
        
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Проверяем, что данные — это список
                if not isinstance(data, list):
                    raise ValueError("Файл истории повреждён: данные не являются списком")
                
                # Проверяем структуру каждого элемента
                for item in data:
                    if not isinstance(item, dict) or \
                       "password" not in item or \
                       "length" not in item or \
                       "date" not in item:
                        raise ValueError("Файл истории повреждён: некорректная структура записи")
                
                return data
                
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Ошибка загрузки истории",
                f"Файл истории повреждён (ошибка JSON).\n"
                f"Будет создана новая история.\n\nТехническая информация: {e}"
            )
            return []
            
        except (IOError, OSError) as e:
            messagebox.showerror(
                "Ошибка чтения файла",
                f"Не удалось прочитать файл истории.\n"
                f"Будет создана новая история.\n\nОшибка: {e}"
            )
            return []
            
        except ValueError as e:
            messagebox.showerror(
                "Ошибка формата данных",
                f"{e}\nБудет создана новая история."
            )
            return []
            
        except Exception as e:
            messagebox.showerror(
                "Непредвиденная ошибка",
                f"Произошла ошибка при загрузке истории.\n"
                f"Будет создана новая история.\n\nОшибка: {e}"
            )
            return []

    def save_history_with_exception_handling(self):
        """Сохранение истории с обработкой ошибок"""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            return True
            
        except (IOError, OSError) as e:
            messagebox.showerror(
                "Ошибка сохранения",
                f"Не удалось сохранить историю в файл.\n"
                f"Программа продолжит работу, но изменения не будут сохранены.\n\nОшибка: {e}"
            )
            return False
            
        except TypeError as e:
            messagebox.showerror(
                "Ошибка данных",
                f"Невозможно сохранить историю из-за некорректных данных.\n\nОшибка: {e}"
            )
            return False
            
        except Exception as e:
            messagebox.showerror(
                "Непредвиденная ошибка",
                f"Не удалось сохранить историю.\n\nОшибка: {e}"
            )
            return False

    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины (только целые числа)
        ttk.Label(settings_frame, text="Длина пароля (4-64):").grid(row=0, column=0, sticky="w")
        self.length_slider = ttk.Scale(
            settings_frame, 
            from_=4, 
            to=64, 
            variable=self.length, 
            orient="horizontal"
        )
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Поле для ручного ввода длины
        self.length_entry = ttk.Entry(settings_frame, width=5, textvariable=self.length)
        self.length_entry.grid(row=0, column=2, padx=5)
        
        self.length_label = ttk.Label(settings_frame, text="символов")
        self.length_label.grid(row=0, column=3, padx=5)
        
        # Привязываем события для синхронизации ползунка и поля ввода
        self.length_slider.configure(command=self.update_length_from_slider)
        self.length_entry.bind("<FocusOut>", self.validate_length_input)
        self.length_entry.bind("<Return>", self.validate_length_input)

        # Чекбоксы
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w", pady=5)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=1, column=2, sticky="w", pady=5)

        # Кнопка генерации
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=2, column=0, columnspan=4, pady=10)

        # Поле вывода пароля
        password_frame = ttk.LabelFrame(self.root, text="Сгенерированный пароль", padding=10)
        password_frame.pack(fill="x", padx=10, pady=5)
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, font=("Courier", 12), state="readonly")
        password_entry.pack(fill="x")

        # Кнопка копирования
        self.copy_btn = ttk.Button(password_frame, text="Копировать в буфер обмена", command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=5)

        # Таблица истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей (последние 20 записей)", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("password", "length", "date")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("date", text="Дата и время")
        
        # Настройка ширины колонок
        self.history_tree.column("password", width=300)
        self.history_tree.column("length", width=80)
        self.history_tree.column("date", width=150)
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history_with_confirmation).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Экспортировать историю", command=self.export_history).pack(side="left", padx=5)

    def update_length_from_slider(self, value):
        """Обновление значения длины из ползунка"""
        int_value = int(float(value))
        self.length.set(int_value)
        self.length_entry.delete(0, tk.END)
        self.length_entry.insert(0, str(int_value))

    def validate_length_input(self, event=None):
        """Валидация ввода длины (только целые числа в диапазоне 4-64)"""
        try:
            # Получаем значение из поля ввода
            value = self.length_entry.get().strip()
            
            # Проверка на пустое значение
            if not value:
                raise ValueError("Длина не может быть пустой")
            
            # Преобразуем в целое число
            length = int(value)
            
            # Проверка диапазона
            if length < 4:
                raise ValueError("Минимальная длина пароля — 4 символа")
            if length > 64:
                raise ValueError("Максимальная длина пароля — 64 символа")
            
            # Если всё корректно, обновляем значения
            self.length.set(length)
            self.length_slider.set(length)
            
        except ValueError as e:
            # Если ошибка, показываем сообщение и возвращаем предыдущее значение
            messagebox.showerror("Ошибка ввода", str(e))
            # Возвращаем предыдущее корректное значение
            current_value = self.length.get()
            self.length_entry.delete(0, tk.END)
            self.length_entry.insert(0, str(current_value))
            self.length_slider.set(current_value)

    def generate_password(self):
        """Генерация пароля с валидацией"""
        # Валидация длины перед генерацией
        try:
            length = self.length.get()
            if not isinstance(length, int) or length < 4 or length > 64:
                raise ValueError("Длина пароля должна быть целым числом от 4 до 64")
        except (tk.TclError, ValueError):
            messagebox.showerror("Ошибка", "Длина пароля должна быть целым числом от 4 до 64")
            self.length.set(12)
            self.length_slider.set(12)
            self.length_entry.delete(0, tk.END)
            self.length_entry.insert(0, "12")
            return
        
        # Проверка — выбран ли хоть один тип символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_symbols.get()):
            messagebox.showerror(
                "Ошибка генерации",
                "Выберите хотя бы один тип символов!\n\n"
                "Пароль не может быть сгенерирован без символов."
            )
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
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.insert(0, {"password": password, "length": length, "date": now})
        
        # Ограничиваем историю 100 записями
        if len(self.history) > 100:
            self.history = self.history[:100]
        
        self.save_history_with_exception_handling()
        self.update_history_table()
        
        # Показываем сообщение об успешной генерации
        self.root.after(100, lambda: messagebox.showinfo("Успех", "Пароль успешно сгенерирован!"))

    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Копирование", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет сгенерированного пароля для копирования")

    def update_history_table(self):
        """Обновление таблицы истории"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for entry in self.history[:20]:  # показываем последние 20
            self.history_tree.insert("", "end", values=(entry["password"], entry["length"], entry["date"]))

    def clear_history_with_confirmation(self):
        """Очистка истории с подтверждением"""
        if not self.history:
            messagebox.showinfo("Информация", "История уже пуста")
            return
        
        # Диалог подтверждения
        result = messagebox.askyesno(
            "Подтверждение очистки",
            "Вы уверены, что хотите очистить всю историю паролей?\n\n"
            "Это действие нельзя отменить.",
            icon="warning"
        )
        
        if result:
            self.history = []
            if self.save_history_with_exception_handling():
                self.update_history_table()
                messagebox.showinfo("Успех", "История успешно очищена")
            else:
                messagebox.showerror("Ошибка", "Не удалось очистить историю")

    def export_history(self):
        """Экспорт истории в отдельный JSON-файл"""
        if not self.history:
            messagebox.showinfo("Информация", "Нет записей для экспорта")
            return
        
        try:
            from datetime import datetime
            filename = f"password_history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo(
                "Экспорт успешен",
                f"История экспортирована в файл:\n{filename}\n\n"
                f"Всего записей: {len(self.history)}"
            )
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", f"Не удалось экспортировать историю:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
