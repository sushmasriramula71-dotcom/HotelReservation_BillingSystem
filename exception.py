class HotelError(Exception):
    pass

class InvalidRoomError(HotelError):
    pass

class RoomNotAvailableError(HotelError):
    pass

class InvalidGuestError(HotelError):
    pass

class BookingStatusError(HotelError):
    pass