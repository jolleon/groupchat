from flask import Flask, request, redirect, render_template, session
from twilio.twiml.messaging_response import MessagingResponse

import logic


app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO env or generate


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    from_number = request.values.get('From')
    to_number = request.values.get('To')
    body = request.values.get('Body')
    print(from_number, to_number, body)

    logic.process_message(from_number, to_number, body)

    resp = MessagingResponse()
    return str(resp)


@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect('/login')
    user = logic.get_user(session["user_id"])
    if user is None:
        # something weird - user got deleted? make them login again
        return redirect('/logout')
    all_chats = logic.get_all_chats()
    my_chats = logic.get_user_chats(user.id)
    return render_template('index.html', user=user, all_chats=all_chats, my_chats=my_chats)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        phone = request.form['userphone']
        user = logic.login_or_create_user(name, phone)
        session['user_id'] = user.id
        return redirect('/')
    return '''
        <form method="post">
            <p><input type=text name=username placeholder=username>
            <p><input type=text name=userphone placeholder="+14151234567">
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/chats', methods=['POST'])
def create_chat():
    # This endpoint is a bit overloaded - if we had a proper JS frontend
    # I'd cleanup the API to something like:
    # POST /chats: create new chat
    # POST /me/chats {chat_id: 123}: join a chat
    # DELETE /me/chats {chat_id: 123}: leave a chat
    # (for instance... could be /me or /users/{id} or... one of the many options)
    # Also implement auth so you can't join/leave chats for someone else etc.
    # But for now we just look at the form variable provided to decide what we need to do.
    chat_id = request.form.get('chatid')
    membership_id = request.form.get('membershipid')
    if chat_id is not None:
        # join an existing chat
        user = logic.get_user(session['user_id'])
        logic.join_chat(user, chat_id)
    elif membership_id is not None:
        # leave an existing chat
        logic.leave_chat(membership_id)
    else:
        # we're creating a new chat
        name = request.form['chatname']
        logic.create_chat(name)
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
