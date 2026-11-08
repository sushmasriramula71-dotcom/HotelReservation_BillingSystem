import sqlite3
import csv
con=sqlite3.connect("databases.db")
cursor=con.cursor()

query1="""create table if not exists rooms(
            room_no integer primary key,
            room_type varchar not null,
            floor int not null)
            """
cursor.execute(query1)

query2="""
        create table if not exists guests(
        guest_id integer primary key autoincrement,
        name varchar(20) not null,
        mobile varchar(20) unique not null,
        email varchar(20) not null)
        """
cursor.execute(query2)

query3="""create table if not exists bookings(
        booking_id integer primary key autoincrement,
        guest_id int,
        room_no int,
        check_in varchar(10),
        check_out varchar(10),
        guests int,
        total_amount decimal(10,2),
        status varchar(20) default "CONFIRMED",
        breakfast int default 0,
        room_charge decimal(10,2) default 0,
        extra_guest_charge decimal(10,2) default 0,
        breakfast_charge decimal(10,2) default 0,
        long_stay_discount decimal(10,2) default 0,
        loyalty_discount decimal(10,2) default 0,
        gst decimal(10,2) default 0,
        foreign key (guest_id) references guests(guest_id),
        foreign key (room_no) references rooms(room_no))"""
cursor.execute(query3)


con.commit()

with open("rooms.csv",'r') as file:
    reader=csv.DictReader(file)
    for row in reader:
        try:
            room_no=int(row["room_no"])
            room_type=row["room_type"].strip().capitalize()
            floor=int(row["floor"])

            if room_no <=0 or floor<=0:
                raise ValueError("values greater than 0")
            if room_type not in ['Standard','Deluxe','Suite']:
                raise ValueError("invalid room type")

            cursor.execute("""insert or ignore into rooms(room_no,room_type,floor) values(?,?,?)""",(room_no,room_type,floor))

        except ValueError as e:
            with open("errors.txt",'w')as error:
                error.write(f"{row}--{e}")
                print("Errors saved to error.txt file")

con.commit()
# print("room vals inserted")


