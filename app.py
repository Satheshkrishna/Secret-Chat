from flask import Flask, render_template, request, redirect, url_for, session, flash
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'your_secret_key'

chat_rooms = {}

def generate_key():
    return Fernet.generate_key()

def get_cipher(key):
    return Fernet(key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join_chat', methods=['POST'])
def join_chat():
    username = request.form.get('username')
    pin = request.form.get('pin')

    if not username or not pin:
        flash('Username and PIN are required!')
        return redirect(url_for('index'))

    if pin not in chat_rooms:
        chat_rooms[pin] = []

    session['username'] = username
    session['pin'] = pin
    session['key'] = generate_key().decode()  
    return redirect(url_for('chat'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    username = session.get('username')
    pin = session.get('pin')
    key = session.get('key')

    if not username or not pin or pin not in chat_rooms:
        flash('Invalid session or chat room!')
        return redirect(url_for('index'))

    cipher = get_cipher(key.encode())

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            encrypted_message = cipher.encrypt(message.encode()).decode()
            chat_rooms[pin].append({'from': username, 'message': encrypted_message})

    decrypted_messages = [
        {'from': msg['from'], 'message': cipher.decrypt(msg['message'].encode()).decode()}
        for msg in chat_rooms[pin]
    ]

    return render_template('chat.html', username=username, chat_messages=decrypted_messages)

@app.route('/delete_chat', methods=['POST'])
def delete_chat():
    pin = session.get('pin')

    if pin and pin in chat_rooms:
        del chat_rooms[pin]


    session.pop('username', None)
    session.pop('pin', None)
    session.pop('key', None)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
