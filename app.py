from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bikes")
    bikes = cur.fetchall()
    return render_template('home.html', bikes=bikes, username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Username already exists.')
        
    return render_template('register.html')

@app.route('/bike/<int:bike_id>')
def bike_detail(bike_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bikes WHERE id = %s", (bike_id,))
    bike = cur.fetchone()
    return render_template('bike_detail.html', bike=bike, username=session.get('username'))

@app.route('/custom_bikes')
def custom_bikes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM custom_bikes")
    custom_bikes = cur.fetchall()
    return render_template('custom_bikes.html', custom_bikes=custom_bikes, username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)
