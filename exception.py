class HotelError(Exception):
    pass

class InvalidRoomError(HotelError):
    pass

class RoomNotAvailableError(HotelError):
    pass

class InvalidGuestError(HotelError):
    pass

class BookingNotFoundError(HotelError):
    pass

class BookingStatusError(HotelError):
    pass

class InvalidDateError(HotelError):
    pass

class DatabaseOperationError(HotelError):
    pass

class InvalidRoomDataError(HotelError):
    pass