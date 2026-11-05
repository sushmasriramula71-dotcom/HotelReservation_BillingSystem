from datetime import timedelta

def calculate_nights(check_in,check_out):
    return (check_out-check_in).days

def calculate_weekend_rate(room,date):
    rate=room.get_rate()
    if date.weekday()==4 or date.weekday()==5:
        rate=rate+(rate*0.20)
    return rate

def calculate_extra_guest_charge(room,guests,nights):
    return room.get_extra_guest_charge(guests)*nights

def calculate_room_charge(room,check_in,nights):
    total=0
    for i in range(nights):
        current_date=check_in+timedelta(days=i)
        rate=calculate_weekend_rate(room,current_date)
        total=total+rate

    return total

def calculate_loyalty_discount(amount,completed_stays):
    if completed_stays>=3:
        return amount*0.05
    else:
        return 0

def calculate_breakfast_charge(room,guests,nights,breakfast):
    if breakfast and room.get_breakfast_charge()>0:
        return room.get_breakfast_charge()*guests*nights
    return 0

def calculate_long_stay_discount(room_charge,nights):
    if nights>=7:
        return room_charge*0.10
    else:
        return 0

def calculate_gst(amount,nightly_rate):
    if nightly_rate<=7500:
        return amount*0.12
    else:
        return amount*0.18

def calculate_total(amount,gst):
    return amount+gst
