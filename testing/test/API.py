from flask import Flask, jsonify, render_template, flash, request, session
import mysql.connector
import json
from flask import request
import hashlib
from googletrans import Translator
import coverage


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



    def user_sign_up(self, data):
        self.cur1.execute("SELECT user_name from user")
        user_list = self.cur1.fetchall()
        user_list = jsonify(user_list).get_json()
        user_list = [row[0] for row in user_list]
        if (data['user_name'] in user_list):
            return "User name not available"
            # return render_template("sign-up.html", Error="User Name not available ! ")
        elif (data['password'] != data['confirm_password']):
            return "Password Mismatch !"
            # return render_template("sign-up.html", Error="Passwords did not match ! ")
        else:
            session['user_name'] = f"{data['user_name']}"
            self.cur.execute(
                f"INSERT INTO user(name,mob_number,email,dob,sex,address,user_name,password) VALUES('{data['name']}','{data['mob_number']}','{data['email']}','{data['dob']}','{data['sex']}','Null','{data['user_name']}','{hashlib.sha256(data['password'].encode('utf-8')).hexdigest()}')")
            return "Sign-up Successful"
            # return render_template('profile-page.html', user_name=data['user_name'], name=data['name'], email=data['email'], mob_number=data['mob_number'], sex=data['sex'], dob=data['dob'],table = None)

    def user_log_in(self, data):
        id = data['user_name']
        psd = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
        self.cur1.execute("SELECT user_name FROM user")
        result = self.cur1.fetchall()

        column_list = [row[0] for row in result]

        if not(id in column_list):
            return "id not found"
            # return render_template('./login-page.html', Error="Incorrect username")
        else:
            self.cur2.execute(f"SELECT * FROM user WHERE user_name = '{id}'")
            result1 = jsonify(self.cur2.fetchall()).get_json()
            if result1[0]['password'] != psd:
                return "wrong password"
                # return render_template("./login-page.html", Error="You Entered the Wrong Password,Please Enter the Correct Psssword")
            else:
                info = result1[0]
                session['user_name'] = info['user_name']
                return result1
                # return render_template('profile-page.html', user_name=info['user_name'], name=info['name'], email=info['email'], mob_number=info['mob_number'], sex=info['sex'], dob=info['dob'],table = None)

    def logout(self):
        session['user_name'] = None
        return "Logged out Successfully"
        # return render_template('login-page.html')

    # data here is a name of medicine of type string.
    def med_detail(self, data):
        if session['user_name'] != None:
            med = data['medicine-name'].lower()
            self.cur.execute(
                "SELECT * from drugs WHERE LOWER(drug_name) LIKE '%"+(med)+"%'")
            result = jsonify(self.cur.fetchall()).get_json()
            return result
            # return render_template('med-detail.html', data=result)
        else:
            return "Please Sign In to book medicine"


    def book_appointment(self, data):
        translator = Translator()
        
        if len(data['symptom']) != 0:
            translation = translator.translate(
                data['symptom'], src=translator.detect(data['symptom']).lang, dest='en')
            
        self.cur1.execute(f"SELECT Doctor_Name FROM doclist WHERE Doctor_ID = '{data['Doctor_ID']}'")
        doc_name = self.cur1.fetchall()
        doc_name = doc_name[0][0]
        
        self.cur.execute(
            f"INSERT INTO appointment(Doctor_Name,user_name,appointment_date,Doctor_ID,symptom) VALUES('{doc_name}','{session['user_name']}','{data['appointment_date']}','{data['Doctor_ID']}','{translation.text}')")
    
        return "Appointment booked successfully !"
        

    def get_user(self, data):
        if data == None:
            return "Log In first !"
            # return render_template('login-page.html')
        else:
            self.cur.execute(f"SELECT * FROM user WHERE user_name = '{data}'")
            result1 = jsonify(self.cur.fetchall()).get_json()
            return result1
           
    def order_medicine(self, data):

        self.cur1.execute(
            f"SELECT quantity FROM drugs WHERE drug_id = '{data['drug_id']}'")
        drug_quantity = self.cur1.fetchall()
        drug_quantity = jsonify(drug_quantity).get_json()
       
        if int(drug_quantity[0][0]) < int(data['quantity']):
            return "Sorry the quantity demanded is not avaialble"

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
            return "Order Placed Successfully"

    def get_appointment(self, data):
        if data != None:
            self.cur.execute(
                f"SELECT * FROM appointment WHERE user_name = '{data}'")
            result = jsonify(self.cur.fetchall()).get_json()

            self.cur.execute(f"SELECT * FROM user WHERE user_name = '{data}'")
            result1 = jsonify(self.cur.fetchall()).get_json()
            return result1
        else:
            return "PLease Sign in to view your appointmnets"
            
    def my_order(self, data):
        if data != None:
            self.cur.execute(
                f"SELECT * FROM orders WHERE user_name = '{data}'")
            result = jsonify(self.cur.fetchall()).get_json()
            # return render_template('profile-page.html', data=result, controller='Not None')
            self.cur.execute(f"SELECT * FROM user WHERE user_name = '{data}'")
            result1 = jsonify(self.cur.fetchall()).get_json()
            return result1
        else:
            return "PLease Sign in to view your orders"
    


    def get_doctors(self, data):
        if session['user_name'] != None:
            self.cur.execute(
                f"SELECT * FROM doclist WHERE speciality = '{data['speciality']}'")
            result = jsonify(self.cur.fetchall()).get_json()
            return result
          
        else:
            "Please Log In to book appointment"
            


obj = user_model()


@app.route("/",methods=['POST'])
def default_home():
    session['user_name'] = None
    return "Welcome to our website"
    


@app.route('/home-page')
def home_page():
    return render_template('index.html')




@app.route("/get-user", methods=['GET'])
def get_user():
    return obj.get_user(session['user_name'])


@app.route("/user/sign-up", methods=['POST', 'GET'])
def user_sign_up():
    
    userDetails = request.form
    data = {'name': userDetails['Full Name'], 'mob_number': userDetails['Enter Mobile Number'], 'email': userDetails['Enter a Valid Email'], 'user_name': userDetails['Create Username'],
            'password': userDetails['Create Password'], 'confirm_password': userDetails['Confirm Password'], 'dob': userDetails['Date of Birth'], 'sex': userDetails['Select Gender']}
    return obj.user_sign_up(data)



@app.route("/user/log-in", methods=['POST', 'GET'])
def user_log_in():
    
    userDetails = request.form
    data = {'user_name': userDetails['Name'],
            'password': userDetails['Password']}
    return obj.user_log_in(data)



@app.route("/user/log-out", methods=['POST', 'GET'])
def user_log_out():
    return obj.logout()



@app.route("/med-detail", methods=['POST', 'GET'])
def med_detail():
    
    drug = request.form
    # return drug
    data = {'medicine-name': drug['medicine-name']}
    return obj.med_detail(data)



@app.route("/select-speciality", methods=['POST', 'GET'])
def get_doctors():
    
    return obj.get_doctors(request.form)



@app.route("/book-an-appointment", methods=['POST', 'GET'])
def book_an_appointment():

    
    return obj.book_appointment(request.form)



@app.route("/order", methods=['POST', 'GET'])
def order_medicine():
    return obj.order_medicine(request.form)




@app.route("/my-appointment", methods=['GET'])
def get_appointment():
    return obj.get_appointment(session['user_name'])


@app.route("/my-order", methods=['GET'])
def my_order():
    return obj.my_order(session['user_name'])



@app.route("/contact-us")
def contact():
    return "Contact Us page here"



@app.route("/about-us")
def about():
    return "About Us page jere"



if __name__ == '__main__':
    app.run(debug=True)
