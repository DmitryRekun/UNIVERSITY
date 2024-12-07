import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedTk
import sqlite3


class BreadFactoryApp:
    def __init__(self, master, connection_params):
        self.master = master
        self.connection_params = connection_params
        self.master.title("АРМ Работника Хлебозавода")
        self.master.geometry("800x600")  # Устанавливаем стандартный размер окна

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')

        self.conn = sqlite3.connect(**connection_params)
        self.cursor = self.conn.cursor()

        self.table_names = self.get_table_names()

        if not self.table_names:
            messagebox.showwarning(
                "Ошибка", "В базе данных нет таблиц. Пожалуйста, создайте их перед запуском."
            )
            return

        for table_name in self.table_names:
            frame = tk.Frame(self.notebook)
            self.notebook.add(frame, text=table_name)
            self.create_table_view(frame, table_name)

    def get_table_names(self):
        """Получение списка таблиц в базе данных"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in self.cursor.fetchall()]
        return table_names

    def create_table_view(self, frame, table_name):
        """Создание интерфейса для работы с таблицей"""
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in self.cursor.fetchall()]

        tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
        tree.pack(expand=True, fill='both')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        self.populate_treeview(tree, table_name)

        add_button = tk.Button(frame, text="Добавить", command=lambda: self.add_row(tree, table_name))
        add_button.pack(side=tk.LEFT, padx=10)

        delete_button = tk.Button(frame, text="Удалить", command=lambda: self.delete_row(tree, table_name))
        delete_button.pack(side=tk.LEFT, padx=10)

        edit_button = tk.Button(frame, text="Изменить", command=lambda: self.edit_row(tree, table_name))
        edit_button.pack(side=tk.LEFT, padx=10)

        refresh_button = tk.Button(frame, text="Обновить", command=lambda: self.populate_treeview(tree, table_name))
        refresh_button.pack(side=tk.LEFT, padx=10)

    def populate_treeview(self, tree, table_name):
        """Заполнение таблицы данными из базы"""
        self.cursor.execute(f"SELECT * FROM {table_name};")
        data = self.cursor.fetchall()

        tree.delete(*tree.get_children())

        for row in data:
            tree.insert('', 'end', values=row)

    def get_next_id(self, table_name):
        """Получение следующего значения для id"""
        self.cursor.execute(f"SELECT MAX(id) FROM {table_name};")
        max_id = self.cursor.fetchone()[0]
        return (max_id or 0) + 1

    def add_row(self, tree, table_name):
        """Добавление новой строки"""
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in self.cursor.fetchall()]

        add_dialog = tk.Toplevel(self.master)
        add_dialog.title("Добавить строку")

        entry_widgets = []
        for col in columns:
            if col == "id":  # Пропускаем id, так как оно заполняется автоматически
                continue
            label = tk.Label(add_dialog, text=col)
            label.grid(row=columns.index(col), column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(add_dialog)
            entry.grid(row=columns.index(col), column=1, padx=10, pady=5, sticky='w')
            entry_widgets.append((col, entry))

        def insert_row():
            values = {col: entry.get() for col, entry in entry_widgets}
            values['id'] = self.get_next_id(table_name)

            columns_clause = ', '.join(values.keys())
            placeholders = ', '.join(['?' for _ in values])
            query = f"INSERT INTO {table_name} ({columns_clause}) VALUES ({placeholders});"
            try:
                self.cursor.execute(query, tuple(values.values()))
                self.conn.commit()
                self.populate_treeview(tree, table_name)
                add_dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка базы данных", f"Ошибка: {e}")

        submit_button = tk.Button(add_dialog, text="Подтвердить", command=insert_row)
        submit_button.grid(row=len(columns), columnspan=2, pady=10)

    def delete_row(self, tree, table_name):
        """Удаление выбранной строки"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите строку для удаления.")
            return

        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту строку?")
        if not confirm:
            return

        values = tree.item(selected_item)['values']

        where_clause = ' AND '.join([f"{column} = ?" for column in tree['columns']])
        query = f"DELETE FROM {table_name} WHERE {where_clause};"
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.populate_treeview(tree, table_name)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Ошибка: {e}")

    def edit_row(self, tree, table_name):
        """Редактирование выбранной строки"""
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите строку для изменения.")
            return

        values = tree.item(selected_item)['values']

        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in self.cursor.fetchall()]

        edit_dialog = tk.Toplevel(self.master)
        edit_dialog.title("Изменить строку")

        entry_widgets = []
        for col, value in zip(columns, values):
            if col == "id":  # id нельзя изменять
                continue
            label = tk.Label(edit_dialog, text=col)
            label.grid(row=columns.index(col), column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(edit_dialog)
            entry.insert(0, value)
            entry.grid(row=columns.index(col), column=1, padx=10, pady=5, sticky='w')
            entry_widgets.append((col, entry))

        def update_row():
            new_values = {col: entry.get() for col, entry in entry_widgets}
            set_clause = ', '.join([f"{column} = ?" for column in new_values.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?;"
            try:
                self.cursor.execute(query, tuple(new_values.values()) + (values[0],))
                self.conn.commit()
                self.populate_treeview(tree, table_name)
                edit_dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка базы данных", f"Ошибка: {e}")

        submit_button = tk.Button(edit_dialog, text="Подтвердить", command=update_row)
        submit_button.grid(row=len(columns), columnspan=2, pady=10)


if __name__ == "__main__":
    connection_params = {"database": "bread_factory.db"}
    try:
        root = ThemedTk(theme="breeze")
        app = BreadFactoryApp(root, connection_params)
        root.mainloop()
    except sqlite3.Error as err:
        print(f"Ошибка подключения к базе данных: {err}")
