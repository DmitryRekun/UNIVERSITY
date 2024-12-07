import sqlite3


def create_tables():
    connection = sqlite3.connect("bread_factory.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Работники (
        id INTEGER PRIMARY KEY,
        ФИО TEXT NOT NULL,
        Должность TEXT NOT NULL,
        Стаж INTEGER DEFAULT 0,
        Контактный_телефон TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Ингредиенты (
        id INTEGER PRIMARY KEY,
        Название TEXT NOT NULL,
        Количество REAL NOT NULL,
        Поставщик TEXT,
        Стоимость_за_кг REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Хлебные_изделия (
        id INTEGER PRIMARY KEY,
        Название_изделия TEXT NOT NULL,
        Ингредиенты TEXT,
        Количество_произведенных_единиц INTEGER DEFAULT 0,
        Дата_производства TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Стоимость_и_расценки (
        id INTEGER PRIMARY KEY,
        Название_изделия TEXT NOT NULL,
        Себестоимость REAL NOT NULL,
        Розничная_цена REAL NOT NULL,
        Дата_изменения_стоимости TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Заказчики (
        id INTEGER PRIMARY KEY,
        Название TEXT NOT NULL,
        Название_заказанного_изделия TEXT NOT NULL,
        Дата_заказа TEXT NOT NULL,
        Дата_исполнения TEXT NOT NULL,
        Количество_заказанных_единиц INTEGER NOT NULL
    );
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
