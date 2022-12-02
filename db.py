import sqlite3
from collections import namedtuple


con = sqlite3.connect("groupchat.db", check_same_thread=False)
cur = con.cursor()

TWILIO_PHONES = [
    '+19802944153',
]

User = namedtuple('User', ['id', 'phone', 'name'])


def login_or_create_user(username, userphone):
    user = cur.execute("select * from users where phone = ?", (userphone,)).fetchone()
    # TODO what to do if username is different?
    # we could surface it or just update it to be the new value
    print(user)
    if user is None:
        return User(create_user(username, userphone), username, userphone)
    else:
        return User._make(user)


def create_user(username, userphone):
    cur.execute("insert into users (phone, name) values (?, ?)", (userphone, username))
    con.commit()
    return cur.lastrowid


def get_user(user_id):
    u = cur.execute("select * from users where id = ?", (user_id,)).fetchone()
    print(u)
    return User._make(u)


def get_all_chats():
    return cur.execute("select * from chats").fetchall()


def get_user_chats(user_id):
    return cur.execute("""
        select * from chats
        join memberships on memberships.chat_id = chats.id
        where memberships.user_id = ?
    """, (user_id,)).fetchall()


def join_chat(user_id, chat_id):
    already_used_numbers = cur.execute("select twilio_phone from memberships where user_id = ?", (user_id,)).fetchall()
    print(already_used_numbers)
    twilio_number = None
    for number in TWILIO_PHONES:
        if number not in already_used_numbers:
            twilio_number = number

    if twilio_number is None:
        print("already using all phone numbers!")
        raise Exception("no free twilio number")

    cur.execute("insert into memberships (user_id, chat_id, twilio_phone) values (?, ?, ?)", (user_id, chat_id, twilio_number))
    con.commit()


def setup():
    cur.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        phone VARCHAR UNIQUE,
        name VARCHAR
    )
    """)

    cur.execute("""
    CREATE TABLE chats (
        id INTEGER PRIMARY KEY,
        name VARCHAR
    )""")

    cur.execute("""
    CREATE TABLE memberships (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        chat_id INTEGER,
        twilio_phone VARCHAR,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (chat_id) REFERENCES chats (id)
    )""")

    con.commit()


if __name__ == "__main__":
    setup()
