from abc import ABC , abstractmethod
class Room(ABC):
    def __init__(self,room_no,floor):
        self.room_no=room_no
        self.floor=floor

    @abstractmethod
    def get_rate(self):
        pass

    @abstractmethod
    def get_max_guests(self):
        pass

    @abstractmethod
    def get_breakfast_charge(self):
        pass

    @abstractmethod
    def get_extra_guest_charge(self,guests):
        pass

        
class StandardRoom(Room):
    def __init__(self, room_no, floor):
        super().__init__(room_no, floor)

    def get_rate(self):
        return 2500
    
    def get_max_guests(self):
        return 2

    def get_breakfast_charge(self):
        return 350

    def get_extra_guest_charge(self, guests):
        return 0

class DeluxeRoom(Room):
    def __init__(self, room_no, floor):
        super().__init__(room_no, floor)

    def get_rate(self):
        return 4000

    def get_max_guests(self):
        return 3

    def get_breakfast_charge(self):
        return 0

    def get_extra_guest_charge(self, guests):
        return max(0,guests-2)*800

class SuiteRoom(Room):
    def __init__(self, room_no, floor):
        super().__init__(room_no, floor)

    def get_rate(self):
        return 7500
    def get_max_guests(self):
        return 4
    def get_breakfast_charge(self):
        return 0
    def get_extra_guest_charge(self, guests):
        return max(0,guests-2)*800
    