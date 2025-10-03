from flask import Flask, render_template, redirect
import sqlite3

app = Flask(__name__)

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('ponystore.db')  # Aquí se usa el nombre correcto
    conn.row_factory = sqlite3.Row
    return conn

# Página principal
@app.route('/')
def index():
    conn = get_db_connection()
    ropa = conn.execute('SELECT * FROM ropa').fetchall()
    comida = conn.execute('SELECT * FROM comida').fetchall()
    conn.close()
    return render_template('index.html', ropa=ropa, comida=comida)

# Borrar ropa
@app.route('/delete/ropa/<int:id>')
def delete_ropa(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM ropa WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# Borrar comida
@app.route('/delete/comida/<int:id>')
def delete_comida(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM comida WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')