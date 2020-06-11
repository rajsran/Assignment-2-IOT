# Reference: https://docs.python.org/2/library/unittest.html
import unittest
import MySQLdb
import index, car_api, flask_api, booking_api
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class TestDatabaseUtils(unittest.TestCase):
    HOST = "34.87.232.0"
    USER = "root"
    PASSWORD = "123456"
    DATABASE = "People"
    
    def setUp(self):
        self.connection = MySQLdb.connect(TestDatabaseUtils.HOST, TestDatabaseUtils.USER,
            TestDatabaseUtils.PASSWORD, TestDatabaseUtils.DATABASE)
        
        self.connection.commit()

    def tearDown(self):
        try:
            self.connection.close()
        except:
            pass
        finally:
            self.connection = None

    def login(self, email, password):
        with self.connection.cursor() as cursor:
            cursor.execute("select * from User where email = %s", (email,))
            p = (cursor.fetchone()[2])
            if(bcrypt.check_password_hash(p, password)):
                return True
            else:
                return False


    def test_login_pass(self):
        res = self.login("raj19ptd@gmail.com", "123")
        self.assertTrue(res)
    
    def test_login_fail(self):
        res = self.login("raj19ptd@gmail.com", "1234")
        self.assertFalse(res)
        
    
    def book(self, carnumber):
        with self.connection.cursor() as cursor:
            cursor.execute("select * from Car where carnumber = %s", (carnumber,))
            msg = (cursor.fetchone())
            ava = msg[9]
            mai = msg[10]
            if (ava==0 or mai==1):
                return False
            else:
                return True
            
    def test_book_pass(self):
        res = self.book("honda3")
        self.assertTrue(res)
        
        
    def test_book_fail(self):
        res = self.book("honda4")
        self.assertFalse(res)
        
    
    def returncar(self, carnumber, user):
        with self.connection.cursor() as cursor:
            cursor.execute("select * from Booking where carnumber = %s and user = %s", (carnumber,user,))
            msg = (cursor.fetchone())
            if (msg!=None):
                return True
            else:
                return False
            
    def test_returncar_pass(self):
        res = self.returncar("honda4", "syeda")
        self.assertTrue(res)
        
    def test_returncar_fail(self):
        res = self.returncar("honda4", "reuben")
        self.assertFalse(res)
        
    
    def searchcar(self, carnumber):
        with self.connection.cursor() as cursor:
            cursor.execute("select * from Car where carnumber = %s", (carnumber,))
            msg = (cursor.fetchone())
            if (msg!=None):
                return True
            else:
                return False
            
    def test_searchcar_pass(self):
        res = self.searchcar("honda4")
        self.assertTrue(res)
        
    def test_searchcar_fail(self):
        res = self.searchcar("hondacity")
        self.assertFalse(res)
        
    def register(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute("select * from User where username = %s", (username,))
            msg = (cursor.fetchone())
            if (msg!=None):
                return True
            else:
                return False
            
    def test_register_pass(self):
        res = self.register("syeda")
        self.assertTrue(res)
        
    def test_register_fail(self):
        res = self.register("taman")
        self.assertFalse(res)
            
if __name__ == "__main__":
    unittest.main()
