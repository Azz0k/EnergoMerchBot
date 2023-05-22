from imports.Users_mssql import Users
from flask import request
from flask import Flask
from flask import jsonify

app = Flask(__name__)

users = Users()


@app.route('/')
def hello_world():
    return '<p>Hello, World!</p>'


@app.get('/api/user/<phone_number>')
def get_user_id(phone_number: str):
    result = users.get_telegram_id_by_phone_number(phone_number)
    return jsonify({'id': result})


@app.post('/api/user/<phone_number>')
def create_user_and_add_link(phone_number: str):
    link = request.form['link']
    if users.is_phone_number_exists(phone_number):
        users.update_link(phone_number, link)
    else:
        users.insert_number_and_link(phone_number, link)
    return ''


if __name__ == '__main__':
    app.run()
