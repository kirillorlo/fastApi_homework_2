from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()


# Модель пользователя
class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: str
    email: str
    address: str


# Создание таблицы пользователей в базе данных
def create_user_table():
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        last_name TEXT,
                        birth_date TEXT,
                        email TEXT,
                        address TEXT
                    )""")
        conn.commit()


# Добавление нового пользователя в базу данных
def create_user(user: User):
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("""INSERT INTO users (
                        first_name, last_name, birth_date, email, address
                    ) VALUES (?, ?, ?, ?, ?)""",
                  (user.first_name, user.last_name, user.birth_date, user.email, user.address))
        conn.commit()
        user.id = c.lastrowid
    return user


# Получение всех пользователей из базы данных
def get_all_users() -> List[User]:
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        rows = c.fetchall()
        users = [User(id=row[0], first_name=row[1], last_name=row[2], birth_date=row[3], email=row[4], address=row[5]) for row in rows]
    return users


# Получение пользователя по ID
def get_user_by_id(user_id: int) -> User:
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        user = User(id=row[0], first_name=row[1], last_name=row[2], birth_date=row[3], email=row[4], address=row[5])
    return user


# Обновление пользователя по ID
def update_user(user_id: int, user: User) -> User:
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("""UPDATE users SET
                        first_name=?, last_name=?, birth_date=?, email=?, address=?
                    WHERE id=?""",
                  (user.first_name, user.last_name, user.birth_date, user.email, user.address, user_id))
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
    user.id = user_id
    return user


# Удаление пользователя по ID
def delete_user(user_id: int):
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")


# Создание таблицы при запуске приложения
create_user_table()


# Методы API для работы с пользователями
@app.post("/users")
def add_user(user: User):
    return create_user(user)


@app.get("/users")
def get_users():
    return get_all_users()


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return get_user_by_id(user_id)


@app.put("/users/{user_id}")
def update_user_handler(user_id: int, user: User):
    return update_user(user_id, user)


@app.delete("/users/{user_id}")
def delete_user_handler(user_id: int):
    delete_user(user_id)
    return {"message": "User deleted successfully"}
