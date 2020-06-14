# Reference: https://docs.python.org/2/library/unittest.html
import unittest
import MySQLdb
import index, car_api, flask_api, booking_api
from flask_bcrypt import Bcrypt
import speech_recognition as sr 


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
            if(cursor.fetchone()!=None):
                p = (cursor.fetchone()[2])
                if(bcrypt.check_password_hash(p, password)):
                    return True
            cursor.execute("select * from Admin where email = %s", (email,))
            if(cursor.fetchone()!=None):
                p = (cursor.fetchone()[2])
                if(bcrypt.check_password_hash(p, password)):
                    return True
            cursor.execute("select * from Engineer where email = %s", (email,))
            if(cursor.fetchone()!=None):
                p = (cursor.fetchone()[2])
                if(bcrypt.check_password_hash(p, password)):
                    return True
            else:
                return False


    def test_Engineer_login_pass(self):
        res = self.login("E001", "123")
        self.assertFalse(res)
    
    def test_Engineer_login_fail(self):
        res = self.login("E001", "1234")
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
        
    def test_admin_login_pass(self):
        res = self.login("A001", "123")
        self.assertFalse(res)
    
    def test_admin_login_fail(self):
        res = self.login("A001", "1234")
        self.assertFalse(res)
        
    def test_manager_login_pass(self):
        res = self.login("A001", "123")
        self.assertFalse(res)
    
    def test_manager_login_fail(self):
        res = self.login("A001", "1234")
        self.assertFalse(res)
      
    def scanQR(self):
        found = set()
        frame = cv2.imread("qr.jpg")
        frame = imutils.resize(frame, width = 400)
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            if barcodeData not in found:
                return(barcodeData)
        time.sleep(1)

    def qr_pass(self):
        res = self.scanQR()
        self.assertEquals(res, "E001")
        
    def qr_fail(self):
        res = self.scanQR()
        self.assertEquals(res, "E002")
        
    def testVoice(self):
        AUDIO_FILE = ("/home/pi/Desktop/Assignmnet02/voice/example.wav") 
        r = sr.Recognizer() 
        with sr.AudioFile(AUDIO_FILE) as source: 
            audio = r.record(source) 

        try: 
            return(r.recognize_google(audio)) 

        except sr.UnknownValueError: 
            print("Google Speech Recognition could not understand audio") 

        except sr.RequestError as e: 
            print("Could not request results from Google Speech Recognition service; {0}".format(e)) 


    def voice_pass(self):
        res = self.scanQR()
        self.assertEquals(res, "civic")
        
    def voice_fail(self):
        res = self.scanQR()
        self.assertEquals(res, "honda")
    
                    
if __name__ == "__main__":
    unittest.main()
