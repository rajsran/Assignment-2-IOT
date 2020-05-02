import MySQLdb

class DatabaseUtils:
    HOST = "34.87.232.0"
    USER = "root"
    PASSWORD = "123456"
    DATABASE = "People"

    def __init__(self, connection = None):
        if(connection == None):
            connection = MySQLdb.connect(DatabaseUtils.HOST, DatabaseUtils.USER,
                DatabaseUtils.PASSWORD, DatabaseUtils.DATABASE)
        self.connection = connection

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def createCarTable(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                create table if not exists Car (
                    carnumber varchar(6) not null,
                    model varchar(20) not null,
                    color varchar(10),
                    feature varchar(200),
                    body_type varchar(30) not null,
                    seats int not null,
                    location varchar(100) not null,
                    cost_per_hour float not null,
                    photo blob,
                    constraint PK_Car primary key (carnumber)
                )""")
        self.connection.commit()
        print("Table created")
          

    def insertCar(self, carnum,model,color,features,body_type,seats,location,cost,photo):
        with self.connection.cursor() as cursor:
            #with open(photo, 'rb') as file:
                #blobData = file.read()
            '''carnum = '\'' + carnum + '\''
            model = '\'' + model + '\''
            color = '\'' + color + '\''
            features = '\'' + features + '\''
            body_type = '\'' + body_type + '\''
            location = '\'' + location + '\''
            photo = '\'' + photo + '\''
            numofseats = int(seats)
            costph = float(cost)'''
            
            tupledata = (carnum,model,color,features,body_type,seats,location,cost,photo)
            cursor.execute("insert into Car values(%s,%s,%s,%s,%s,%s,%s,%s,load_file(%s))", tupledata)
        self.connection.commit()
        return cursor.rowcount == 1

    def getCar(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select * from Car")
            return cursor.fetchall()

    def deleteCar(self, carnum):
        with self.connection.cursor() as cursor:
            # Note there is an intentionally placed bug here: != should be =
            _sql = "delete from Car where carnumber like '{0}'"
            cursor.execute(_sql.format(carnum))
            #cursor.execute("", (carnum))
        self.connection.commit()
        return cursor.rowcount == 1
