from typing import Optional
import os
import json
import re
from datetime import datetime, timedelta
from collections import deque  


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Vehicle:
    def __init__(self, vehicle_number):
        self.vehicle_number = self.validate_vehicle_number(str(vehicle_number))
        self.entry_time = datetime.now()

    @staticmethod
    def validate_vehicle_number(vehicle_number):
        """Validate vehicle number format"""
        if not vehicle_number or not vehicle_number.strip():
            raise ValidationError("Vehicle number cannot be empty")
        
        vehicle_number = vehicle_number.strip().upper()
        
        # Check length
        if len(vehicle_number) < 3 or len(vehicle_number) > 15:
            raise ValidationError("Vehicle number must be between 3-15 characters")
        
        # Check for valid characters (alphanumeric and hyphens)
        if not re.match(r'^[A-Z0-9\-]+$', vehicle_number):
            raise ValidationError("Vehicle number can only contain letters, numbers, and hyphens")
        
        return vehicle_number

    def calculate_fee(self, duration_in_hours):
        """Calculate parking fee based on duration - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement calculate_fee method")

    def get_vehicle_info(self):
        """Get basic vehicle information"""
        return {
            "number": self.vehicle_number,
            "type": self.__class__.__name__,
            "entry_time": self.entry_time.isoformat()
        }

class Car(Vehicle):
    def calculate_fee(self, duration_in_hours: float):
        if duration_in_hours <= 1:
            return 5 
        else:
            return 5 + (duration_in_hours - 1) * 3

class Bike(Vehicle):
    def calculate_fee(self, duration_in_hours: float):
        if duration_in_hours <= 1:
            return 3
        else:
            return  3 + (duration_in_hours - 1) * 2

class Truck(Vehicle):
    def calculate_fee(self, duration_in_hours: float):
        if duration_in_hours <= 1:
            return 10
        else:
            return 10 + (duration_in_hours - 1) * 5

class UserDefVehicle(Vehicle):
    def __init__(self, vehicle_number: str, vehicle_type: str):
        super().__init__(vehicle_number)
        self.vehicle_type = self.validate_vehicle_type(str(vehicle_type))
        self.fee = 15

    @staticmethod
    def validate_vehicle_type(vehicle_type):
        """Validate custom vehicle type"""
        if not vehicle_type or not vehicle_type.strip():
            raise ValidationError("Custom vehicle type cannot be empty")
        
        vehicle_type = vehicle_type.strip()
        
        if len(vehicle_type) < 2 or len(vehicle_type) > 20:
            raise ValidationError("Vehicle type must be between 2-20 characters")
        
        if not re.match(r'^[A-Za-z\s]+$', vehicle_type):
            raise ValidationError("Vehicle type can only contain letters and spaces")
        
        return vehicle_type.title()

    def calculate_fee(self, duration_in_hours: float):
        if duration_in_hours <= 1:
            return self.fee
        else:
            return self.fee + (duration_in_hours - 1) * 8

class VehicleDataHandler:
    def __init__(self, log_file="parking_log.json", receipt_file="parking_receipts.json"):
        self.log_file = log_file
        self.receipt_file = receipt_file
        self.ensure_files_exist()

    def ensure_files_exist(self):
        for file in [self.log_file, self.receipt_file]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump([], f, indent=2)

    def read_file(self, file):
        with open(file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def write_file(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=2)

    def log_entry(self, entry):
        data = self.read_file(self.receipt_file)
        data.append(entry)
        self.write_file(self.receipt_file, data)

    def log_exit(self, exit_data):
        receipts = self.read_file(self.receipt_file)
        receipts = [r for r in receipts if r["vehicle_number"] != exit_data["vehicle_number"]]
        self.write_file(self.receipt_file, receipts)

        logs = self.read_file(self.log_file)
        logs.append(exit_data)
        self.write_file(self.log_file, logs)

class ParkingSlot:
    def __init__(self, slot_id: str, is_occupied: bool = False, vehicle: Optional[Vehicle] = None):
        self.slot_id = str(slot_id)
        self.is_occupied = is_occupied
        self.vehicle = vehicle

    def assign_vehicle(self, vehicle):
        if not self.is_occupied:
            self.is_occupied = True
            self.vehicle = vehicle
        else:
            raise Exception("Slot is already occupied")

    def free_slot(self):
        if self.is_occupied:
            self.is_occupied = False
            self.vehicle = None
        else:
            raise Exception("Slot is already free")

    def is_available(self):
        return not self.is_occupied

class ParkingLot:
    def __init__(self, total_levels: int, slots_per_level: int):
        self._total_levels = self.validate_positive_integer(total_levels, "total levels")
        self._slots_per_level = self.validate_positive_integer(slots_per_level, "slots per level")
        self.slots = {}
        self._reserved_slots = set()  # For VIP parking
        for level in range(self._total_levels):
            for slot in range(self._slots_per_level):
                slot_id = f"L{level+1}-S{slot+1}"
                self.slots[slot_id] = ParkingSlot(slot_id)

    @staticmethod
    def validate_positive_integer(value, field_name):
        """Validate that a value is a positive integer"""
        try:
            value = int(value)
            if value <= 0:
                raise ValidationError(f"{field_name} must be a positive integer")
            return value
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer")

    def reserve_slot(self, slot_id: str):
        """Reserve a slot for VIP parking"""
        if slot_id not in self.slots:
            raise ValidationError(f"Slot {slot_id} does not exist")
        if not self.slots[slot_id].is_available():
            raise ValidationError(f"Slot {slot_id} is currently occupied")
        self._reserved_slots.add(slot_id)

    def unreserve_slot(self, slot_id: str):
        """Remove reservation from a slot"""
        self._reserved_slots.discard(slot_id)

    def is_slot_reserved(self, slot_id: str):
        """Check if a slot is reserved"""
        return slot_id in self._reserved_slots

    def park_vehicle(self, vehicle, preferred_slot=None, is_vip=False):
        """Park a vehicle with optional preferred slot or VIP parking"""
        # Check if vehicle is already parked
        for slot in self.slots.values():
            if slot.is_occupied and slot.vehicle.vehicle_number == vehicle.vehicle_number:
                raise ValidationError(f"Vehicle {vehicle.vehicle_number} is already parked")

        # Try preferred slot first
        if preferred_slot and preferred_slot in self.slots:
            slot = self.slots[preferred_slot]
            if slot.is_available() and (is_vip or not self.is_slot_reserved(preferred_slot)):
                slot.assign_vehicle(vehicle)
                return preferred_slot

        # Find any available slot
        for slot_id, slot in self.slots.items():
            if slot.is_available():
                # Skip reserved slots unless VIP
                if self.is_slot_reserved(slot_id) and not is_vip:
                    continue
                slot.assign_vehicle(vehicle)
                return slot_id
        return None

    def remove_vehicle(self, vehicle_number):
        for slot_id, slot in self.slots.items():
            if slot.is_occupied and slot.vehicle.vehicle_number == vehicle_number:
                slot.free_slot()
                return slot_id
        return None

    def display_available_slots(self):
        available = []
        for slot_id, slot in self.slots.items():
            if slot.is_available():
                status = " (Reserved)" if self.is_slot_reserved(slot_id) else ""
                available.append(f"{slot_id}{status}")
        return available

    def get_parking_statistics(self):
        """Get detailed parking statistics"""
        total_slots = len(self.slots)
        occupied_slots = sum(1 for slot in self.slots.values() if slot.is_occupied)
        available_slots = total_slots - occupied_slots
        reserved_slots = len(self._reserved_slots)
        
        vehicle_types = {}
        for slot in self.slots.values():
            if slot.is_occupied:
                vtype = type(slot.vehicle).__name__
                vehicle_types[vtype] = vehicle_types.get(vtype, 0) + 1

        return {
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "available_slots": available_slots,
            "reserved_slots": reserved_slots,
            "occupancy_rate": (occupied_slots / total_slots) * 100,
            "vehicle_types": vehicle_types
        }

    def is_full(self):
        return all(not slot.is_available() for slot in self.slots.values())

    def get_vehicle_status(self, vehicle_number):  
        for slot_id, slot in self.slots.items():
            if slot.is_occupied and slot.vehicle.vehicle_number == vehicle_number:
                return slot_id, slot.vehicle.entry_time
        return None, None

    def find_vehicles_by_type(self, vehicle_type):
        """Find all vehicles of a specific type"""
        vehicles = []
        for slot_id, slot in self.slots.items():
            if slot.is_occupied and type(slot.vehicle).__name__ == vehicle_type:
                vehicles.append({
                    "slot_id": slot_id,
                    "vehicle_number": slot.vehicle.vehicle_number,
                    "entry_time": slot.vehicle.entry_time
                })
        return vehicles

class ParkingManager:
    def __init__(self, parking_lot):
        self.parking_lot = parking_lot
        self._data_handler = VehicleDataHandler()
        self._waiting_queue = deque()
        self._vip_queue = deque()  # Separate queue for VIP customers
        self._blacklisted_vehicles = set()  # Track problematic vehicles
        self.load_parked_vehicles()
        self.load_blacklist()

    def load_blacklist(self):
        """Load blacklisted vehicles from file"""
        try:
            with open("blacklist.json", "r") as f:
                blacklist_data = json.load(f)
                self._blacklisted_vehicles = set(blacklist_data.get("vehicles", []))
        except (FileNotFoundError, json.JSONDecodeError):
            self._blacklisted_vehicles = set()

    def save_blacklist(self):
        """Save blacklisted vehicles to file"""
        with open("blacklist.json", "w") as f:
            json.dump({"vehicles": list(self._blacklisted_vehicles)}, f, indent=2)

    def add_to_blacklist(self, vehicle_number):
        """Add a vehicle to blacklist"""
        self._blacklisted_vehicles.add(vehicle_number.upper())
        self.save_blacklist()

    def remove_from_blacklist(self, vehicle_number):
        """Remove a vehicle from blacklist"""
        self._blacklisted_vehicles.discard(vehicle_number.upper())
        self.save_blacklist()

    def is_blacklisted(self, vehicle_number):
        """Check if a vehicle is blacklisted"""
        return vehicle_number.upper() in self._blacklisted_vehicles

    def load_parked_vehicles(self):  
        receipts = self._data_handler.read_file(self._data_handler.receipt_file)
        for entry in receipts:
            try:
                vehicle_number = entry["vehicle_number"]
                vehicle_type = entry["vehicle_type"]
                entry_time = datetime.fromisoformat(entry["entry_time"])
                slot_id = entry["slot"]

                if vehicle_type == "Car":
                    vehicle = Car(vehicle_number)
                elif vehicle_type == "Bike":
                    vehicle = Bike(vehicle_number)
                elif vehicle_type == "Truck":
                    vehicle = Truck(vehicle_number)
                elif vehicle_type == "UserDefVehicle":
                    vehicle = UserDefVehicle(vehicle_number, entry.get("custom_type", "Custom"))
                else:
                    continue

                vehicle.entry_time = entry_time

                if slot_id in self.parking_lot.slots:
                    self.parking_lot.slots[slot_id].assign_vehicle(vehicle)
            except (KeyError, ValueError, ValidationError) as e:
                print(f"Error loading vehicle data: {e}")

    def park_vehicle(self, vehicle, preferred_slot=None, is_vip=False):
        """Enhanced park vehicle with validation and features"""
        try:
            # Check blacklist
            if self.is_blacklisted(vehicle.vehicle_number):
                raise ValidationError(f"Vehicle {vehicle.vehicle_number} is blacklisted and cannot park")

            if self.parking_lot.is_full():
                print("Lot full. Adding to queue.")
                if is_vip:
                    self._vip_queue.append(vehicle)
                else:
                    self._waiting_queue.append(vehicle)
                return "queued"

            slot_id = self.parking_lot.park_vehicle(vehicle, preferred_slot, is_vip)
            if slot_id:
                print(f"Vehicle {vehicle.vehicle_number} parked in slot {slot_id}.")
                self._data_handler.log_entry({
                    "vehicle_number": vehicle.vehicle_number,
                    "vehicle_type": type(vehicle).__name__,
                    "custom_type": getattr(vehicle, 'vehicle_type', None),
                    "entry_time": vehicle.entry_time.isoformat(),
                    "slot": slot_id,
                    "is_vip": is_vip,
                    "status": "entered"
                })
                return slot_id
            else:
                raise ValidationError("No suitable parking slot available")
        except ValidationError as e:
            print(f"Parking failed: {e}")
            raise

    def remove_vehicle(self, vehicle_number):
        """Enhanced remove vehicle with better error handling"""
        try:
            slot_id, entry_time = self.parking_lot.get_vehicle_status(vehicle_number)
            if not slot_id:
                raise ValidationError("Vehicle not found in parking lot")

            slot = self.parking_lot.slots[slot_id]
            vehicle = slot.vehicle
            exit_time = datetime.now()
            duration = (exit_time - entry_time).total_seconds() / 3600 if entry_time else 0
            fee = vehicle.calculate_fee(duration)

            slot.free_slot()  

            receipt = self.generate_fee_receipt(
                vehicle_number=vehicle.vehicle_number,
                vehicle_type=type(vehicle).__name__,
                slot_id=slot_id,
                entry_time=entry_time,
                exit_time=exit_time,
                duration=duration,
                fee=fee
            )

            self._data_handler.log_exit({
                "vehicle_number": vehicle.vehicle_number,
                "vehicle_type": type(vehicle).__name__,
                "slot": slot_id,
                "entry_time": entry_time.isoformat() if entry_time else "",
                "exit_time": exit_time.isoformat(),
                "duration_hours": round(duration, 2),
                "fee": round(fee, 2),
                "status": "exited"
            })

            # Process waiting queue (VIP first)
            if self._vip_queue:
                next_vehicle = self._vip_queue.popleft()
                try:
                    self.park_vehicle(next_vehicle, slot_id, True)
                except ValidationError:
                    # If parking fails, put back in queue
                    self._vip_queue.appendleft(next_vehicle)
            elif self._waiting_queue:
                next_vehicle = self._waiting_queue.popleft()
                try:
                    self.park_vehicle(next_vehicle, slot_id, False)
                except ValidationError:
                    # If parking fails, put back in queue
                    self._waiting_queue.appendleft(next_vehicle)

            return receipt

        except ValidationError as e:
            print(f"Remove vehicle failed: {e}")
            raise

    def get_waiting_queue_status(self):
        """Get status of waiting queues"""
        return {
            "vip_queue": len(self._vip_queue),
            "regular_queue": len(self._waiting_queue),
            "total_waiting": len(self._vip_queue) + len(self._waiting_queue)
        }

    def generate_daily_report(self, date=None):
        """Generate daily parking report"""
        if date is None:
            date = datetime.now().date()
        
        logs = self._data_handler.read_file(self._data_handler.log_file)
        daily_logs = [
            log for log in logs 
            if datetime.fromisoformat(log["exit_time"]).date() == date
        ]
        
        total_revenue = sum(log["fee"] for log in daily_logs)
        total_vehicles = len(daily_logs)
        
        vehicle_types = {}
        for log in daily_logs:
            vtype = log["vehicle_type"]
            vehicle_types[vtype] = vehicle_types.get(vtype, 0) + 1
        
        return {
            "date": date.isoformat(),
            "total_vehicles": total_vehicles,
            "total_revenue": round(total_revenue, 2),
            "vehicle_breakdown": vehicle_types,
            "average_fee": round(total_revenue / total_vehicles, 2) if total_vehicles > 0 else 0
        }

    def find_long_parked_vehicles(self, hours_threshold=24):
        """Find vehicles parked for more than specified hours"""
        current_time = datetime.now()
        long_parked = []
        
        for slot_id, slot in self.parking_lot.slots.items():
            if slot.is_occupied:
                duration = (current_time - slot.vehicle.entry_time).total_seconds() / 3600
                if duration > hours_threshold:
                    long_parked.append({
                        "slot_id": slot_id,
                        "vehicle_number": slot.vehicle.vehicle_number,
                        "vehicle_type": type(slot.vehicle).__name__,
                        "duration_hours": round(duration, 2),
                        "entry_time": slot.vehicle.entry_time
                    })
        
        return long_parked

    def generate_fee_receipt(self, vehicle_number, vehicle_type, slot_id, entry_time, exit_time, duration, fee):
        receipt_str = (
            f"===== Parking Fee Receipt =====\n"
            f"Vehicle Number : {vehicle_number}\n"
            f"Vehicle Type   : {vehicle_type}\n"
            f"Slot           : {slot_id}\n"
            f"Entry Time     : {entry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Exit Time      : {exit_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Duration       : {duration:.2f} hours\n"
            f"Fee            : ${fee:.2f}\n"
            f"Thank you for using our parking service!\n"
            f"================================"
        )
        return receipt_str

    def check_vehicle_status(self, vehicle_number):
        slot_id, entry_time = self.parking_lot.get_vehicle_status(vehicle_number)
        if slot_id:
            duration = (datetime.now() - entry_time).total_seconds() / 3600
            vehicle = self.parking_lot.slots[slot_id].vehicle
            current_fee = vehicle.calculate_fee(duration)
            
            return {
                "found": True,
                "slot_id": slot_id,
                "entry_time": entry_time,
                "duration_hours": round(duration, 2),
                "current_fee": round(current_fee, 2),
                "vehicle_type": type(vehicle).__name__
            }
        else:
            return {"found": False}

    def reserve_slot_for_vip(self, slot_id):
        """Reserve a slot for VIP parking"""
        try:
            self.parking_lot.reserve_slot(slot_id)
            return f"Slot {slot_id} reserved for VIP parking"
        except ValidationError as e:
            return str(e)

