from model import StandardRoom,DeluxeRoom,SuiteRoom
from database import con, cursor
from exception import (InvalidGuestError,InvalidRoomError,RoomNotAvailableError,BookingStatusError,BookingNotFoundError)
from datetime import datetime,timedelta,date
from pricing import *
import os
# from pathlib import path 
import sqlite3
            


def register_guests():
    while True:
        no_of_guests=int(input("Enter no of guests: "))
        if no_of_guests<=0:
            print("no of guests must be greater than 0")
        else:
            break

    
    while True:
        try:
            name=input("Enetr guest name: ").strip()
            if name=="":
                # print("name can't be null")
                raise InvalidGuestError("Guest name can't be empty")
            else:
                break
        except InvalidGuestError as e:
            print(e)

    while True: 
        mobile=input("Enter mobilenumber: ").strip()
        try:
            if mobile=="":
                # print("mobile can't be null")
                raise InvalidGuestError("Mobile can't be null")
            elif len(mobile)!=10:
                # print("mobile num should contains 10 digits")
                raise InvalidGuestError("Invalid Mobile number")
            elif not mobile.isdigit():
                # print("mobile number should contains only digits")
                raise  InvalidGuestError("Mobile number should contain only digits")
            elif mobile[0] not in '6789':
                # print("mobile num should start with 6789")
                raise InvalidGuestError("mobile number should start with 6789")
            
            else:
                break
        except InvalidGuestError as e:
            print(e)

    while True:
        email=input("Enter eamil: ").strip()
        try:
            if email=="":
                # print("email can't be null")
                raise InvalidGuestError("email can't be null")
            elif "@" not in email or "." not in email: 
                # print("email format is not valid")
                raise InvalidGuestError("invalid email address")
            elif email.index("@")>email.index("."):
                # print("email format is not valid")
                raise InvalidGuestError("invalid email format")
            else:
                break
        except InvalidGuestError as e:
            print(e)

    try:
        # cursor.execute("select guest_id from guests where mobile=?",(mobile,))
        # existing_guest=cursor.fetchone()

        
        cursor.execute("""insert into guests(name,mobile,email) values(?,?,?)""",(name,mobile,email))
        con.commit()


            # guest_id=cursor.lastrowid
            # print("Guest registered sucessfully")
            # print("guestid",guest_id)
            # if i==0:
        primary_guest_id=cursor.lastrowid

    except InvalidGuestError as e:
        print(e)
        return None, None

    except Exception as e:
        con.rollback()
        print("Database error",e)
        return None,None
    return primary_guest_id,no_of_guests

def create_room(room_no,room_type,floor):
    if room_type=="Standard":
        return StandardRoom(room_no,floor)
    elif room_type=="Deluxe":
        return DeluxeRoom(room_no,floor)
    elif room_type=="Suite":
        return SuiteRoom(room_no,floor)

def select_room_type(no_of_guests):
    while True:
        room_type=input("Enter room type: ").strip().capitalize()

        if room_type=="Standard":
            room=StandardRoom(0,0)
        elif room_type=="Deluxe":
            room=DeluxeRoom(0,0)
        elif room_type=='Suite':
            room=SuiteRoom(0,0)
        else:
            try:
                raise InvalidRoomError("invalid room type")
            except InvalidRoomError as e:
                print(e)
                # print("invalid room type")
                continue

        if no_of_guests>room.get_max_guests():
            try:
                raise InvalidRoomError("max guests allowed: ",str(room.get_max_guests()))
            except InvalidRoomError as e:
                print(e)
        else:
            return room_type

        
def find_available_room(room_type,check_in_date,check_out_date):
    query="""select room_no,room_type,floor from rooms
            where room_type=? order by room_no"""
    cursor.execute(query,(room_type,))
    rooms=cursor.fetchall()

    for room in rooms:
        room_no=room[0]

        cursor.execute("""select booking_id from bookings 
                            where room_no=? and upper(status) in ('CONFIRMED','CHECKED_IN')
                            and ? <check_out and ? > check_in""",(room_no,check_in_date.strftime("%Y-%m-%d"),check_out_date.strftime("%Y-%m-%d")))
        booking=cursor.fetchone()
        if booking is None:
            return room
    try:
        raise RoomNotAvailableError("no room available for selected dates")
    except RoomNotAvailableError as e:
        print(e)
        return None

def calculate_booking_amount(room,check_in_date,nights,guests,breakfast,completed_stays):
    room_charge=calculate_room_charge(room,check_in_date,nights)
    extra_guest_charge=calculate_extra_guest_charge(room,guests,nights)
    breakfast_charge=calculate_breakfast_charge(room,guests,nights,breakfast)
    long_stay_discount=calculate_long_stay_discount(room_charge,nights)
    subtotal=room_charge+extra_guest_charge+breakfast_charge
    loyalty_discount=calculate_loyalty_discount(subtotal-long_stay_discount,completed_stays)
    taxable_amount=subtotal-long_stay_discount-loyalty_discount
    gst=0
    if subtotal>0:
        discount_ratio=taxable_amount/subtotal
    else:
        discount_ratio=0

    for i in range(nights):
        current_date=check_in_date+timedelta(days=i)
        nightly_rate=calculate_weekend_rate(room,current_date)

        night_amount=nightly_rate
        night_amount=night_amount+room.get_extra_guest_charge(guests)
        if breakfast:
            night_amount=night_amount+(room.get_breakfast_charge()*guests)
        night_amount=night_amount*discount_ratio

        if nightly_rate<=7500:
            gst=gst+(night_amount*0.12)
        else:
            gst=gst+(night_amount*0.18)
    total_amount=taxable_amount+gst
    print("Room charge: ",room_charge)
    print("Extra guest charge: ",extra_guest_charge)
    print("Breakfast charges: ",breakfast_charge)
    print("Long stay discount: ",long_stay_discount)
    print("Loyalty discount: ",loyalty_discount)
    print("GST: ",gst)
    print("total amount: ",total_amount)
    return (room_charge,extra_guest_charge,breakfast_charge,long_stay_discount,loyalty_discount,gst,total_amount)


def generate_invoice(booking_id):
    try:
        cursor.execute("""select b.booking_id,b.check_in,b.check_out,b.guests,
                        b.total_amount,b.breakfast,b.room_charge,b.extra_guest_charge,
                        b.breakfast_charge,b.long_stay_discount,b.loyalty_discount,b.gst,
                        g.name,g.mobile,g.email,r.room_no,r.room_type,r.floor
                        from bookings b
                        join guests g on b.guest_id=g.guest_id
                        join rooms r on b.room_no=r.room_no
                        where b.booking_id=?""",(booking_id,))
        booking=cursor.fetchone()
        if booking is None:
            raise BookingNotFoundError("Booking not found")
        check_in_date=datetime.strptime(booking[1],"%Y-%m-%d").date()
        check_out_date=datetime.strptime(booking[2],"%Y-%m-%d").date()
        room=create_room(booking[15],booking[16],booking[17])

        file_name="invoices/BK"+str(booking_id).zfill(4)+".txt"
        with open(file_name,'w') as file:
            file.write("========STAYEASY HOTEL========\n")
            file.write("        INVOICES     \n")
            file.write("------------------------------------\n")
            file.write("Booking ID: "+str(booking[0])+"\n")
            file.write("Guest Name: "+booking[12]+"\n")
            file.write("Mobile: "+booking[13]+"\n")
            file.write("Email: "+booking[14]+"\n")
            file.write("Room number: "+str(booking[15])+"\n")
            file.write("Room type: "+booking[16]+"\n")
            file.write("Floor: "+str(booking[17])+"\n")
            file.write("Check-in: "+str(check_in_date)+"\n")
            file.write("check-out: "+str(check_out_date)+"\n")
            file.write("Guests: "+str(booking[3])+"\n")
            file.write("\n------------Night-Wise Charges------------\n")
            nights=(check_out_date-check_in_date).days
            for i in range(nights):
                current_date=check_in_date+timedelta(days=i)
                nightly_rate=calculate_weekend_rate(room,current_date)
                extra_charge=room.get_extra_guest_charge(booking[3])
                breakfast_charge=0
                if booking[5]:
                    breakfast_charge=(room.get_breakfast_charge()*booking[3])
                file.write(str(current_date) +
                    " | Room: Rs. " + str(nightly_rate) +
                    " | Extra Guest: Rs. " + str(extra_charge) +
                    " | Breakfast: Rs. " + str(breakfast_charge) + "\n")
            file.write("\n-------------Price Summary---------------\n")
            file.write("Room Charge: Rs. "+str(booking[6])+"\n")
            file.write("Extra Guest Charge: Rs. "+str(booking[7])+"\n")
            file.write("Breakfast Charge: Rs. "+str(booking[8])+"\n")
            file.write("Long stay Discount: Rs. "+str(booking[9])+"\n")
            file.write("Loyalty Discount: Rs. "+str(booking[10])+"\n")
            file.write("GST: Rs. "+str(booking[11])+"\n")
        
            file.write("------------------------------------\n")
            file.write("TOTAL AMOUNT: Rs. " + str(booking[4]) + "\n")
            file.write("====================================\n")

        print("Invoice generated successfully")
        print("File name:", file_name)

    except BookingNotFoundError as e:
        print(e)

    except Exception as e:
        print("Invoice generation failed:", e)



def check_out_booking():
    try:
        booking_id=int(input("Enter booking id: "))
        cursor.execute("""select status from bookings where booking_id=?""",(booking_id,))
        booking=cursor.fetchone()

        
        if booking is None:
            raise BookingNotFoundError("Booking not found")
        status=booking[0].upper()

        print("statusvalue: ",repr(status))
        print("Comparision: ",status!="CHECKED_IN")
        
        if status !="CHECKED_IN":
            raise BookingStatusError("check not allowd current status: "+status)
        cursor.execute("""update bookings set status=? where booking_id=? """,("CHECKED_OUT",booking_id))
        con.commit()
        print("checkout successfull")
        generate_invoice(booking_id)

    except BookingNotFoundError as e:
        print(e)

    except BookingStatusError as e:
        print(e)

    except ValueError:
        print("enter valid bookind id")

    except Exception as e:
        con.rollback()
        print("Checkout failed: ",e)



# def generate_invoice(booking_id):
#     cursor.execute("""
#         select b.booking_id,b.room_no,b.check_in,b.check_out,
#                b.guests,b.breakfast,b.total_amount,
#                b.room_charge,b.extra_guest_charge,
#                b.breakfast_charge,b.long_stay_discount,
#                b.loyalty_discount,b.gst,
#                g.name,g.mobile,g.email,r.room_type
#         from bookings b
#         join guests g on b.guest_id=g.guest_id
#         join rooms r on b.room_no=r.room_no
#         where b.booking_id=?
#     """,(booking_id,))

#     booking=cursor.fetchone()

#     if booking is None:
#         print("Booking details not found")
#         return None

#     invoice_folder=Path("invoices")
#     invoice_folder.mkdir(exist_ok=True)

#     invoice_file=invoice_folder/("BK"+str(booking_id)+".txt")

#     file=open(invoice_file,"w")

#     file.write("========== STAYEASY HOTEL ==========\n")
#     file.write("              INVOICE\n")
#     file.write("====================================\n\n")

#     file.write("Booking ID: "+str(booking[0])+"\n")
#     file.write("Guest Name: "+str(booking[13])+"\n")
#     file.write("Mobile Number: "+str(booking[14])+"\n")
#     file.write("Email: "+str(booking[15])+"\n")
#     file.write("Room Number: "+str(booking[1])+"\n")
#     file.write("Room Type: "+str(booking[16])+"\n")
#     file.write("Check-in: "+str(booking[2])+"\n")
#     file.write("Check-out: "+str(booking[3])+"\n")
#     file.write("Guest Count: "+str(booking[4])+"\n")
#     file.write("Breakfast: "+str(booking[5])+"\n")

#     file.write("\n========== BILL DETAILS ==========\n")

#     file.write("Room Charge: Rs."+str(booking[7])+"\n")
#     file.write("Extra Guest Charge: Rs."+str(booking[8])+"\n")
#     file.write("Breakfast Charge: Rs."+str(booking[9])+"\n")
#     file.write("Long Stay Discount: Rs."+str(booking[10])+"\n")
#     file.write("Loyalty Discount: Rs."+str(booking[11])+"\n")
#     file.write("GST: Rs."+str(booking[12])+"\n")

#     file.write("\n========== BILL SUMMARY ==========\n")
#     file.write("Total Amount: Rs."+str(booking[6])+"\n")

#     file.write("====================================\n")
#     file.write("       THANK YOU FOR VISITING!\n")
#     file.write("====================================\n")

#     file.close()

#     print("Invoice generated:",invoice_file)
#     return invoice_file






# def checkout_booking(booking_id):
#     try:
#         cursor.execute("""
#             select status from bookings
#             where booking_id=?
#         """,(booking_id,))

#         booking=cursor.fetchone()

#         if booking is None:
#             raise BookingNotFoundError("Booking ID not found")

#         status=booking[0].upper()

#         if status!="CHECKED_IN":
#             raise BookingStatusError("Check-out not allowed current status: "+status)

#         invoice_file=generate_invoice(booking_id)

#         if invoice_file is None:
#             return

#         cursor.execute("""
#             update bookings
#             set status=?
#             where booking_id=?
#         """,("CHECKED_OUT",booking_id))

#         con.commit()

#         print("Guest checked out successfully!")

#     except BookingNotFoundError as e:
#         print(e)

#     except BookingStatusError as e:
#         print(e)

#     except Exception as e:
#         con.rollback()
#         print("Checkout failed:",e)


def check_in_booking():
    try:
        booking_id=int(input("Enter booking id: "))
        cursor.execute("""select check_in,status from bookings where booking_id=?""",(booking_id,))
        booking=cursor.fetchone()
        if booking is None:
            raise BookingNotFoundError("Booking not found")
            return
        check_in_date=booking[0]
        status=booking[1].upper()

        if status!="CONFIRMED":
            raise BookingStatusError("check in not allowed current status: "+status)
        today=date.today().strftime("%Y-%m-%d")
        if today!=check_in_date:
            print("Check in is allowed only on the booking date")
            return 
        cursor.execute("""update bookings set status=? where booking_id=?""",("CHECKED_IN",booking_id,))
        con.commit()
        print("Check in successfull")
    except BookingStatusError as e:
        print(e)
    except BookingNotFoundError as e:
        print(e)
    except ValueError:
        print("enter a valid booking id")
    except Exception as e:
        con.rollback()
        print("Check-in failed: ",e)


def cancel_booking():
    try:
        booking_id=int(input("Enter booking id: "))
        cursor.execute("""select check_in,total_amount,status from bookings where booking_id=?""",(booking_id,))
        booking=cursor.fetchone()
        if booking is None:
            print("Booking not found")
            return
        check_in_date=datetime.strptime(booking[0],"%Y-%m-%d").date()
        total_amount=booking[1]
        status=booking[2].upper()

        if status!="CONFIRMED":
            raise BookingStatusError("cancellation not allowed,current status: "+status)
            
        days_before_checkin=(check_in_date-date.today()).days
        if days_before_checkin>=7:
            refund=total_amount
            refund_percentage=100
        elif days_before_checkin>=2:
            refund=total_amount*0.50
            refund_percentage=50
        else:
            refund=0
            refund_percentage=0

        cursor.execute("""update bookings set status="CANCELLED" where booking_id=?""",(booking_id,))
        con.commit()

        print("Booking cancelled successfully")
        print("Refund percentage: ",refund_percentage,"%")
        print("Refund amount: Rs.",refund)
    except ValueError:
        print("Enter a valid booking id")
    except BookingStatusError as e:
        print(e)
    except BookingNotFoundError as e:
        print(e)
    except Exception as e:
        con.rollback()
        print("Cancellation failed: ",e)

def view_booking_details():
    try:
        booking_id=int(input("enter booking id: "))
        cursor.execute("""select b.booking_id,b.check_in,b.check_out,
                            b.guests,b.total_amount,b.status,g.name,
                            g.mobile,g.email,r.room_no,r.room_type,r.floor
                            from bookings b
                            join guests g on b.guest_id=g.guest_id
                            join rooms r on b.room_no=r.room_no
                            where b.booking_id=?""",(booking_id,))
        booking=cursor.fetchone()
        if booking is None:                                                          
            raise BookingNotFoundError("Booking not fonud")
            

        print("---------Booking details---------")
        print("Booking id: ",booking[0])
        print("Guest Name: ",booking[6])
        print("Mobile: ",booking[7])
        print("Email: ",booking[8])
        print("Room Number: ",booking[9])
        print("Room Type: ",booking[10])
        print("Floor: ",booking[11])
        print("Check-in: ",booking[1])
        print("Check-out: ",booking[2])
        print("Number of guests: ",booking[3])
        print("Total Amount: ",booking[4])
        print("Booking Status: ",booking[5])
        print("                                                     ")
    except BookingNotFoundError as e:
        print(e)
    except ValueError:
        print("Enter a valid booking id")
    except Exception as e:
        print("Unable to fetch booking details:",e)

def guest_stay_history():
    try:
        mobile=input("Enter guest mobile num: ").strip()
        if len(mobile)!=10 or not mobile.isdigit() or mobile[0] not in '6789':
            raise InvalidGuestError("Enter a valid 10-didgit mobile number")
        cursor.execute("""select b.booking_id,r.room_no,r.room_type,
                            b.check_in,b.check_out,b.guests,
                            b.total_amount,b.status
                            from bookings b
                            join guests g on b.guest_id=g.guest_id
                            join rooms r on b.room_no=r.room_no
                            where g.mobile=?
                            order by b.booking_id""",(mobile,))
        bookings=cursor.fetchall()
        if not bookings:
            raise BookingNotFoundError("no booking history")
            

        print("Guest stay history")
        for booking in bookings:
            print("booking id: ",booking[0])
            print("Room number: ",booking[1])
            print("Room type: ",booking[2])
            print("check-in: ",booking[3])
            print("check-out: ",booking[4])
            print("Guests: ",booking[5])
            print("Total Amount: ",booking[6])
            print("Status: ",booking[7])
            print("                                                             ")
    except BookingNotFoundError as e:
        print(e)
    except InvalidGuestError as e:
        print(e)
    except Exception as e:
        print("unable to fetch guest history: ",e)






