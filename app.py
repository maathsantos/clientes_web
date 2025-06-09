from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import csv
import re
import io

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    cidade TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def email_valido(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        cidade = request.form["cidade"]

        if nome and email_valido(email) and telefone and cidade:
            c.execute("INSERT INTO clientes (nome, email, telefone, cidade) VALUES (?, ?, ?, ?)",
                      (nome, email, telefone, cidade))
            conn.commit()

    search = request.args.get("search", "")
    if search:
        c.execute("SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ? OR cidade LIKE ?",
                  (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        c.execute("SELECT * FROM clientes")

    clientes = c.fetchall()
    conn.close()
    return render_template("index.html", clientes=clientes, search=search)

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("DELETE FROM clientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        cidade = request.form["cidade"]

        if nome and email_valido(email) and telefone and cidade:
            c.execute("UPDATE clientes SET nome=?, email=?, telefone=?, cidade=? WHERE id=?",
                      (nome, email, telefone, cidade, id))
            conn.commit()
            conn.close()
            return redirect("/")

    c.execute("SELECT * FROM clientes WHERE id=?", (id,))
    cliente = c.fetchone()
    conn.close()
    return render_template("edit.html", cliente=cliente)

@app.route("/export")
def export():
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute("SELECT nome, email, telefone, cidade FROM clientes")
    dados = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Email", "Telefone", "Cidade"])
    writer.writerows(dados)
    output.seek(0)

    return send_file(io.BytesIO(output.read().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name="clientes.csv")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
