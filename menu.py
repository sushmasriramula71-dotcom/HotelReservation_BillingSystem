from database import con,cursor
from reports import search_availability,get_booking_dates,occupancy_report,revenue_report,export_all_bookings
from main import (register_guests,select_room_type,find_available_room,create_room,calculate_booking_amount,check_in_booking,cancel_booking,view_booking_details,guest_stay_history,check_out_booking)
# from reports import search_availability,get_booking_dates
# from pricing import (calculate_nights,calculate_room_charge,calculate_extra_guest_charge,
#                      calculate_breakfast_charge,calculate_long_stay_discount,calculate_loyalty_discount,calculate_weekend_rate,calculate_gst)

         

while True:
    print("""       STAYEASY HOTEL  
        1.Search room availability
        2.Create booking
        3.Check-in
        4.Check-out
        5.Cancel booking
        6.View booking details
        7.Guest stay history
        8.Occupancy report
        9.Revenue report
        10.Export all booking to csv
        11.Exit """)
    choice=input("enter your choice: ").strip()
    if choice=='1':
        print("Search room availability selected")
        search_availability()


    elif choice=='2':
        print("create booking selected")
        primary_guest_id,no_of_guests=register_guests()
        if primary_guest_id is not None:
            room_type=select_room_type(no_of_guests)
            check_in_date,check_out_date,nights=get_booking_dates()
            room=find_available_room(room_type,check_in_date,check_out_date)
            if room is None:
                print("no rooms available ")
            else:
                print("Room available")
                print("Room Number: ",room[0])
                print("Room Type: ",room[1])
                print("Floor: ",room[2])

                print("primary guesst id: ",primary_guest_id)
                print("total guests: ",no_of_guests)
                print("selected room type: ",room_type)
                room_obj=create_room(room[0],room[1],room[2])
                if room[1]=='Standard':
                    while True:
                        breakfast=input("Do you want breakfast: (yes/no)").strip().lower()
                        if breakfast=='yes':
                            breakfast=True
                            break
                        elif breakfast=='no':
                            breakfast=False
                            break
                        else:
                            print("enter yes or no: ")
                else:
                    breakfast=False
                cursor.execute("""select count(*) from bookings where guest_id=? and upper(status)='CHECKED_OUT'""",(primary_guest_id,))
                completed_stays=cursor.fetchone()[0]
                print("Completed stays:",completed_stays)

                try: 
                    (room_charge,extra_guest_charge,breakfast_charge,long_stay_discount,loyalty_discount,gst,total_amount) = calculate_booking_amount(room_obj,check_in_date,nights,no_of_guests,breakfast,completed_stays)
                
                    cursor.execute("""insert into bookings(guest_id,room_no,check_in,check_out,guests,total_amount,status) values(?,?,?,?,?,?,?)""",
                                   (primary_guest_id,room[0],check_in_date.strftime("%Y-%m-%d"),
                                    check_out_date.strftime("%Y-%m-%d"),
                                    no_of_guests,total_amount,"CONFIRMED"))
                    cursor.execute("""
                        INSERT INTO bookings
                        (guest_id, room_no, check_in, check_out, guests,
                        total_amount, status, breakfast, room_charge,
                        extra_guest_charge, breakfast_charge,
                        long_stay_discount, loyalty_discount, gst)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        primary_guest_id,
                        room[0],
                        check_in_date.strftime("%Y-%m-%d"),
                        check_out_date.strftime("%Y-%m-%d"),
                        no_of_guests,
                        total_amount,
                        "CONFIRMED",
                        int(breakfast),
                        room_charge,
                        extra_guest_charge,
                        breakfast_charge,
                        long_stay_discount,
                        loyalty_discount,
                        gst
                    ))
                    con.commit()
                    booking_id=cursor.lastrowid
                    print("Booking created successfully")
                    print("Booking id: ",booking_id)
                    print("Total amount paid: ",total_amount)
                    print("Booking status: CONFIRMED")
                except Exception as e:
                    con.rollback()
                    print("Booking failed: ",e)
    

    elif choice=='3':
        print("Check in selected")
        check_in_booking()

    elif choice=='4':
        print("check out and generated invoice selected")
        check_out_booking()

    elif choice=='5':
        print("Cancel booking selected")
        cancel_booking()

    elif choice=='6':
        print("View booking details selected")
        view_booking_details()

    elif choice=='7':
        print("Guest stay history selected")
        guest_stay_history()

    elif choice=='8':
        print("Occupancy report selected")
        occupancy_report()

    elif choice=='9':
        print("Revenue report selected")
        revenue_report()

    elif choice=='10':
        print("Export booking to csv selected")
        export_all_bookings()

    elif choice=='11':
        print("Thank you for using stayeasy hotel")
        break

    else:
        print("Invalid choice")
    



