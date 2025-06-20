import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class SanatoriumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Санаторий: система учета")
        self.root.geometry("1000x600")
        
        # Подключение к БД
        self.conn = sqlite3.connect('sanatorium.db')
        self.create_tables()
        
        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        # Вкладка отдыхающих
        self.guests_frame = ttk.Frame(self.notebook)
        self.create_guests_tab()
        self.notebook.add(self.guests_frame, text="Отдыхающие")
        
        # Вкладка услуг
        self.services_frame = ttk.Frame(self.notebook)
        self.create_services_tab()
        self.notebook.add(self.services_frame, text="Платные услуги")
        
        # Вкладка записи на прием
        self.appointments_frame = ttk.Frame(self.notebook)
        self.create_appointments_tab()
        self.notebook.add(self.appointments_frame, text="Запись на прием")
        
        # Заполняем данные
        self.update_guests_tree()
        self.update_services_tree()
        self.update_appointments_tree()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Таблица отдыхающих
        cursor.execute('''CREATE TABLE IF NOT EXISTS guests (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            last_name TEXT NOT NULL,
                            first_name TEXT NOT NULL,
                            middle_name TEXT,
                            birth_date TEXT,
                            passport TEXT,
                            phone TEXT,
                            check_in_date TEXT,
                            check_out_date TEXT,
                            room TEXT,
                            notes TEXT)''')
        
        # Таблица услуг
        cursor.execute('''CREATE TABLE IF NOT EXISTS services (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            description TEXT,
                            price REAL NOT NULL,
                            duration INTEGER)''')
        
        # Таблица записей
        cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guest_id INTEGER NOT NULL,
                            service_id INTEGER NOT NULL,
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            status TEXT DEFAULT 'Запланирован',
                            FOREIGN KEY (guest_id) REFERENCES guests (id),
                            FOREIGN KEY (service_id) REFERENCES services (id))''')
        
        self.conn.commit()
    
    def create_guests_tab(self):
        # Форма добавления отдыхающего
        input_frame = ttk.LabelFrame(self.guests_frame, text="Добавить/Изменить отдыхающего")
        input_frame.pack(fill='x', padx=10, pady=5)
        
        labels = ['Фамилия:', 'Имя:', 'Отчество:', 'Дата рождения:', 'Паспорт:', 
                 'Телефон:', 'Дата заезда:', 'Дата выезда:', 'Номер комнаты:', 'Примечания:']
        
        self.guest_entries = {}
        for i, label in enumerate(labels):
            lbl = ttk.Label(input_frame, text=label)
            lbl.grid(row=i//2, column=(i%2)*2, padx=5, pady=5, sticky='e')
            
            entry = ttk.Entry(input_frame)
            entry.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5, sticky='we')
            self.guest_entries[label[:-1].lower()] = entry
        
        # Кнопки
        btn_frame = ttk.Frame(self.guests_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Добавить", command=self.add_guest).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_guest).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_guest).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_guest_form).pack(side='left', padx=5)
        
        # Таблица отдыхающих
        tree_frame = ttk.Frame(self.guests_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('id', 'last_name', 'first_name', 'middle_name', 'birth_date', 
                   'passport', 'phone', 'check_in_date', 'check_out_date', 'room')
        
        self.guests_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Настройка колонок
        self.guests_tree.heading('id', text='ID')
        self.guests_tree.heading('last_name', text='Фамилия')
        self.guests_tree.heading('first_name', text='Имя')
        self.guests_tree.heading('middle_name', text='Отчество')
        self.guests_tree.heading('birth_date', text='Дата рождения')
        self.guests_tree.heading('passport', text='Паспорт')
        self.guests_tree.heading('phone', text='Телефон')
        self.guests_tree.heading('check_in_date', text='Дата заезда')
        self.guests_tree.heading('check_out_date', text='Дата выезда')
        self.guests_tree.heading('room', text='Комната')
        
        for col in columns:
            self.guests_tree.column(col, width=100, anchor='w')
        
        self.guests_tree.pack(side='left', fill='both', expand=True)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.guests_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.guests_tree.configure(yscrollcommand=scrollbar.set)
        
        # Привязка события выбора
        self.guests_tree.bind('<<TreeviewSelect>>', self.on_guest_select)
    
    def create_services_tab(self):
        # Форма добавления услуги
        input_frame = ttk.LabelFrame(self.services_frame, text="Добавить/Изменить услугу")
        input_frame.pack(fill='x', padx=10, pady=5)
        
        labels = ['Название:', 'Описание:', 'Цена:', 'Длительность (мин):']
        
        self.service_entries = {}
        for i, label in enumerate(labels):
            lbl = ttk.Label(input_frame, text=label)
            lbl.grid(row=i, column=0, padx=5, pady=5, sticky='e')
            
            entry = ttk.Entry(input_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='we')
            key = label.split(':')[0].lower()
            self.service_entries[key] = entry
        
        # Кнопки
        btn_frame = ttk.Frame(self.services_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Добавить", command=self.add_service).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_service).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_service).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_service_form).pack(side='left', padx=5)
        
        # Таблица услуг
        tree_frame = ttk.Frame(self.services_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('id', 'name', 'description', 'price', 'duration')
        
        self.services_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Настройка колонок
        self.services_tree.heading('id', text='ID')
        self.services_tree.heading('name', text='Название')
        self.services_tree.heading('description', text='Описание')
        self.services_tree.heading('price', text='Цена')
        self.services_tree.heading('duration', text='Длительность (мин)')
        
        for col in columns:
            self.services_tree.column(col, width=120, anchor='w')
        
        self.services_tree.pack(side='left', fill='both', expand=True)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.services_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.services_tree.configure(yscrollcommand=scrollbar.set)
        
        # Привязка события выбора
        self.services_tree.bind('<<TreeviewSelect>>', self.on_service_select)
    
    def create_appointments_tab(self):
        # Форма добавления записи
        input_frame = ttk.LabelFrame(self.appointments_frame, text="Добавить/Изменить запись")
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Выбор отдыхающего
        ttk.Label(input_frame, text="Отдыхающий:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.guest_combobox = ttk.Combobox(input_frame, state='readonly')
        self.guest_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='we')
        
        # Выбор услуги
        ttk.Label(input_frame, text="Услуга:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.service_combobox = ttk.Combobox(input_frame, state='readonly')
        self.service_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        # Дата и время
        ttk.Label(input_frame, text="Дата:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.appointment_date_entry = ttk.Entry(input_frame)
        self.appointment_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky='we')
        
        ttk.Label(input_frame, text="Время:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.appointment_time_entry = ttk.Entry(input_frame)
        self.appointment_time_entry.grid(row=3, column=1, padx=5, pady=5, sticky='we')
        
        # Статус
        ttk.Label(input_frame, text="Статус:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.appointment_status_combobox = ttk.Combobox(input_frame, values=['Запланирован', 'Выполнен', 'Отменен'])
        self.appointment_status_combobox.grid(row=4, column=1, padx=5, pady=5, sticky='we')
        
        # Кнопки
        btn_frame = ttk.Frame(self.appointments_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Добавить", command=self.add_appointment).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_appointment).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_appointment).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_appointment_form).pack(side='left', padx=5)
        
        # Таблица записей
        tree_frame = ttk.Frame(self.appointments_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('id', 'guest_name', 'service_name', 'date', 'time', 'status')
        
        self.appointments_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Настройка колонок
        self.appointments_tree.heading('id', text='ID')
        self.appointments_tree.heading('guest_name', text='Отдыхающий')
        self.appointments_tree.heading('service_name', text='Услуга')
        self.appointments_tree.heading('date', text='Дата')
        self.appointments_tree.heading('time', text='Время')
        self.appointments_tree.heading('status', text='Статус')
        
        for col in columns:
            self.appointments_tree.column(col, width=120, anchor='w')
        
        self.appointments_tree.pack(side='left', fill='both', expand=True)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.appointments_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.appointments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Привязка события выбора
        self.appointments_tree.bind('<<TreeviewSelect>>', self.on_appointment_select)
        
        # Обновляем комбобоксы
        self.update_comboboxes()
    
    def update_comboboxes(self):
        # Обновление комбобоксов отдыхающих
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, last_name || ' ' || first_name || ' ' || COALESCE(middle_name, '') FROM guests")
        guests = cursor.fetchall()
        self.guest_combobox['values'] = [f"{g[0]}: {g[1]}" for g in guests]
        
        # Обновление комбобоксов услуг
        cursor.execute("SELECT id, name FROM services")
        services = cursor.fetchall()
        self.service_combobox['values'] = [f"{s[0]}: {s[1]}" for s in services]
    
    # Методы для работы с отдыхающими
    def add_guest(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO guests 
                            (last_name, first_name, middle_name, birth_date, passport, phone, 
                             check_in_date, check_out_date, room, notes) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (self.guest_entries['фамилия'].get(),
                             self.guest_entries['имя'].get(),
                             self.guest_entries['отчество'].get(),
                             self.guest_entries['дата рождения'].get(),
                             self.guest_entries['паспорт'].get(),
                             self.guest_entries['телефон'].get(),
                             self.guest_entries['дата заезда'].get(),
                             self.guest_entries['дата выезда'].get(),
                             self.guest_entries['номер комнаты'].get(),
                             self.guest_entries['примечания'].get()))
            self.conn.commit()
            self.update_guests_tree()
            self.update_comboboxes()
            self.clear_guest_form()
            messagebox.showinfo("Успех", "Отдыхающий успешно добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении отдыхающего: {str(e)}")
    
    def update_guest(self):
        selected = self.guests_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите отдыхающего для изменения")
            return
        
        guest_id = self.guests_tree.item(selected[0])['values'][0]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''UPDATE guests SET 
                            last_name = ?, first_name = ?, middle_name = ?, birth_date = ?, 
                            passport = ?, phone = ?, check_in_date = ?, check_out_date = ?, 
                            room = ?, notes = ? WHERE id = ?''',
                            (self.guest_entries['фамилия'].get(),
                             self.guest_entries['имя'].get(),
                             self.guest_entries['отчество'].get(),
                             self.guest_entries['дата рождения'].get(),
                             self.guest_entries['паспорт'].get(),
                             self.guest_entries['телефон'].get(),
                             self.guest_entries['дата заезда'].get(),
                             self.guest_entries['дата выезда'].get(),
                             self.guest_entries['номер комнаты'].get(),
                             self.guest_entries['примечания'].get(),
                             guest_id))
            self.conn.commit()
            self.update_guests_tree()
            self.update_comboboxes()
            messagebox.showinfo("Успех", "Данные отдыхающего успешно обновлены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении данных: {str(e)}")
    
    def delete_guest(self):
        selected = self.guests_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите отдыхающего для удаления")
            return
        
        guest_id = self.guests_tree.item(selected[0])['values'][0]
        
        try:
            # Проверка на наличие записей
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE guest_id = ?", (guest_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                messagebox.showwarning("Предупреждение", 
                                     "Нельзя удалить отдыхающего с активными записями. Сначала удалите все записи.")
                return
            
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого отдыхающего?"):
                cursor.execute("DELETE FROM guests WHERE id = ?", (guest_id,))
                self.conn.commit()
                self.update_guests_tree()
                self.update_comboboxes()
                self.clear_guest_form()
                messagebox.showinfo("Успех", "Отдыхающий успешно удален")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении отдыхающего: {str(e)}")
    
    def clear_guest_form(self):
        for entry in self.guest_entries.values():
            entry.delete(0, tk.END)
    
    def update_guests_tree(self):
        # Очистка дерева
        for item in self.guests_tree.get_children():
            self.guests_tree.delete(item)
        
        # Заполнение данными
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM guests")
        guests = cursor.fetchall()
        
        for guest in guests:
            self.guests_tree.insert('', 'end', values=guest)
    
    def on_guest_select(self, event):
        selected = self.guests_tree.selection()
        if not selected:
            return
        
        guest = self.guests_tree.item(selected[0])['values']
        
        # Заполнение формы
        self.clear_guest_form()
        
        self.guest_entries['фамилия'].insert(0, guest[1])
        self.guest_entries['имя'].insert(0, guest[2])
        self.guest_entries['отчество'].insert(0, guest[3] if guest[3] else '')
        self.guest_entries['дата рождения'].insert(0, guest[4] if guest[4] else '')
        self.guest_entries['паспорт'].insert(0, guest[5] if guest[5] else '')
        self.guest_entries['телефон'].insert(0, guest[6] if guest[6] else '')
        self.guest_entries['дата заезда'].insert(0, guest[7] if guest[7] else '')
        self.guest_entries['дата выезда'].insert(0, guest[8] if guest[8] else '')
        self.guest_entries['номер комнаты'].insert(0, guest[9] if guest[9] else '')
        self.guest_entries['примечания'].insert(0, guest[10] if guest[10] else '')
    
    # Методы для работы с услугами
    def add_service(self):
        try:
            price = float(self.service_entries['цена'].get())
            duration = int(self.service_entries['длительность (мин)'].get())
            
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO services 
                            (name, description, price, duration) 
                            VALUES (?, ?, ?, ?)''',
                            (self.service_entries['название'].get(),
                             self.service_entries['описание'].get(),
                             price,
                             duration))
            self.conn.commit()
            self.update_services_tree()
            self.update_comboboxes()
            self.clear_service_form()
            messagebox.showinfo("Успех", "Услуга успешно добавлена")
        except ValueError:
            messagebox.showerror("Ошибка", "Цена и длительность должны быть числами")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении услуги: {str(e)}")
    
    def update_service(self):
        selected = self.services_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите услугу для изменения")
            return
        
        service_id = self.services_tree.item(selected[0])['values'][0]
        
        try:
            price = float(self.service_entries['цена'].get())
            duration = int(self.service_entries['длительность (мин)'].get())
            
            cursor = self.conn.cursor()
            cursor.execute('''UPDATE services SET 
                            name = ?, description = ?, price = ?, duration = ? 
                            WHERE id = ?''',
                            (self.service_entries['название'].get(),
                             self.service_entries['описание'].get(),
                             price,
                             duration,
                             service_id))
            self.conn.commit()
            self.update_services_tree()
            self.update_comboboxes()
            messagebox.showinfo("Успех", "Данные услуги успешно обновлены")
        except ValueError:
            messagebox.showerror("Ошибка", "Цена и длительность должны быть числами")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении данных: {str(e)}")
    
    def delete_service(self):
        selected = self.services_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите услугу для удаления")
            return
        
        service_id = self.services_tree.item(selected[0])['values'][0]
        
        try:
            # Проверка на наличие записей
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE service_id = ?", (service_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                messagebox.showwarning("Предупреждение", 
                                     "Нельзя удалить услугу с активными записями. Сначала удалите все записи.")
                return
            
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту услугу?"):
                cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
                self.conn.commit()
                self.update_services_tree()
                self.update_comboboxes()
                self.clear_service_form()
                messagebox.showinfo("Успех", "Услуга успешно удалена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении услуги: {str(e)}")
    
    def clear_service_form(self):
        for entry in self.service_entries.values():
            entry.delete(0, tk.END)
    
    def update_services_tree(self):
        # Очистка дерева
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
        
        # Заполнение данными
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM services")
        services = cursor.fetchall()
        
        for service in services:
            self.services_tree.insert('', 'end', values=service)
    
    def on_service_select(self, event):
        selected = self.services_tree.selection()
        if not selected:
            return
        
        service = self.services_tree.item(selected[0])['values']
        
        # Заполнение формы
        self.clear_service_form()
        
        self.service_entries['название'].insert(0, service[1])
        self.service_entries['описание'].insert(0, service[2] if service[2] else '')
        self.service_entries['цена'].insert(0, str(service[3]))
        self.service_entries['длительность (мин)'].insert(0, str(service[4]))
    
    # Методы для работы с записями
    def add_appointment(self):
        try:
            if not self.guest_combobox.get() or not self.service_combobox.get():
                messagebox.showerror("Ошибка", "Выберите отдыхающего и услугу")
                return

            if not self.appointment_status_combobox.get():
                self.appointment_status_combobox.set("Запланирован")

            guest_id = int(self.guest_combobox.get().partition(':')[0])
            service_id = int(self.service_combobox.get().partition(':')[0])
            date = self.appointment_date_entry.get()
            time = self.appointment_time_entry.get()
            status = self.appointment_status_combobox.get()

            # Проверка даты и времени
            datetime.strptime(date, '%d.%m.%Y')
            datetime.strptime(time, '%H:%M')

            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO appointments 
                              (guest_id, service_id, date, time, status) 
                              VALUES (?, ?, ?, ?, ?)''',
                           (guest_id, service_id, date, time, status))
            self.conn.commit()
            self.update_appointments_tree()
            self.clear_appointment_form()
            messagebox.showinfo("Успех", "Запись успешно добавлена")
        except ValueError as ve:
            messagebox.showerror("Ошибка", f"Некорректный формат данных: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении записи: {str(e)}")


    
    def update_appointment(self):
        selected = self.appointments_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для изменения")
            return
        
        appointment_id = self.appointments_tree.item(selected[0])['values'][0]
        
        try:
            guest_id = int(self.guest_combobox.get().partition(':')[0])
            service_id = int(self.service_combobox.get().partition(':')[0])
            date = self.appointment_date_entry.get()
            time = self.appointment_time_entry.get()
            status = self.appointment_status_combobox.get()
            
            # Проверка даты и времени
            datetime.strptime(date, '%d.%m.%Y')
            datetime.strptime(time, '%H:%M')
           
            cursor = self.conn.cursor()
            cursor.execute('''UPDATE appointments SET 
                            guest_id = ?, service_id = ?, date = ?, time = ?, status = ? 
                            WHERE id = ?''',
                            (guest_id, service_id, date, time, status, appointment_id))
            self.conn.commit()
            self.update_appointments_tree()
            messagebox.showinfo("Успех", "Запись успешно обновлена")
        except ValueError as ve:
            messagebox.showerror("Ошибка", f"Некорректный формат данных: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении записи: {str(e)}")
    
    def delete_appointment(self):
        selected = self.appointments_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        appointment_id = self.appointments_tree.item(selected[0])['values'][0]
        
        try:
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?"):
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
                self.conn.commit()
                self.update_appointments_tree()
                self.clear_appointment_form()
                messagebox.showinfo("Успех", "Запись успешно удалена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении записи: {str(e)}")
    
    def clear_appointment_form(self):
        self.guest_combobox.set('')
        self.service_combobox.set('')
        self.appointment_date_entry.delete(0, tk.END)
        self.appointment_time_entry.delete(0, tk.END)
    
    def update_appointments_tree(self):
        # Очистка дерева
        for item in self.appointments_tree.get_children():
            self.appointments_tree.delete(item)
        
        # Заполнение данными с объединением таблиц
        cursor = self.conn.cursor()
        cursor.execute('''SELECT a.id, 
                         g.last_name || ' ' || g.first_name || ' ' || COALESCE(g.middle_name, ''), 
                         s.name, a.date, a.time, a.status 
                         FROM appointments a
                         JOIN guests g ON a.guest_id = g.id
                         JOIN services s ON a.service_id = s.id''')
        appointments = cursor.fetchall()
        
        for app in appointments:
            self.appointments_tree.insert('', 'end', values=app)
    
    def on_appointment_select(self, event):
        selected = self.appointments_tree.selection()
        if not selected:
            return
        
        appointment = self.appointments_tree.item(selected[0])['values']
        
        # Заполнение формы
        self.clear_appointment_form()
        
        # Находим ID гостя и услуги по имени
        cursor = self.conn.cursor()
        
        # Гость
        cursor.execute("SELECT id FROM guests WHERE last_name || ' ' || first_name || ' ' || COALESCE(middle_name, '') = ?", 
                      (appointment[1],))
        guest_id = cursor.fetchone()[0]
        
        # Услуга
        cursor.execute("SELECT id FROM services WHERE name = ?", (appointment[2],))
        service_id = cursor.fetchone()[0]
        
        # Устанавливаем значения в комбобоксы
        self.guest_combobox.set(f"{guest_id}: {appointment[1]}")
        self.service_combobox.set(f"{service_id}: {appointment[2]}")
        
        # Остальные поля
        self.appointment_date_entry.insert(0, appointment[3])
        self.appointment_time_entry.insert(0, appointment[4])
        self.appointment_status_combobox.set(appointment[5])
    
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SanatoriumApp(root)
    root.mainloop()