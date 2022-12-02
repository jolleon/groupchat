from flask import Flask, request, redirect, render_template, session
from twilio.twiml.messaging_response import MessagingResponse


import db


app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO env or generate


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message("The Robots are coming! Head for the hills!")

    return str(resp)


@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect('/login')
    user = db.get_user(session["user_id"])
    if user is None:
        # something weird - user got deleted? make them login again
        return redirect('/logout')
    all_chats = db.get_all_chats()
    my_chats = db.get_user_chats(user.id)
    return render_template('index.html', user=user, all_chats=all_chats, my_chats=my_chats)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        phone = request.form['userphone']
        user = db.login_or_create_user(name, phone)
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
    chat_id = request.form.get('chatid')
    membership_id = request.form.get('membershipid')
    if chat_id is not None:
        db.join_chat(session['user_id'], chat_id)
    elif membership_id is not None:
        db.leave_chat(membership_id)
    else:
        # we're creating a new chat
        name = request.form['chatname']
        db.create_chat(name)
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
