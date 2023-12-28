from flask import (Flask, render_template, request, redirect, url_for)
import sqlite3
import xlsxwriter
import pdfkit

app = Flask(__name__)


@app.route('/')
def index():
    conn = sqlite3.connect('basesita.db')
    cursor = conn.cursor()

    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    cursor.execute('SELECT * FROM usuarios LIMIT ? OFFSET ?', (per_page, offset))
    usuarios = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM usuarios')
    total_users = cursor.fetchone()[0]

    conn.close()

    return render_template('index.html', usuarios=usuarios, total_users=total_users, per_page=per_page)


@app.route('/agregar', methods=['POST'])
def agregar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']

        conn = sqlite3.connect('basesita.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (nombre, email) VALUES (?, ?)', (nombre, email))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))


@app.route('/editar/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    conn = sqlite3.connect('basesita.db')
    cursor = conn.cursor()
    usuario = cursor.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        cursor.execute('UPDATE usuarios SET nombre = ?, email = ? WHERE id = ?', (nombre, email, usuario_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('editar.html', usuario=usuario)


@app.route('/eliminar/<int:usuario_id>', methods=['GET', 'POST'])
def eliminar_usuario(usuario_id):
    conn = sqlite3.connect('basesita.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/exportar_excel', methods=['GET'])
def exportar_excel():
    conn = sqlite3.connect('basesita.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()

    workbook = xlsxwriter.Workbook('C:/Users/USER/desktop/usuarios.xlsx')
    worksheet = workbook.add_worksheet()

    headers = ['ID', 'Nombre', 'Email']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row, usuario in enumerate(usuarios, start=1):
        for col, data in enumerate(usuario):
            worksheet.write(row, col, data)

    workbook.close()
    return redirect(url_for('index'))


config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')


@app.route('/exportar_pdf', methods=['GET'])
def exportar_pdf():
    conn = sqlite3.connect('basesita.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()

    html_content = '<html><head><title>Usuarios</title></head><body><table border="1">'
    html_content += '<tr><th>ID</th><th>Nombre</th><th>Email</th></tr>'
    for usuario in usuarios:
        html_content += '<tr>'
        for data in usuario:
            html_content += f'<td>{data}</td>'
        html_content += '</tr>'
    html_content += '</table></body></html>'

    pdfkit.from_string(html_content, 'C:/Users/USER/desktop/usuarios.pdf', configuration=config)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
