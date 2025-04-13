import psycopg2
from db_config import config
import pandas as pd

class PhoneBook:
    def __init__(self):
        self.conn = None
        try:
            params = config()
            self.conn = psycopg2.connect(**params)
            self.create_table()
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")

    def create_table(self):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50),
                    phone VARCHAR(15) NOT NULL
                )
            """)
            self.conn.commit()
            cur.close()
        except Exception as e:
            print(f"Ошибка создания таблицы: {e}")

    
    def insert_from_console(self):
        try:
            first_name = input("Введите имя: ")
            last_name = input("Введите фамилию (опционально): ") or None
            phone = input("Введите номер телефона: ")
            
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO contacts (first_name, last_name, phone)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (first_name, last_name, phone))
            
            contact_id = cur.fetchone()[0]
            self.conn.commit()
            print(f"Контакт добавлен с ID: {contact_id}")
            cur.close()
        except Exception as e:
            print(f"Ошибка добавления контакта: {e}")

    
    def insert_from_csv(self, csv_file):
        try:
            df = pd.read_csv(csv_file)
            cur = self.conn.cursor()
            
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO contacts (first_name, last_name, phone)
                    VALUES (%s, %s, %s)
                """, (
                    row['first_name'],
                    row.get('last_name', None),
                    row['phone']
                ))
            
            self.conn.commit()
            print(f"Добавлено {len(df)} контактов из CSV")
            cur.close()
        except Exception as e:
            print(f"Ошибка добавления из CSV: {e}")

    
    def update_contact(self):
        try:
            contact_id = input("Введите ID контакта для обновления: ")
            print("1. Обновить имя")
            print("2. Обновить телефон")
            choice = input("Выберите, что обновить (1-2): ")
            
            cur = self.conn.cursor()
            if choice == '1':
                new_name = input("Введите новое имя: ")
                cur.execute("""
                    UPDATE contacts 
                    SET first_name = %s 
                    WHERE id = %s
                """, (new_name, contact_id))
            elif choice == '2':
                new_phone = input("Введите новый телефон: ")
                cur.execute("""
                    UPDATE contacts 
                    SET phone = %s 
                    WHERE id = %s
                """, (new_phone, contact_id))
            else:
                print("Неверный выбор")
                return
                
            self.conn.commit()
            print("Контакт успешно обновлен")
            cur.close()
        except Exception as e:
            print(f"Ошибка обновления контакта: {e}")

   
    def query_contacts(self):
        try:
            print("1. Показать все контакты")
            print("2. Поиск по имени")
            print("3. Поиск по телефону")
            choice = input("Выберите тип запроса (1-3): ")
            
            cur = self.conn.cursor()
            if choice == '1':
                cur.execute("SELECT * FROM contacts")
            elif choice == '2':
                name = input("Введите имя для поиска: ")
                cur.execute("SELECT * FROM contacts WHERE first_name ILIKE %s", (f'%{name}%',))
            elif choice == '3':
                phone = input("Введите телефон для поиска: ")
                cur.execute("SELECT * FROM contacts WHERE phone ILIKE %s", (f'%{phone}%',))
            else:
                print("Неверный выбор")
                return
                
            rows = cur.fetchall()
            for row in rows:
                print(f"ID: {row[0]}, Имя: {row[1]} {row[2] or ''}, Телефон: {row[3]}")
            cur.close()
        except Exception as e:
            print(f"Ошибка запроса контактов: {e}")

   
    def delete_contact(self):
        try:
            print("1. Удалить по имени")
            print("2. Удалить по телефону")
            choice = input("Выберите способ удаления (1-2): ")
            
            cur = self.conn.cursor()
            if choice == '1':
                name = input("Введите имя для удаления: ")
                cur.execute("DELETE FROM contacts WHERE first_name = %s", (name,))
            elif choice == '2':
                phone = input("Введите телефон для удаления: ")
                cur.execute("DELETE FROM contacts WHERE phone = %s", (phone,))
            else:
                print("Неверный выбор")
                return
                
            self.conn.commit()
            print("Контакт успешно удален")
            cur.close()
        except Exception as e:
            print(f"Ошибка удаления контакта: {e}")

    def __del__(self):
        if self.conn is not None:
            self.conn.close()


def main():
    phonebook = PhoneBook()
    
    while True:
        print("\nМеню PhoneBook:")
        print("1. Добавить контакт через консоль")
        print("2. Добавить контакты из CSV")
        print("3. Обновить контакт")
        print("4. Показать контакты")
        print("5. Удалить контакт")
        print("6. Выход")
        
        choice = input("Введите ваш выбор (1-6): ")
        
        if choice == '1':
            phonebook.insert_from_console()
        elif choice == '2':
            csv_file = input("Введите путь к CSV файлу: ")
            phonebook.insert_from_csv(csv_file)
        elif choice == '3':
            phonebook.update_contact()
        elif choice == '4':
            phonebook.query_contacts()
        elif choice == '5':
            phonebook.delete_contact()
        elif choice == '6':
            break
        else:
            print("Неверный выбор")

if __name__ == '__main__':
    main()