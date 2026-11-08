from datetime import datetime,date
from database import cursor
import csv
from exception import InvalidDateError


def get_booking_dates():
    while True:
            check_in=input("Enter check_in: ")
            try:
                check_in_date=datetime.strptime(check_in,"%d-%m-%Y").date()
    
                if check_in_date<date.today():
                    raise InvalidDateError("Check-in can't be in past")
                elif (check_in_date-date.today()).days>180:
                    raise InvalidDateError("Check in date can't be more than 180 days ahead")
                else:
                    break
            except ValueError:
                print("invalid date format")

            except InvalidDateError as e:
                print(e)
    
    while True:
        check_out=input("enter check-out date: ")
        try:
            check_out_date=datetime.strptime(check_out,"%d-%m-%Y").date()
            nights=(check_out_date-check_in_date).days

            if nights<=0:
                print("check-out must be after check-in")
            elif nights>30:
                print("max stay is 30 nights")
            else:
                return check_in_date,check_out_date,nights

        except ValueError:
            print("invalid date format")



def search_availability():
    while True:
        room_type=input("enter room type (Standard/Deluxe/Suite): ").strip().capitalize()

        if room_type not in ['Standard','Deluxe','Suite']:
            print("invalid room type")
        else:
            break

    max_guests={'Standard':2,"Deluxe":3,"Suite":4}
    while True:
        try:
            guests=int(input("Enter no of guests: "))
            if guests<=0:
                print("guests must be greater than 0")
            elif guests>max_guests[room_type]:
                print("max guests allowed: ",max_guests[room_type])
            else:
                break
        except ValueError:
            print("Enter a valid num")
    # while True:
    #     check_in=input("Enter check_in: ")
    #     try:
    #         check_in_date=datetime.strptime(check_in,"%d-%m-%Y").date()

    #         if check_in_date<date.today():
    #             print("Check-in can't be in past")
    #         elif (check_in_date-date.today()).days>180:
    #             print("Check in date can't be more than 180 days ahead")
    #         else:
    #             break
    #     except ValueError:
    #         print("invalid date format")

    # while True:
    #     check_out=input("enter check-out date: ")
    #     try:
    #         check_out_date=datetime.strptime(check_out,"%d-%m-%Y").date()
    #         nights=(check_out_date-check_in_date).days

    #         if nights<=0:
    #             print("check-out must be after check-in")
    #         elif nights>30:
    #             print("max stay is 30 nights")
    #         else:
    #             return check_in_date,check_out_date,nights
#
        # except ValueError:
        #     print("invalid date format")

    check_in_date,check_out_date,nights=get_booking_dates()
    cursor.execute("""select room_no,room_type,floor from rooms
                    where room_type=? order by room_no""",(room_type,))
    rooms=cursor.fetchall()
    available_rooms=[]
    for room in rooms:
        room_no=room[0]

        cursor.execute("""select booking_id from bookings
                        where room_no=? and upper(status) in ("CONFIRMED","CHECKED_IN")
                        and ? < check_out
                        and ? > check_in""",
                        (room_no,check_in_date.strftime("%Y-%m-%d"),check_out_date.strftime("%Y-%m-%d")))

        booking=cursor.fetchone()
        if booking is None:
            available_rooms.append(room)
    if len(available_rooms)==0:
        print("No rooms available for the selected dates")
    else:
        print("Available_rooms:\n")
        for room in available_rooms:
            print("Room No: ",room[0],"Room typee: ",room[1],"Floor: ",room[2])

        print("total available rooms:",len(available_rooms))


def occupancy_report():
    try:
        while True:
            start_date=input("enter start date: ")
            try:
                start_date=datetime.strptime(start_date,"%d-%m-%Y").date()
                break
            except ValueError:
                print("invalid start date")

        while True:
            end_date=input("Enter end date: ")
            try:
                end_date=datetime.strptime(end_date,"%d-%m-%Y").date()
                if end_date<start_date:
                    print("end date must be after or equal to start date")

                else:
                    break
            except ValueError:
                print("invalid end date")
        cursor.execute("""select b.booking_id,r.room_no,r.room_type,
                        g.name,b.check_in,b.check_out,b.guests,b.status
                        from bookings b
                        join guests g on b.guest_id=g.guest_id
                        join rooms r on b.room_no=r.room_no
                        where upper(b.status) in ('CONFIRMED','CHECKED_IN','CHECKED_OUT') 
                        and b.check_in <= ?
                        and b.check_out >?
                        order by r.room_no""",(end_date.strftime("%Y-%m-%d"),
                                                start_date.strftime("%Y-%m-%d")))
        bookings=cursor.fetchall()

        print("--------Occupancy Report--------")
        print("Start date: ",start_date.strftime("%d-%m-%Y"))
        print("End date: ",end_date.strftime("%d-%m-%Y"))

        if not bookings:
            print("No bookings found for this period")
            print("Occupied rooms: 0")
            return
        print("Total occupied bookings: ",len(bookings))

        for booking in bookings:
            print("Booking id: ",booking[0])
            print("Room number: ",booking[1])
            print("Room type: ",booking[2])
            print("Guest Name: ",booking[3])
            print("Check-in: ",booking[4])
            print("Check-out: ",booking[5])
            print("Guests: ",booking[6])
            print("Status: ",booking[7])
            print("                                                                 ")

    except Exception as e:
        print("Occupancy report failed:",e)



def revenue_report():
    try:
        cursor.execute("""select distinct room_type from rooms""")
        room_types=cursor.fetchall()
        total_revenue=0

        print("-------Revenue Report-------")
        for room in room_types:
            room_type=room[0]
            cursor.execute("""select b.total_amount from bookings b
                            join rooms r on b.room_no=r.room_no
                            where r.room_type=? and upper(b.status) in 
                            ("CONFIRMED","CHECKED_IN","CHECKED_OUT")""",(room_type,))

            amounts=cursor.fetchall()
            booking_count=0
            revenue=0

            for amount in amounts:
                booking_count=booking_count+1
                revenue=revenue+amount[0]

            print("Room type: ",room_type)
            print("Total Bookings: ",booking_count)
            print("Total revenue: ",revenue)

            total_revenue=total_revenue+revenue
        print("                                 ")
        print("Overall revenue: ",total_revenue)
    except Exception as e:
        print("Revenue report failed: ",e)


def export_all_bookings():
    try:
        cursor.execute("""select b.booking_id,g.name,g.mobile,g.email,
                            r.room_no,r.room_type,b.check_in,b.check_out,
                            b.guests,b.total_amount,b.status
                            from bookings b 
                            join guests g on b.guest_id=g.guest_id
                            join rooms r on b.room_no=r.room_no
                            order by b.booking_id""")
        bookings=cursor.fetchall()
        with open("bookings.csv","w") as file:
            writer=csv.writer(file)
            writer.writerow(["Booking id","Guest Name","Mobile","Email","Room Number","Room Type","Check-in","Check-out","Guests","Total Amount","Status"])
            for booking in bookings:
                writer.writerow(booking)
        print("Booking exported successfully")
        print("total bookings exported: ",len(bookings))
        print("File name: bookings.csv")

    except Exception as e:
        print("Export failed: ",e)