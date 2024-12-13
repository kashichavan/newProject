from flask import Flask, render_template, request, redirect, url_for, flash, g
import pymysql

# Make pymysql work as MySQLdb (to avoid changes in the rest of the code)
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# Railway MySQL Configuration
app.config['MYSQL_HOST'] = 'mysql.railway.internal'  # Replace with Railway MySQL host
app.config['MYSQL_USER'] = 'root'           # Replace with Railway MySQL username
app.config['MYSQL_PASSWORD'] = 'gWglUMkwryIYoNnFyaFzKdPVXoAUDenH'       # Replace with Railway MySQL password
app.config['MYSQL_DB'] = 'railway'             # Replace with Railway MySQL database name
app.config['MYSQL_PORT'] = 3306                      # Replace with Railway MySQL port if different

def get_db():
    """Open a new database connection if one is not already open."""
    if 'db' not in g:
        try:
            g.db = pymysql.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                passwd=app.config['MYSQL_PASSWORD'],
                db=app.config['MYSQL_DB'],
                port=app.config['MYSQL_PORT'],
                cursorclass=pymysql.cursors.DictCursor  # Use dictionary cursor for easier data handling
            )
        except pymysql.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
            flash("Database connection failed", 'error')
            return redirect(url_for('index'))
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close the database connection after each request."""
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    cursor.close()
    return render_template('index.html', users=data)

@app.route('/add', methods=['POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        db = get_db()
        cursor = db.cursor()
        try:
            query = "INSERT INTO users (name, email) VALUES (%s, %s)"
            cursor.execute(query, (name, email))
            db.commit()
            flash("User Added Successfully")
        except pymysql.MySQLError as e:
            db.rollback()  # Rollback if any error occurs
            print(f"Error executing query: {e}")
            flash("Error adding user", 'error')
        finally:
            cursor.close()
        return redirect(url_for('index'))

@app.route('/update/<id>', methods=['POST', 'GET'])
def update_user(id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        try:
            query = "UPDATE users SET name = %s, email = %s WHERE id = %s"
            cursor.execute(query, (name, email, id))
            db.commit()
            flash("User Updated Successfully")
        except pymysql.MySQLError as e:
            db.rollback()
            print(f"Error executing query: {e}")
            flash("Error updating user", 'error')
        finally:
            cursor.close()
        return redirect(url_for('index'))
    else:
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        data = cursor.fetchone()
        cursor.close()
        return render_template('update.html', user=data)

@app.route('/delete/<id>', methods=['POST'])
def delete_user(id):
    db = get_db()
    cursor = db.cursor()
    try:
        query = "DELETE FROM users WHERE id = %s"
        cursor.execute(query, (id,))
        db.commit()
        flash("User Deleted Successfully")
    except pymysql.MySQLError as e:
        db.rollback()
        print(f"Error executing query: {e}")
        flash("Error deleting user", 'error')
    finally:
        cursor.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
