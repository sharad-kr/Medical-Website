from flask import Flask, jsonify, render_template, flash, request, session
import mysql.connector
import json
from flask import request
import hashlib
from googletrans import Translator


app = Flask(__name__)
app.secret_key = 'btech'


class user_model():
    def __init__(self):

        self.con = mysql.connector.connect(
            host='localhost', user='root', password='sharad_KUMAR2021', database='medical')
        self.con.autocommit = True
        self.cur = self.con.cursor(dictionary=True)
        self.cur1 = self.con.cursor()
        self.cur2 = self.con.cursor(dictionary=True)
        self.cur3 = self.con.cursor()
        self.cur4 = self.con.cursor()

    def user_get_all(self):
        self.cur.execute("SELECT * FROM user")
        result = self.cur.fetchall()
        return jsonify(result)

    def user_sign_up(self, data):
        self.cur1.execute("SELECT user_name from user")
        user_list = self.cur1.fetchall()
        user_list = jsonify(user_list).get_json()
        user_list = [row[0] for row in user_list]
        if (data['user_name'] in user_list):
            return render_template("sign-up.html", Error="User Name not available ! ")
        elif (data['password'] != data['confirm_password']):
            return render_template("sign-up.html", Error="Passwords did not match ! ")
        else:
            session['user_name'] = f"{data['user_name']}"
            self.cur.execute(
                f"INSERT INTO user(name,mob_number,email,dob,sex,address,user_name,password) VALUES('{data['name']}','{data['mob_number']}','{data['email']}','{data['dob']}','{data['sex']}','Null','{data['user_name']}','{hashlib.sha256(data['password'].encode('utf-8')).hexdigest()}')")
            return render_template('profile-page.html', user_name=data['user_name'], name=data['name'], email=data['email'], mob_number=data['mob_number'], sex=data['sex'], dob=data['dob'],table = None)

    def user_log_in(self, data):
        id = data['user_name']
        psd = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
        self.cur1.execute("SELECT user_name FROM user")
        result = self.cur1.fetchall()

        column_list = [row[0] for row in result]

        if not(id in column_list):
            return render_template('./login-page.html', Error="Incorrect username")
        else:
            self.cur2.execute(f"SELECT * FROM user WHERE user_name = '{id}'")
            result1 = jsonify(self.cur2.fetchall()).get_json()
            if result1[0]['password'] != psd:
                return render_template("./login-page.html", Error="You Entered the Wrong Password,Please Enter the Correct Psssword")
            else:
                info = result1[0]
                session['user_name'] = info['user_name']
                return render_template('profile-page.html', user_name=info['user_name'], name=info['name'], email=info['email'], mob_number=info['mob_number'], sex=info['sex'], dob=info['dob'],table = None)

    def logout(self):
        session['user_name'] = None
        return render_template('login-page.html')

    # data here is a name of medicine of type string.
    def med_detail(self, data):
        if session['user_name'] != None:
            med = data['medicine-name'].lower()
            self.cur.execute(
                "SELECT * from drugs WHERE LOWER(drug_name) LIKE '%"+(med)+"%'")
            result = jsonify(self.cur.fetchall()).get_json()
            return render_template('med-detail.html', data=result)
        else:
            return render_template('./login-page.html', Error="Please Sign in to order medicine")

    # data here is the name of doctor of type string.

    def find_doctors(self, data):
        if session['user_name'] != None:
            self.cur.execute(
                f"SELECT * FROM doclist WHERE speciality = '{data}'")
            result = jsonify(self.cur.fetchall()).get_json()
            return result
        else:
            return render_template('./login-page.html', Error="Please Sign in to book appointment")

    def book_appointment(self, data):
        translator = Translator()
        # return data['symptom']
        if len(data['symptom']) != 0:
            translation = translator.translate(
                data['symptom'], src=translator.detect(data['symptom']).lang, dest='en')
            translation = translation.text
        else:
            translation = data['symptom']
            
        self.cur1.execute(f"SELECT Doctor_Name FROM doclist WHERE Doctor_ID = '{data['Doctor_ID']}'")
        doc_name = self.cur1.fetchall()
        doc_name = doc_name[0][0]
        # return doc_name
        self.cur.execute(
            f"INSERT INTO appointment(Doctor_Name,user_name,appointment_date,Doctor_ID,symptom) VALUES('{doc_name}','{session['user_name']}','{data['appointment_date']}','{data['Doctor_ID']}','{translation.text}')")
        self.cur1.execute("SELECT Doctor_ID FROM Doctor_duty")
        result = self.cur1.fetchall()
        column_list = [row[0] for row in result]
        if (int(f"{data['Doctor_ID']}") in column_list):
            self.cur.execute(
                f"UPDATE Doctor_duty SET doc_load = doc_load + 1 WHERE Doctor_ID = '{data['Doctor_ID']}' ")
        else:
            self.cur.execute(
                f"INSERT INTO Doctor_duty (Doctor_ID, doc_load) VALUES ('{data['Doctor_ID']}', '1') ")
        return render_template('select-speciality.html',result="Appointment booked successfully !")

    def get_user(self, data):
        if data == None:
            return render_template('login-page.html')
        else:
            self.cur.execute(f"SELECT * FROM user WHERE user_name = '{data}'")
            result1 = jsonify(self.cur.fetchall()).get_json()
            # if result1[0]['password'] != psd:
            # return render_template("./login-page.html", Error="You Entered the Wrong Password,Please Enter the Correct Psssword")
            # return result1
            info = result1[0]
            # return info
            return render_template('profile-page.html', user_name=info['user_name'], name=info['name'], email=info['email'], mob_number=info['mob_number'], sex=info['sex'], dob=info['dob'],table = None)

    def order_medicine(self, data):
        # self.cur4.execute("SELECT drug_name FROM drugs")
        # drug_list = self.cur4.fetchall()
        # drug_list = jsonify(drug_list).get_json()
        # drug_list = [row[0] for row in drug_list]
        # if not(drug_name in drug_list):
        #     return "Sorry ,This medicine is not available"
        # else:
        self.cur1.execute(
            f"SELECT quantity FROM drugs WHERE drug_id = '{data['drug_id']}'")
        drug_quantity = self.cur1.fetchall()
        drug_quantity = jsonify(drug_quantity).get_json()
        # return drug_quantity
        if int(drug_quantity[0][0]) < int(data['quantity']):
            # return jsonify({"message": "Sorry, the quantity of medicine demanded is not available"})
            return render_template('med-shop.html',result="Sorry, the quantity of medicine demanded is not available.")
        else:
            self.cur3.execute(
                "SELECT DATE(DATE_ADD(NOW(), INTERVAL 5 DAY)) as date")
            date = self.cur3.fetchall()
            column_list = [row[0] for row in date]
            self.cur4.execute(
                f"SELECT drug_name FROM drugs WHERE drug_id = {data['drug_id']}")
            drug_name = self.cur4.fetchall()
            drug_name = drug_name[0][0]
            self.cur.execute(
                f"INSERT INTO orders(drug_name,address,user_name,shipment_date,order_quantity) VALUES('{drug_name}','{data['address']}','{session['user_name']}','{column_list[0]}','{data['quantity']}')")
            self.cur2.execute(
                f"UPDATE drugs SET quantity = quantity - {data['quantity']}  WHERE drug_id = '{data['drug_id']}'")
            # return jsonify({"message": "Order placed successfully"})
            return render_template('med-shop.html',result="Order placed Succesfully!")

    def get_opd(self, data):
        self.cur.execute(
            f"SELECT * FROM appointment WHERE Doctor_ID = '{data['Doctor_ID']}'")
        result = jsonify(self.cur.fetchall()).get_json()
        return result

    def get_appointment(self, data):
        if data != None:
            self.cur.execute(
                f"SELECT * FROM appointment WHERE user_name = '{data}'")
            result = jsonify(self.cur.fetchall()).get_json()

            self.cur.execute(f"SELECT * FROM user WHERE user_name = '{data}'")
            result1 = jsonify(self.cur.fetchall()).get_json()
            info = result1[0]
            return render_template('profile-page.html', user_name=info['user_name'], name=info['name'], email=info['email'], mob_number=info['mob_number'], sex=info['sex'], dob=info['dob'], data=result, controller=None,table = 'Not None')
        else:
            return render_template('login-page.html',Error = 'PLease Sign in to view your appointmnets')
    def my_order(self, data):
        if data != None:
            self.cur.execute(
                f"SELECT * FROM orders WHERE user_name = '{data}'")
            result = jsonify(self.cur.fetchall()).get_json()
            # return render_template('profile-page.html', data=result, controller='Not None')
            self.cur.execute(f"SELECT * FROM user WHERE user_name = '{data}'")
            result1 = jsonify(self.cur.fetchall()).get_json()
            info = result1[0]
            return render_template('profile-page.html', user_name=info['user_name'], name=info['name'], email=info['email'], mob_number=info['mob_number'], sex=info['sex'], dob=info['dob'], data=result, controller='Not None',table = 'Not None')
        else:
            return render_template('login-page.html',Error = 'PLease Sign in to view your orders')
    def update_opd(self, data):
        self.cur1.execute(
            f"SELECT Doctor_ID from appointment WHERE appointment_id = '{data['appointment_id']}'")
        result = self.cur1.fetchall()
        column_list = [row[0] for row in result]
        doctor = column_list[0]
        if int(doctor) != data['Doctor_ID']:
            return "This patient is not alloted to you ! "
        else:
            self.cur.execute(
                f"DELETE FROM appointment WHERE appointment_id = '{data['appointment_id']}'")
            self.cur.execute(
                f"UPDATE Doctor_duty SET doc_load = doc_load - 1 WHERE Doctor_ID = '{data['Doctor_ID']}' ")
            return "Appointment list updated successfully ! "


    def update_status(self, data):
        self.cur.execute(
            f"UPDATE orders SET status = 'Shipped' WHERE order_id = '{data}';")
        return "Order Status updated successfully"


    def get_doctors(self, data):
        if session['user_name'] != None:
            self.cur.execute(
                f"SELECT * FROM doclist WHERE speciality = '{data['speciality']}'")
            result = jsonify(self.cur.fetchall()).get_json()
            return render_template('doctors.html', data=result)
        else:
            return render_template('./login-page.html', Error="Please Sign in to book appointment")


obj = user_model()


@app.route("/")
def default_home():
    session['user_name'] = None
    return render_template('index.html')


@app.route('/home-page')
def home_page():
    return render_template('index.html')


@app.route("/user/get-all", methods=['GET'])
def user_get_all():
    return obj.user_get_all()


@app.route("/get-user", methods=['GET'])
def get_user():
    return obj.get_user(session['user_name'])


@app.route("/user/sign-up", methods=['POST', 'GET'])
def user_sign_up():
    if request.method == 'POST':
        userDetails = request.form
        data = {'name': userDetails['Full Name'], 'mob_number': userDetails['Enter Mobile Number'], 'email': userDetails['Enter a Valid Email'], 'user_name': userDetails['Create Username'],
                'password': userDetails['Create Password'], 'confirm_password': userDetails['Confirm Password'], 'dob': userDetails['Date of Birth'], 'sex': userDetails['Select Gender']}
        return obj.user_sign_up(data)
    return render_template('sign-up.html')


@app.route("/user/log-in", methods=['POST', 'GET'])
def user_log_in():
    if request.method == 'POST':
        userDetails = request.form
        data = {'user_name': userDetails['Name'],
                'password': userDetails['Password']}
        return obj.user_log_in(data)
    return render_template('login-page.html')


@app.route("/user/log-out", methods=['POST', 'GET'])
def user_log_out():
    return obj.logout()


@app.route("/getme")
def getme():
    return session['user_name']


@app.route("/med-detail", methods=['POST', 'GET'])
def med_detail():
    if request.method == 'POST':
        drug = request.form
        # return drug
        data = {'medicine-name': drug['medicine-name']}
        return obj.med_detail(data)
    return render_template('med-shop.html')


@app.route("/find-doctors", methods=['POST', 'GET'])
def find_doctors():
    return obj.find_doctors(request.form)


@app.route("/select-speciality", methods=['POST', 'GET'])
def get_doctors():
    if request.method == 'POST':
        return obj.get_doctors(request.form)
    return render_template('select-speciality.html')


@app.route("/book-an-appointment", methods=['POST', 'GET'])
def book_an_appointment():
    # userDetails = request.form
    if request.method == 'POST':
        return obj.book_appointment(request.form)
    # return "yes"
    return render_template('doctors.html')


@app.route("/order", methods=['POST', 'GET'])
def order_medicine():
    return obj.order_medicine(request.form)


@app.route("/doctor/get-opd", methods=['POST', 'GET'])
def get_opd():
    return obj.get_opd(request.form)

# the following api removes the appointment from appointment table when a doctor sees the patient.


@app.route("/doctor/update-opd", methods=['POST'])
def update_opd():
    return obj.update_opd(request.form)


@app.route("/shipped/<int:order_id>", methods=['POST'])
def update_status(order_id):
    return obj.update_status(order_id)


@app.route("/home-page")
def home():
    return render_template("home-page.html")


@app.route("/my-appointment", methods=['GET'])
def get_appointment():
    return obj.get_appointment(session['user_name'])


@app.route("/my-order", methods=['GET'])
def my_order():
    return obj.my_order(session['user_name'])
# @app.route("/med-shop")
# def order():
#     return render_template('med-shop.html')


@app.route("/contact-us")
def contact():
    return render_template('contact-us.html')


@app.route("/about-us")
def about():
    return render_template('about-us.html')


# @app.route("/profile-page", methods=['GET'])
# def profile():
#     return obj.get_user(session['user_name'])


if __name__ == '__main__':
    app.run(debug=True)
