from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
pymysql.install_as_MySQLdb()  

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Railway MySQL Configuration
app.config['MYSQL_HOST'] = 'mysql.railway.internal'  # Replace with Railway MySQL host
app.config['MYSQL_USER'] = 'root'           # Replace with Railway MySQL username
app.config['MYSQL_PASSWORD'] = 'gWglUMkwryIYoNnFyaFzKdPVXoAUDenH'       # Replace with Railway MySQL password
app.config['MYSQL_DB'] = 'railway'             # Replace with Railway MySQL database name
app.config['MYSQL_PORT'] = 3306                     # Replace with Railway MySQL port if different

# Connect to the database
mysql = MySQLdb.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    port=app.config['MYSQL_PORT']
)

@app.route('/')
def index():
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    cursor.close()
    return render_template('index.html', users=data)

@app.route('/add', methods=['POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cursor = mysql.cursor()
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        cursor.execute(query, (name, email))
        mysql.commit()
        cursor.close()
        flash("User Added Successfully")
        return redirect(url_for('index'))

@app.route('/update/<id>', methods=['POST', 'GET'])
def update_user(id):
    cursor = mysql.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        query = "UPDATE users SET name = %s, email = %s WHERE id = %s"
        cursor.execute(query, (name, email, id))
        mysql.commit()
        cursor.close()
        flash("User Updated Successfully")
        return redirect(url_for('index'))
    else:
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        data = cursor.fetchone()
        cursor.close()
        return render_template('update.html', user=data)

@app.route('/delete/<id>', methods=['POST'])
def delete_user(id):
    cursor = mysql.cursor()
    query = "DELETE FROM users WHERE id = %s"
    cursor.execute(query, (id,))
    mysql.commit()
    cursor.close()
    flash("User Deleted Successfully")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
