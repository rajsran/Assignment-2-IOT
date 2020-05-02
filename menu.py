from database_utils import DatabaseUtils

class Menu:
    def main(self):
        with DatabaseUtils() as db:
            db.createCarTable()
        self.runMenu()

    def runMenu(self):
        while(True):
            print()
            print("1. List Cars")
            print("2. Insert Car")
            print("3. Delete car")
            print("4. Quit")
            selection = input("Select an option: ")
            print()

            if(selection == "1"):
                self.listCar()
            elif(selection == "2"):
                self.insertCar()
            elif(selection == "3"):
                num = input("Car number of car to delete:")
                self.deleteCar(num)
            elif(selection == "4"):
                print("Goodbye!")
                break
            else:
                print("Invalid input - please try again.")

    def listCar(self):
        print("--- Cars ---")
        with DatabaseUtils() as db:
            for car in db.getCar():
                print("{:<15} {}".format(car[0], car[1],car[2], car[3],car[4], car[5],car[6], car[7],car[8] ))

    def deleteCar(self, num):
        with DatabaseUtils() as db:
            if(db.deleteCar(num)):
                print("{} Deleted successfully.".format(num))
            else:
                print("{} failed to be deleted.".format(num))
               
            
    def insertCar(self):
        print("--- Insert Car ---")
        number = input("Enter the car number: ")
        model = input("Enter the car model: ")
        color = input("Enter the car color: ")
        feature = input("Enter the car feature: ")
        body_type = input("Enter the car type: ")
        seats = int(input("Enter the number of seats: "))
        location = input("Enter the location: ")
        cph = float(input("Enter the cost per hour: "))
        img = input("Enter image location:")
        
        with DatabaseUtils() as db:
            if(db.insertCar(number,model,color,feature,body_type, seats , location,cph,img)):
                print("{} inserted successfully.".format(number))
            else:
                print("{} failed to be inserted.".format(number))

if __name__ == "__main__":
    Menu().main()
