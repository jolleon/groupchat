import sqlite3
from collections import namedtuple


con = sqlite3.connect("groupchat.db", check_same_thread=False)
cur = con.cursor()

# TODO if we're regularly adding or modifying the numbers,
# would be easier to put them in the db as well
TWILIO_PHONES = [
    '+19802944153',
    '+17208079029'
]

# Very basic "models" just to make it a bit nicer to use than sqlite's indexing
User = namedtuple('User', ['id', 'phone', 'name'])
Chat = namedtuple('Chat', ['id', 'name'])
JoinedChat = namedtuple('JoinedChat', ['membership_id', 'chat_id', 'group_name', 'twilio_phone'])


# DB tables creation
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
