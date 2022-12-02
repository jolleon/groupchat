import sqlite3
from collections import namedtuple

import twilio_api


con = sqlite3.connect("groupchat.db", check_same_thread=False)
cur = con.cursor()

# TODO if we're regularly adding or modifying the numbers,
# would be easier to put them in the db as well
TWILIO_PHONES = [
    '+19802944153',
    '+17208079029'
]

User = namedtuple('User', ['id', 'phone', 'name'])
Chat = namedtuple('Chat', ['id', 'name'])
JoinedChat = namedtuple('JoinedChat', ['membership_id', 'chat_id', 'group_name', 'twilio_phone'])


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
    if u is None:
        return None
    return User._make(u)


def get_all_chats():
    return map(Chat._make, cur.execute("select * from chats").fetchall())


def get_user_chats(user_id):
    return map(JoinedChat._make,
        cur.execute("""
            select memberships.id, chats.id, chats.name, memberships.twilio_phone from chats
            join memberships on memberships.chat_id = chats.id
            where memberships.user_id = ?
        """, (user_id,)).fetchall()
    )


def create_chat(name):
    cur.execute("insert into chats (name) values (?)", (name,))
    con.commit()
    return cur.lastrowid


def join_chat(user, chat_id):
    print(f"user {user} wants to join chat {chat_id}")

    user_id = user.id

    # don't join a chat twice
    already_joined = cur.execute("select twilio_phone from memberships where user_id = ? and chat_id = ?", (user_id, chat_id)).fetchone()
    if already_joined is not None:
        print("already joined this chat")
        return

    # find free twilio number
    used_numbers = cur.execute("select twilio_phone from memberships where user_id = ?", (user_id,)).fetchall()
    used_numbers = [n[0] for n in used_numbers]
    print('already used numbers:')
    print(used_numbers)
    twilio_number = None
    for number in TWILIO_PHONES:
        if number not in used_numbers:
            twilio_number = number

    print(twilio_number)
    if twilio_number is None:
        print("already using all phone numbers!")
        raise Exception("no free twilio number")

    cur.execute("insert into memberships (user_id, chat_id, twilio_phone) values (?, ?, ?)", (user_id, chat_id, twilio_number))
    con.commit()

    group_name = cur.execute("select name from chats where id = ?", (chat_id,)).fetchone()[0]
    twilio_api.send_welcome_message(user.phone, twilio_number, group_name)



def leave_chat(membership_id):
    cur.execute("delete from memberships where id = ?", membership_id)
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
