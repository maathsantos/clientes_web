from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import csv
import io

app = Flask(__name__)
DB_NAME = 'clientes.db'

# Função para criar a tabela se não existir
def criar_tabela():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cidade TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Chama para garantir que a tabela exista ao iniciar o app
criar_tabela()

# Página principal: lista e busca
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    busca = request.args.get('busca', '').strip()

    if busca:
        c.execute("SELECT * FROM clientes WHERE nome LIKE ? OR email LIKE ? OR telefone LIKE ? OR cidade LIKE ?", 
                  ('%'+busca+'%', '%'+busca+'%', '%'+busca+'%', '%'+busca+'%'))
    else:
        c.execute("SELECT * FROM clientes")

    clientes = c.fetchall()
    conn.close()
    return render_template('index.html', clientes=clientes, busca=busca)

# Adicionar novo cliente
@app.route('/add', methods=['POST'])
def add():
    nome = request.form['nome'].strip()
    email = request.form['email'].strip()
    telefone = request.form['telefone'].strip()
    cidade = request.form['cidade'].strip()

    # Validação simples
    if not nome or not email or not telefone or not cidade:
        return "Todos os campos são obrigatórios!", 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO clientes (nome, email, telefone, cidade) VALUES (?, ?, ?, ?)",
              (nome, email, telefone, cidade))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Página para editar cliente
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        telefone = request.form['telefone'].strip()
        cidade = request.form['cidade'].strip()

        if not nome or not email or not telefone or not cidade:
            return "Todos os campos são obrigatórios!", 400

        c.execute("UPDATE clientes SET nome=?, email=?, telefone=?, cidade=? WHERE id=?",
                  (nome, email, telefone, cidade, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    else:
        c.execute("SELECT * FROM clientes WHERE id=?", (id,))
        cliente = c.fetchone()
        conn.close()
        if cliente:
            return render_template('edit.html', cliente=cliente)
        else:
            return "Cliente não encontrado", 404

# Excluir cliente
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM clientes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Exportar clientes para CSV
@app.route('/export')
def export():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT nome, email, telefone, cidade FROM clientes")
    clientes = c.fetchall()
    conn.close()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Nome', 'Email', 'Telefone', 'Cidade'])
    cw.writerows(clientes)

    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)

    return send_file(output, mimetype='text/csv', download_name='clientes.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
