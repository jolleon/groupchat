from flask import Flask, request, redirect, render_template, session
from twilio.twiml.messaging_response import MessagingResponse

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
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html', username=session["username"], userphone=session['userphone'])



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['userphone'] = request.form['userphone']
        return redirect('/')
    return '''
        <form method="post">
            <p><input type=text name=username placeholder=username>
            <p><input type=text name=userphone placeholder="+14151234567">
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('userphone', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
