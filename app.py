from flask import Flask, render_template, redirect, request
import sqlite3
import time
from configs import ADMIN_CODE
from random import randint
from datetime import datetime
from classic_caesar import cipher

app = Flask(__name__)
RAN_NUM = 8

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def detected():
	db = sqlite3.connect("data.db")
	sql = db.cursor()

	sql.execute("""CREATE TABLE IF NOT EXISTS users(
		name TEXT,
		first_name TEXT,
		code TEXT,
		true_code TEXT
	)""")
	db.commit()


	sql.close()
	db.close()
	return redirect('/login')

@app.route('/home', methods=["POST", "GET"])
def not_login():
	return redirect("/login")


@app.route('/home/<string:encusername>/<string:encfirstname>/<string:encodik>', methods=["POST", "GET"])
def index(encusername, encfirstname, encodik):
	symb = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"

	db = sqlite3.connect("data.db")
	sql = db.cursor()

	sql.execute(f"SELECT * FROM users WHERE name='{encusername}'")
	data = sql.fetchone()
	
	if data is None:
		return redirect("/login")
	else:
		if (data[1] == encfirstname):
			if (data[2] == encodik):
				pass
			else:
				return redirect("/login")
		else:
			return redirect("/login")

	username = cipher.getTranslatedMessage(symb, encusername, RAN_NUM, True)
	firstname = cipher.getTranslatedMessage(symb, encfirstname, RAN_NUM, True)
	codik = cipher.getTranslatedMessage("1234567890", encodik, 5, True)


	sql.execute("""CREATE TABLE IF NOT EXISTS msg_list(
		id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		author TEXT,
		sendTime TIME,
		content TEXT
		)""")
	db.commit()

	msgs = sql.execute("SELECT * FROM msg_list").fetchall()


	if request.method == "POST":
		author = f"{username} {firstname}"
		now_time = datetime.now()
		sendTime = f"{now_time.hour}:{now_time.minute}"
		content = request.form["message"]
		
		sql.execute("INSERT INTO msg_list(author, sendTime, content) VALUES (?,?,?)", (author, sendTime, content))
		db.commit()

		return redirect(f"/home/{encusername}/{encfirstname}/{encodik}")

	msg_list = []

	for i in msgs:
		formatik = f"| {i[1]} | {i[3]} | Отправлено: {i[2]} |"
		msg_list.append(formatik)

	return render_template("index.html", msg_list=msg_list)


@app.route('/login', methods=["POST", "GET"])
def login():
	symb = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"

	db = sqlite3.connect("data.db")
	sql = db.cursor()

	sql.execute("""CREATE TABLE IF NOT EXISTS users(
		name TEXT,
		first_name TEXT,
		code TEXT,
		true_code TEXT
		)""")

	db.commit()
	if request.method == "POST":

		code = request.form["code"]
		encode_name = cipher.getTranslatedMessage(symb, request.form["username"], RAN_NUM, False)
		encode_first_name = cipher.getTranslatedMessage(symb, request.form["first_name"], RAN_NUM, False)
		encode_code = cipher.getTranslatedMessage("1234567890", request.form["code"], 5, False)

		sql.execute("SELECT * FROM users")
		data = sql.fetchall()
		
		for i in data:
			if i[0] == encode_name:
				if i[1] == encode_first_name:
					if i[2] == encode_code:
						return redirect(f"/home/{encode_name}/{encode_first_name}/{encode_code}")



		sql.close()
		db.close()
		return redirect("/login")
	else:
		return render_template("login.html")


@app.route("/reg", methods=["POST", "GET"])
def reg_new_user():
	symb = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
	if request.method == "POST":
		cod = request.form["admin-code"]

		if cod == ADMIN_CODE:
			encode_name = cipher.getTranslatedMessage(symb, request.form['new_name'], RAN_NUM, False)
			encode_first_name = cipher.getTranslatedMessage(symb, request.form['new_first_name'], RAN_NUM, False)
			future_code = randint(100000, 300000)
			encode_code = cipher.getTranslatedMessage("1234567890", f"{future_code}", 5, False)
			db = sqlite3.connect("data.db")
			sql = db.cursor()

			sql.execute("SELECT * FROM users")
			data = sql.fetchall()

			if encode_name == "" or encode_first_name == "":
				return redirect("/reg")
			else:
				for i in data:
					if i[0] == encode_name:
						return redirect("/reg")
					else:
						if i[1] == encode_first_name:
							return redirect("/reg")
						else:
							sql.execute("INSERT INTO users(name, first_name, code, true_code) VALUES (?,?,?,?)", (encode_name, encode_first_name, encode_code, f"{future_code}"))
							db.commit()
							return redirect("/login")
				
				if data == []:
					sql.execute("INSERT INTO users(name, first_name, code, true_code) VALUES (?,?,?,?)", (encode_name, encode_first_name, encode_code, f"{future_code}"))
					db.commit()
					return redirect("/login")

			sql.close()
			db.close()
		else:
			return redirect("/reg")
	else:
		return render_template("reg_page.html")


if __name__ == "__main__":
	app.run(debug=True, use_reloader=True)