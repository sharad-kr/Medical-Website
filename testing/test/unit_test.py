import unittest
import json
from API import app
import requests
import coverage


class TestUserLogIn(unittest.TestCase):
    

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_set_session(self):
        response=self.app.post('/')
        self.assertEqual(response.status_code, 200)


    def test_user_log_in(self):
        # define test data
        test_data = {
            'Name': 'vivek_gupta',
            'Password': 'gupta'
        }

        # make POST request to /user/log-in endpoint
        response = self.app.post('/user/log-in', data=test_data)

        self.assertEqual(response.status_code, 200)
      

        self.assertEqual(response.json, [{"address":"Null","dob":"Thu, 21 Aug 2003 00:00:00 GMT","email":"vivek12@gmail.com","mob_number":"9929349800","name":"Vivek Gupta","password":"ebe475f8e6050882ece02f3ae1862fdc1d0a8fb64abf147d191d0052e8793b3d","sex":"male","user_id":1,"user_name":"vivek_gupta"}])
        

    def test_user_log_in_invalid_username(self):
        data = {'Name': 'vivek_g', 'Password': 'gupta'}
        response = self.app.post('/user/log-in', data=data)
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'id not found')

    def test_user_log_in_invalid_password(self):
        data = {'Name': 'vivek_gupta', 'Password': 'wrongpass'}
        response = self.app.post('/user/log-in', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'wrong password')


    def test_user_sign_up_already_exists(self):
            # Try to sign up with an existing user name
            response = self.app.post('/user/sign-up', data={
            'Full Name': 'Vivek Sharma',
            'Enter Mobile Number': '1234567890',
            'Enter a Valid Email': 'johndoe@example.com',
            'Date of Birth': '1990-01-01',
            'Select Gender': 'Male',
            'Create Username': 'vivek_gupta',
            'Create Password': 'mypassword',
            'Confirm Password' : 'mypassword'
            })
           
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_data(as_text=True), 'User name not available')

    def test_user_sign_up_password_mismatch(self):
        # Try to sign up with mismatching password fields
        response = self.app.post('/user/sign-up', data={
            'Full Name': 'Vivek Agrawal',
            'Enter Mobile Number': '1234567890',
            'Enter a Valid Email': 'johndoe@example.com',
            'Date of Birth': '1990-01-01',
            'Select Gender': 'Male',
            'Create Username': 'vivek_agrawal',
            'Create Password': 'mypassword',
            'Confirm Password' : 'ourpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'Password Mismatch !')

    def test_user_sign_up_successful(self):
        # Try to sign up with valid data
        response = self.app.post('/user/sign-up', data={
            'Full Name': 'Vivek Sharma',
            'Enter Mobile Number': '1234567890',
            'Enter a Valid Email': 'johndoe@example.com',
            'Date of Birth': '1990-01-01',
            'Select Gender': 'Male',
            'Create Username': 'vivek_sharma',
            'Create Password': 'mypassword',
            'Confirm Password' : 'mypassword'
        })
        self.assertEqual(response.status_code, 200)
        self


    def test_valid_medicine_name(self):
            self.log_in()
        # with patch('flask.g.db', MagicMock()):
            response = self.app.post('/med-detail', data={'medicine-name': 'semag'})
            # print(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.get_json(),list)

    def test_invalid_medicine_name(self):
            self.log_in()
        # with patch('flask.g.db', MagicMock()):
            response = self.app.post('/med-detail', data={'medicine-name': 'weiredname'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), [])

    def test_user_not_signed_in(self):
        # with app.app_context():
        self.app.post('/')
        response = self.app.post('/med-detail', data={'medicine-name': 'semag'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "Please Sign In to book medicine")


    def log_in(self):
        test_data1 = {
            'Name': 'vivek_gupta',
            'Password': 'gupta'
        }
        self.app.post('/user/log-in', data=test_data1)
        

    def test_user_sign_up(self):
        test_data = {
            'Full Name': 'John Doe',
            'Enter Mobile Number': '1234567890',
            'Enter a Valid Email': 'johndoe@example.com',
            'Date of Birth': '1990-01-01',
            'Select Gender': 'Male',
            'Create Username': 'johndoe',
            'Create Password': 'mypassword',
            'Confirm Password' : 'mypassword'
        }

        response = self.app.post('/user/sign-up', data=test_data)
        self.assertEqual(response.status_code, 200)

    def test_med_detail_WithOut_LogIn(self):
        self.app.post('/')
        test_data = {
            'medicine-name' : 'semag'
        }
        response = self.app.post('/med-detail', data=test_data)
        self.assertEqual(response.status_code, 200)

    def test_med_detail(self):
        self.log_in()
        test_data = {
            'medicine-name' : 'semag'
        }
        response = self.app.post('/med-detail', data=test_data)
        self.assertEqual(response.status_code, 200)

    def test_user_log_out(self):
        response = self.app.post('/user/log-out')
        self.assertEqual(response.status_code, 200)
    


    def test_get_doctors(self):
        self.log_in()

        test_data ={
            'speciality' : 'Cardiologist'
        }
        response = self.app.post('select-speciality',data=test_data)
        self.assertEqual(response.status_code, 200)


    def test_book_appointment(self):
        self.log_in()
        
        test_data = {
            'symptom' : 'Mujhe Kal se Bukhaar hai' , 'Doctor_ID' : '598' , 'appointment_date' : '2023-09-05'
        }
        response = self.app.post('/book-an-appointment',data=test_data)
        self.assertEqual(response.status_code, 200)


    def test_order_medicine(self):
        self.log_in()

        test_data = {
            'drug_id' : '165' , 'quantity' : '2' , 'address' : '102, Karol Bagh, Delhi'
        }
        response = self.app.post('/order',data=test_data)
        self.assertEqual(response.status_code, 200)


    def test_get_appointment(self):
        self.log_in()

        response = self.app.get('/my-appointment')
        self.assertEqual(response.status_code, 200)

    def test_my_order(self):
        self.log_in()
        response = self.app.get('/my-order')
        self.assertEqual(response.status_code, 200)
        

    def test_get_user(self):
        self.log_in()
        response = self.app.get('/get-user')
        self.assertEqual(response.status_code, 200)
    
    def test_contact_us(self):
        response = self.app.get('/contact-us')
        self.assertEqual(response.status_code, 200)

    def test_contact_us(self):
        response = self.app.get('/about-us')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()