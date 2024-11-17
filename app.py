from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Duração dos serviços em minutos
SERVICOS = {
    "Corte de Cabelo": 40,
    "Barba": 30,
    "Sobrancelha": 10
}

def conectar_banco():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html', servicos=SERVICOS)

@app.route('/agenda', methods=['POST'])
def agenda():
    nome = request.form['nome']
    telefone = request.form['telefone']
    servico = request.form['servico']
    data = request.form['data']
    horario = request.form['horario']

    duracao = SERVICOS[servico]
    horario_inicio = datetime.strptime(f"{data} {horario}", "%Y-%m-%d %H:%M")
    horario_fim = horario_inicio + timedelta(minutes=duracao)

    conn = conectar_banco()
    cursor = conn.cursor()

    # Verificar se o horário está disponível
    cursor.execute("""
        SELECT * FROM agendamentos
        WHERE data = ? AND 
              ((horario_inicio BETWEEN ? AND ?) OR
               (horario_fim BETWEEN ? AND ?))
    """, (data, horario_inicio, horario_fim, horario_inicio, horario_fim))
    conflitos = cursor.fetchall()

    if conflitos:
        return "Horário indisponível. Escolha outro horário.", 400

    # Inserir agendamento
    cursor.execute("""
        INSERT INTO agendamentos (nome, telefone, servico, data, horario_inicio, horario_fim)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, telefone, servico, data, horario_inicio, horario_fim))
    conn.commit()
    conn.close()

    return redirect(url_for('confirm', nome=nome, servico=servico, horario=horario))

@app.route('/confirm')
def confirm():
    nome = request.args.get('nome')
    servico = request.args.get('servico')
    horario = request.args.get('horario')
    return render_template('confirm.html', nome=nome, servico=servico, horario=horario)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

