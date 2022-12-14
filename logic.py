import twilio_api
from db import con, cur, User, Chat, JoinedChat, TWILIO_PHONES


def login_or_create_user(username, userphone):
    user = cur.execute("select * from users where phone = ?", (userphone,)).fetchone()
    # TODO what to do if username is different?
    # we could surface it or just update it to be the new value
    # but for now we just use the existing name and ignore the one provided when logging in
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


def process_message(from_number, to_number, message):
    chat_id, sender_name = cur.execute("""
        select memberships.chat_id, users.name from memberships
        join users on users.id = memberships.user_id
        where users.phone = ? and memberships.twilio_phone = ?
    """, (from_number, to_number)).fetchone()
    print(f"message from user {sender_name} to group {chat_id}")

    to_users = cur.execute("""
        select memberships.twilio_phone, users.phone from memberships
        join users on users.id = memberships.user_id
        where memberships.chat_id = ?
    """, (chat_id,)).fetchall()

    print(to_users)

    for twilio_number, user_number in to_users:
        print(f"sending sms to {user_number} from {twilio_number}")
        twilio_api.send_message(user_number, twilio_number, f"{sender_name}: {message}")
