from flask import Flask, render_template, request, redirect, flash, url_for

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

import mysql.connector

from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)

app.secret_key = 'harshithbhaskar'



# Database connection setup

def get_db_connection():

    try:

        return mysql.connector.connect(

            host='localhost',

            user='root',

            password='',

            port=4306,

            database='farmers'

        )

    except mysql.connector.Error as err:

        flash(f"Database connection error: {err}", "danger")

        return None



# User class

class User(UserMixin):

    def __init__(self, id, username, email, password):

        self.id = id

        self.username = username

        self.email = email

        self.password = password



# User loader for Flask-Login

login_manager = LoginManager(app)

login_manager.login_view = 'login'



@login_manager.user_loader

def load_user(user_id):

    conn = get_db_connection()

    if conn:

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))

        user = cursor.fetchone()

        cursor.close()

        conn.close()

        return User(user['id'], user['username'], user['email'], user['password']) if user else None

    return None



# Home route

@app.route('/')

def index():

    return render_template('index.html')



# Farmer details route

@app.route('/farmerdetails')

@login_required

def farmerdetails():

    conn = get_db_connection()

    if conn:

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM register")

        query = cursor.fetchall()

        cursor.close()

        conn.close()

        return render_template('farmerdetails.html', query=query)

    return redirect(url_for('index'))



# Agro products route

@app.route('/agroproducts')

def agroproducts():

    conn = get_db_connection()

    if conn:

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM addagroproducts")

        query = cursor.fetchall()

        cursor.close()

        conn.close()

        return render_template('agroproducts.html', query=query)

    return redirect(url_for('index'))



# Add agro product route

@app.route('/addagroproduct', methods=['POST', 'GET'])

@login_required

def addagroproduct():

    if request.method == "POST":

        username = request.form.get('username')

        email = request.form.get('email')

        productname = request.form.get('productname')

        productdesc = request.form.get('productdesc')

        price = request.form.get('price')



        conn = get_db_connection()

        if conn:

            cursor = conn.cursor()

            cursor.execute(

                "INSERT INTO addagroproducts (username, email, productname, productdesc, price) VALUES (%s, %s, %s, %s, %s)",

                (username, email, productname, productdesc, price)

            )

            conn.commit()

            cursor.close()

            conn.close()

            flash("Product Added", "info")

            return redirect('/agroproducts')

    return render_template('addagroproducts.html')



# Triggers route

@app.route('/triggers')

@login_required

def triggers():

    conn = get_db_connection()

    if conn:

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM trig")

        query = cursor.fetchall()

        cursor.close()

        conn.close()

        return render_template('triggers.html', query=query)

    return redirect(url_for('index'))



# Add farming route

@app.route('/addfarming', methods=['POST', 'GET'])

@login_required

def addfarming():

    if request.method == "POST":

        farmingtype = request.form.get('farming')



        conn = get_db_connection()

        if conn:

            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM farming WHERE farmingtype = %s", (farmingtype,))

            query = cursor.fetchone()



            if query:

                flash("Farming Type Already Exists", "warning")

            else:

                cursor.execute("INSERT INTO farming (farmingtype) VALUES (%s)", (farmingtype,))

                conn.commit()

                flash("Farming Added", "success")

            

            cursor.close()

            conn.close()

            return redirect('/addfarming')

    

    return render_template('farming.html')



# Delete route

@app.route("/delete/<int:rid>", methods=['POST', 'GET'])

@login_required

def delete(rid):

    conn = get_db_connection()

    if conn:

        cursor = conn.cursor()

        cursor.execute("DELETE FROM register WHERE rid = %s", (rid,))

        conn.commit()

        cursor.close()

        conn.close()

        flash("Slot Deleted Successfully", "warning")

    return redirect('/farmerdetails')



# Edit route

@app.route("/edit/<int:rid>", methods=['POST', 'GET'])

@login_required

def edit(rid):

    conn = get_db_connection()

    if conn:

        cursor = conn.cursor(dictionary=True)



        if request.method == "POST":

            farmername = request.form.get('farmername')

            adharnumber = request.form.get('adharnumber')

            age = request.form.get('age')

            gender = request.form.get('gender')

            phonenumber = request.form.get('phonenumber')

            address = request.form.get('address')

            farmingtype = request.form.get('farmingtype')



            cursor.execute(

                "UPDATE register SET farmername = %s, adharnumber = %s, age = %s, gender = %s, phonenumber = %s, address = %s, farming = %s WHERE rid = %s",

                (farmername, adharnumber, age, gender, phonenumber, address, farmingtype, rid)

            )

            conn.commit()

            flash("Slot is Updated", "success")

            cursor.close()

            conn.close()

            return redirect('/farmerdetails')



        cursor.execute("SELECT * FROM register WHERE rid = %s", (rid,))

        posts = cursor.fetchone()

        cursor.close()

        conn.close()



        farming = []  # Fetch the farming types if needed

        return render_template('edit.html', posts=posts, farming=farming)



    return redirect('/farmerdetails')



# Signup route

@app.route('/signup', methods=['POST', 'GET'])

def signup():

    if request.method == "POST":

        username = request.form.get('username')

        email = request.form.get('email')

        password = request.form.get('password')

        hashed_password = generate_password_hash(password)



        conn = get_db_connection()

        if conn:

            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))

            user = cursor.fetchone()



            if user:

                flash("Email Already Exists", "warning")

            else:

                cursor.execute(

                    "INSERT INTO user (username, email, password) VALUES (%s, %s, %s)",

                    (username, email, hashed_password)

                )

                conn.commit()

                flash("Signup Success, Please Login", "success")

                return redirect(url_for('login'))

            cursor.close()

            conn.close()

    

    return render_template('signup.html')



# Login route

@app.route('/login', methods=['POST', 'GET'])

def login():

    if request.method == "POST":

        email = request.form.get('email')

        password = request.form.get('password')



        conn = get_db_connection()

        if conn:

            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))

            user = cursor.fetchone()



            if user and check_password_hash(user['password'], password):

                user_obj = User(user['id'], user['username'], user['email'], user['password'])


                login_user(user_obj)

                flash("Login Success", "primary")

                return redirect(url_for('index'))

            else:

                flash("Invalid credentials", "warning")

            cursor.close()

            conn.close()



    return render_template('login.html')



# Logout route

@app.route('/logout')

@login_required

def logout():

    logout_user()

    flash("Logout Successful", "warning")

    return redirect(url_for('login'))



# Register route

@app.route('/register', methods=['POST', 'GET'])

@login_required

def register():

    if request.method == "POST":

        farmername = request.form.get('farmername')

        adharnumber = request.form.get('adharnumber')

        age = request.form.get('age')

        gender = request.form.get('gender')

        phonenumber = request.form.get('phonenumber')

        address = request.form.get('address')

        farmingtype = request.form.get('farmingtype')



        conn = get_db_connection()

        if conn:

            cursor = conn.cursor()

            cursor.execute(

                "INSERT INTO register (farmername, adharnumber, age, gender, phonenumber, address, farming) VALUES (%s, %s, %s, %s, %s, %s, %s)",

                (farmername, adharnumber, age, gender, phonenumber, address, farmingtype)

            )

            conn.commit()

            cursor.close()

            conn.close()

            return redirect('/farmerdetails')



    # Fetch farming types

    conn = get_db_connection()

    if conn:

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT farmingtype FROM farming")

        farming = cursor.fetchall()

        cursor.close()

        conn.close()



    return render_template('farmer.html', farming=farming)





# Test connection route

@app.route('/test')

def test():

    conn = get_db_connection()

    if conn:

        conn.close()

        return 'My database is Connected'

    return 'My db is not Connected'



if __name__ == '__main__':

    app.run(debug=True)