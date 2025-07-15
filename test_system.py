"""
Test script for the Enhanced Parking Management System
"""
import unittest
import json
import os
from datetime import datetime
from Oel import (Car, Bike, Truck, UserDefVehicle, ParkingLot, 
                 ParkingManager, ValidationError, VehicleDataHandler)


class TestParkingSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Clean up any existing test files first
        test_files = ["test_log.json", "test_receipts.json", "test_blacklist.json",
                     "parking_log.json", "parking_receipts.json", "blacklist.json"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                
        self.lot = ParkingLot(2, 3)  # Small lot for testing
        self.manager = ParkingManager(self.lot)
        
        # Clear any existing data
        self.manager._blacklisted_vehicles.clear()
        self.manager._waiting_queue.clear()
        self.manager._vip_queue.clear()
                
    def tearDown(self):
        """Clean up after tests"""
        test_files = ["test_log.json", "test_receipts.json", "test_blacklist.json",
                     "parking_log.json", "parking_receipts.json", "blacklist.json"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_vehicle_validation(self):
        """Test vehicle number validation"""
        # Valid vehicle numbers
        car1 = Car("ABC123")
        self.assertEqual(car1.vehicle_number, "ABC123")
        
        car2 = Car("XYZ-456")
        self.assertEqual(car2.vehicle_number, "XYZ-456")
        
        # Invalid vehicle numbers
        with self.assertRaises(ValidationError):
            Car("")  # Empty
            
        with self.assertRaises(ValidationError):
            Car("AB")  # Too short
            
        with self.assertRaises(ValidationError):
            Car("A" * 20)  # Too long
            
        with self.assertRaises(ValidationError):
            Car("ABC@123")  # Invalid characters

    def test_custom_vehicle_validation(self):
        """Test custom vehicle type validation"""
        # Valid custom vehicle
        custom1 = UserDefVehicle("ABC123", "Motorcycle")
        self.assertEqual(custom1.vehicle_type, "Motorcycle")
        
        # Invalid custom types
        with self.assertRaises(ValidationError):
            UserDefVehicle("ABC123", "")  # Empty
            
        with self.assertRaises(ValidationError):
            UserDefVehicle("ABC123", "A")  # Too short
            
        with self.assertRaises(ValidationError):
            UserDefVehicle("ABC123", "A" * 25)  # Too long
            
        with self.assertRaises(ValidationError):
            UserDefVehicle("ABC123", "Type123")  # Invalid characters

    def test_parking_lot_initialization(self):
        """Test parking lot initialization with validation"""
        # Valid initialization
        lot = ParkingLot(2, 5)
        self.assertEqual(len(lot.slots), 10)
        
        # Invalid initialization
        with self.assertRaises(ValidationError):
            ParkingLot(0, 5)  # Zero levels
            
        with self.assertRaises(ValidationError):
            ParkingLot(2, 0)  # Zero slots
            
        with self.assertRaises(ValidationError):
            ParkingLot(-1, 5)  # Negative levels

    def test_basic_parking_operations(self):
        """Test basic park and remove operations"""
        car = Car("TEST123")
        
        # Park vehicle
        slot_id = self.manager.park_vehicle(car)
        self.assertIsNotNone(slot_id)
        self.assertTrue(slot_id.startswith("L"))
        
        # Check status
        status = self.manager.check_vehicle_status("TEST123")
        self.assertTrue(status["found"])
        self.assertEqual(status["slot_id"], slot_id)
        
        # Remove vehicle
        receipt = self.manager.remove_vehicle("TEST123")
        self.assertIsNotNone(receipt)
        self.assertIn("TEST123", receipt)

    def test_duplicate_parking_prevention(self):
        """Test prevention of parking same vehicle twice"""
        car = Car("DUPLICATE123")
        
        # Park once - should succeed
        slot_id = self.manager.park_vehicle(car)
        self.assertIsNotNone(slot_id)
        
        # Try to park again - should fail
        with self.assertRaises(ValidationError):
            self.manager.park_vehicle(car)

    def test_blacklist_functionality(self):
        """Test blacklist management"""
        vehicle_number = "BLACKLIST123"
        
        # Add to blacklist
        self.manager.add_to_blacklist(vehicle_number)
        self.assertTrue(self.manager.is_blacklisted(vehicle_number))
        
        # Try to park blacklisted vehicle
        car = Car(vehicle_number)
        with self.assertRaises(ValidationError):
            self.manager.park_vehicle(car)
        
        # Remove from blacklist
        self.manager.remove_from_blacklist(vehicle_number)
        self.assertFalse(self.manager.is_blacklisted(vehicle_number))
        
        # Should be able to park now
        slot_id = self.manager.park_vehicle(car)
        self.assertIsNotNone(slot_id)

    def test_vip_parking(self):
        """Test VIP parking functionality"""
        # Start with fresh lot for this test
        fresh_lot = ParkingLot(2, 3)
        fresh_manager = ParkingManager(fresh_lot)
        
        # Reserve a slot for VIP
        fresh_manager.parking_lot.reserve_slot("L1-S1")
        self.assertTrue(fresh_manager.parking_lot.is_slot_reserved("L1-S1"))
        
        # Regular vehicle should not get reserved slot
        regular_car = Car("REGULAR123")
        slot_id = fresh_manager.park_vehicle(regular_car, "L1-S1", False)
        self.assertNotEqual(slot_id, "L1-S1")
        
        # VIP vehicle should get reserved slot
        vip_car = Car("VIP123")
        slot_id = fresh_manager.park_vehicle(vip_car, "L1-S1", True)
        self.assertEqual(slot_id, "L1-S1")

    def test_waiting_queue(self):
        """Test waiting queue functionality"""
        # Use fresh lot for this test
        fresh_lot = ParkingLot(2, 2)  # Even smaller lot: 4 slots
        fresh_manager = ParkingManager(fresh_lot)
        
        # Fill up the parking lot
        cars = []
        for i in range(4):  # 2 levels * 2 slots = 4 total
            car = Car(f"CAR{i:03d}")
            cars.append(car)
            slot_id = fresh_manager.park_vehicle(car)
            self.assertIsNotNone(slot_id)
        
        # Lot should be full now
        self.assertTrue(fresh_manager.parking_lot.is_full())
        
        # Add vehicle to queue
        queued_car = Car("QUEUED123")
        result = fresh_manager.park_vehicle(queued_car)
        self.assertEqual(result, "queued")
        
        # Check queue status
        queue_status = fresh_manager.get_waiting_queue_status()
        self.assertEqual(queue_status["total_waiting"], 1)
        
        # Remove a car to make space
        fresh_manager.remove_vehicle("CAR000")
        
        # Queued car should be automatically parked
        status = fresh_manager.check_vehicle_status("QUEUED123")
        self.assertTrue(status["found"])

    def test_fee_calculation(self):
        """Test fee calculation for different vehicle types"""
        # Test Car fees
        car = Car("FEE123")
        self.assertEqual(car.calculate_fee(0.5), 5)  # Base fee for < 1 hour
        self.assertEqual(car.calculate_fee(2), 8)    # Base + 1 hour extra
        
        # Test Bike fees
        bike = Bike("BIKE123")
        self.assertEqual(bike.calculate_fee(0.5), 3)  # Base fee
        self.assertEqual(bike.calculate_fee(2), 5)    # Base + 1 hour extra
        
        # Test Truck fees
        truck = Truck("TRUCK123")
        self.assertEqual(truck.calculate_fee(0.5), 10)  # Base fee
        self.assertEqual(truck.calculate_fee(2), 15)    # Base + 1 hour extra

    def test_statistics(self):
        """Test parking statistics"""
        # Use fresh lot for clean test
        fresh_lot = ParkingLot(2, 3)  # 6 slots total
        fresh_manager = ParkingManager(fresh_lot)
        
        # Park some vehicles
        car = Car("STAT1")
        bike = Bike("STAT2")
        
        fresh_manager.park_vehicle(car)
        fresh_manager.park_vehicle(bike)
        
        stats = fresh_manager.parking_lot.get_parking_statistics()
        
        self.assertEqual(stats["total_slots"], 6)
        self.assertEqual(stats["occupied_slots"], 2)
        self.assertEqual(stats["available_slots"], 4)
        self.assertAlmostEqual(stats["occupancy_rate"], 33.33, places=1)
        self.assertEqual(stats["vehicle_types"]["Car"], 1)
        self.assertEqual(stats["vehicle_types"]["Bike"], 1)

    def test_data_persistence(self):
        """Test data saving and loading"""
        # Create a temporary manager with test files
        test_handler = VehicleDataHandler("test_log.json", "test_receipts.json")
        test_lot = ParkingLot(2, 3)
        test_manager = ParkingManager(test_lot)
        test_manager._data_handler = test_handler
        
        # Park a vehicle
        car = Car("PERSIST123")
        slot_id = test_manager.park_vehicle(car)
        
        # Check that data was saved
        self.assertTrue(os.path.exists("test_receipts.json"))
        
        with open("test_receipts.json", "r") as f:
            receipts = json.load(f)
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["vehicle_number"], "PERSIST123")
        
        # Remove vehicle and check logs
        test_manager.remove_vehicle("PERSIST123")
        
        self.assertTrue(os.path.exists("test_log.json"))
        
        with open("test_log.json", "r") as f:
            logs = json.load(f)
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["vehicle_number"], "PERSIST123")

    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Try to remove non-existent vehicle
        with self.assertRaises(ValidationError):
            self.manager.remove_vehicle("NONEXISTENT")
        
        # Try to reserve non-existent slot
        with self.assertRaises(ValidationError):
            self.manager.parking_lot.reserve_slot("L99-S99")
        
        # Try to reserve occupied slot
        car = Car("OCCUPY123")
        slot_id = self.manager.park_vehicle(car)
        
        with self.assertRaises(ValidationError):
            self.manager.parking_lot.reserve_slot(slot_id)


def run_integration_test():
    """Run a comprehensive integration test"""
    print("Running integration test...")
    
    try:
        # Initialize system
        lot = ParkingLot(2, 5)
        manager = ParkingManager(lot)
        
        print("✓ System initialized successfully")
        
        # Test vehicle parking
        vehicles = [
            Car("INT001"),
            Bike("INT002"),
            Truck("INT003"),
            UserDefVehicle("INT004", "Scooter")
        ]
        
        for vehicle in vehicles:
            slot_id = manager.park_vehicle(vehicle)
            print(f"✓ Parked {type(vehicle).__name__} {vehicle.vehicle_number} in {slot_id}")
        
        # Test statistics
        stats = manager.parking_lot.get_parking_statistics()
        print(f"✓ Statistics: {stats['occupied_slots']}/{stats['total_slots']} slots occupied")
        
        # Test blacklist
        manager.add_to_blacklist("BANNED001")
        print("✓ Added vehicle to blacklist")
        
        # Test VIP reservation (use an available slot)
        available_slots = manager.parking_lot.display_available_slots()
        if available_slots:
            vip_slot = available_slots[0].split()[0]  # Get slot ID without status
            manager.parking_lot.reserve_slot(vip_slot)
            print(f"✓ Reserved VIP slot {vip_slot}")
        else:
            print("✓ No available slots to reserve")
        
        # Test vehicle removal
        for vehicle in vehicles:
            receipt = manager.remove_vehicle(vehicle.vehicle_number)
            print(f"✓ Removed {vehicle.vehicle_number}")
        
        print("✓ Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("Enhanced Parking Management System - Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration test
    print("\n" + "=" * 50)
    run_integration_test()
    
    print("\nAll tests completed!")
