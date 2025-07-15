import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from Oel import Car, Bike, Truck, UserDefVehicle, ParkingLot, ParkingManager, ValidationError
import json
from datetime import datetime
import re

# Initialize parking system
lot = ParkingLot(3, 10)
manager = ParkingManager(lot)

class ParkingGUI:
    def __init__(self):
        self.app = tb.Window(themename="darkly")
        self.app.title("Smart Parking Lot Management System")
        self.app.geometry("900x700")
        self.app.iconbitmap("icon.ico")
        
        self.setup_variables()
        self.create_widgets()
        self.update_statistics()
        
    def setup_variables(self):
        self.vehicle_type_var = tk.StringVar(value="Car")
        self.status_var = tk.StringVar()
        self.stats_var = tk.StringVar()
        self.vip_var = tk.BooleanVar()
        
    def create_widgets(self):
        # Header
        self.create_header()
        
        # Statistics panel
        self.create_stats_panel()
        
        # Main input form
        self.create_input_form()
        
        # Buttons
        self.create_buttons()
        
        # Status bar
        self.create_status_bar()
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        header_frame = tb.Frame(self.app, padding=10)
        header_frame.pack(fill="x")
        
        tb.Label(header_frame, text="Smart Parking Lot Management System", 
                font=("Segoe UI", 18, "bold")).pack(pady=10)
        
    def create_stats_panel(self):
        stats_frame = tb.LabelFrame(self.app, text="Parking Statistics", padding=10)
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.stats_label = tb.Label(stats_frame, textvariable=self.stats_var, 
                                   font=("Segoe UI", 10))
        self.stats_label.pack()
        
    def create_input_form(self):
        form_frame = tb.LabelFrame(self.app, text="Vehicle Information", padding=20)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Vehicle type
        tb.Label(form_frame, text="Vehicle Type:", font=("Open Sans", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5)
        
        self.vehicle_type_combo = tb.Combobox(form_frame, textvariable=self.vehicle_type_var, 
                                             values=["Car", "Bike", "Truck", "Custom"], 
                                             state="readonly", width=20)
        self.vehicle_type_combo.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.vehicle_type_combo.bind("<<ComboboxSelected>>", self.toggle_custom_input)
        
        # Custom type (hidden by default)
        self.custom_type_label = tb.Label(form_frame, text="Custom Type:", 
                                         font=("Open Sans", 10, "bold"))
        self.custom_type_entry = tb.Entry(form_frame, width=20)
        
        # Vehicle number
        tb.Label(form_frame, text="Vehicle Number:", font=("Open Sans", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=5)
        
        self.number_entry = tb.Entry(form_frame, width=20)
        self.number_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.number_entry.bind('<KeyRelease>', self.validate_vehicle_number_input)
        
        # Preferred slot
        tb.Label(form_frame, text="Preferred Slot (optional):", 
                font=("Open Sans", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        
        self.preferred_slot_entry = tb.Entry(form_frame, width=20)
        self.preferred_slot_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # VIP checkbox
        self.vip_checkbox = tb.Checkbutton(form_frame, text="VIP Parking", 
                                          variable=self.vip_var)
        self.vip_checkbox.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")
        
    def create_buttons(self):
        btn_frame = tb.Frame(self.app, padding=10)
        btn_frame.pack(fill="x", padx=20)
        
        # Primary buttons
        primary_buttons = [
            ("Park Vehicle", self.park_vehicle, "success"),
            ("Remove Vehicle", self.remove_vehicle, "danger"),
            ("Check Status", self.check_status, "info"),
            ("Show Available Slots", self.show_slots, "primary")
        ]
        
        for i, (text, command, style) in enumerate(primary_buttons):
            btn = tb.Button(btn_frame, text=text, command=command, 
                           bootstyle=style, width=18)
            btn.grid(row=0, column=i, padx=5, pady=5)
        
        # Secondary buttons
        secondary_buttons = [
            ("Show Logs", self.show_logs),
            ("Statistics", self.show_detailed_stats),
            ("Daily Report", self.show_daily_report),
            ("Long Parked", self.show_long_parked)
        ]
        
        for i, (text, command) in enumerate(secondary_buttons):
            btn = tb.Button(btn_frame, text=text, command=command, 
                           bootstyle="secondary", width=18)
            btn.grid(row=1, column=i, padx=5, pady=5)
        
        # Admin buttons
        admin_frame = tb.LabelFrame(self.app, text="Admin Functions", padding=10)
        admin_frame.pack(fill="x", padx=20, pady=10)
        
        admin_buttons = [
            ("Reserve VIP Slot", self.reserve_vip_slot),
            ("Manage Blacklist", self.manage_blacklist),
            ("Queue Status", self.show_queue_status),
            ("Export Data", self.export_data)
        ]
        
        for i, (text, command) in enumerate(admin_buttons):
            btn = tb.Button(admin_frame, text=text, command=command, 
                           bootstyle="warning", width=18)
            btn.grid(row=0, column=i, padx=5, pady=5)
        
    def create_status_bar(self):
        status_frame = tb.Frame(self.app)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        self.status_label = tb.Label(status_frame, textvariable=self.status_var, 
                                    font=("Segoe UI", 10))
        self.status_label.pack(anchor="w")
        
    def create_footer(self):
        footer_frame = tb.Frame(self.app, padding=5)
        footer_frame.pack(fill="x", side="bottom")
        
        tb.Label(footer_frame, text="Developed by Ghulam Murtaza | Enhanced Parking Management System", 
                font=("Segoe UI", 8)).pack()
        
    def toggle_custom_input(self, event=None):
        is_custom = self.vehicle_type_var.get() == "Custom"
        if is_custom:
            self.custom_type_label.grid(row=1, column=0, sticky="w", pady=5)
            self.custom_type_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        else:
            self.custom_type_label.grid_remove()
            self.custom_type_entry.grid_remove()
            
    def validate_vehicle_number_input(self, event=None):
        """Real-time validation of vehicle number input"""
        current_text = self.number_entry.get()
        if current_text:
            # Remove invalid characters and convert to uppercase
            valid_text = re.sub(r'[^A-Z0-9\-]', '', current_text.upper())
            if valid_text != current_text:
                self.number_entry.delete(0, tk.END)
                self.number_entry.insert(0, valid_text)
                
    def get_vehicle(self):
        """Create vehicle object with validation"""
        try:
            number = self.number_entry.get().strip()
            if not number:
                raise ValidationError("Please enter vehicle number")
                
            vtype = self.vehicle_type_var.get()
            
            if vtype == "Car":
                return Car(number)
            elif vtype == "Bike":
                return Bike(number)
            elif vtype == "Truck":
                return Truck(number)
            elif vtype == "Custom":
                custom_type = self.custom_type_entry.get().strip()
                if not custom_type:
                    raise ValidationError("Please enter custom vehicle type")
                return UserDefVehicle(number, custom_type)
            else:
                raise ValidationError("Please select a valid vehicle type")
                
        except ValidationError as e:
            self.show_status(str(e), True)
            return None
            
    def clear_inputs(self):
        """Clear all input fields"""
        self.number_entry.delete(0, tk.END)
        self.custom_type_entry.delete(0, tk.END)
        self.preferred_slot_entry.delete(0, tk.END)
        self.vehicle_type_var.set("Car")
        self.vip_var.set(False)
        self.toggle_custom_input()
        
    def show_status(self, message, is_error=False):
        """Display status message"""
        self.status_var.set(f"{'❌ ' if is_error else '✅ '}{message}")
        self.app.after(5000, lambda: self.status_var.set(""))
        
    def update_statistics(self):
        """Update parking statistics display"""
        try:
            stats = manager.parking_lot.get_parking_statistics()
            queue_status = manager.get_waiting_queue_status()
            
            stats_text = (f"Total Slots: {stats['total_slots']} | "
                         f"Occupied: {stats['occupied_slots']} | "
                         f"Available: {stats['available_slots']} | "
                         f"Occupancy: {stats['occupancy_rate']:.1f}% | "
                         f"Queue: {queue_status['total_waiting']}")
            
            self.stats_var.set(stats_text)
            
            # Schedule next update
            self.app.after(10000, self.update_statistics)
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
            
    def park_vehicle(self):
        """Park a vehicle with enhanced features"""
        vehicle = self.get_vehicle()
        if not vehicle:
            return
            
        try:
            preferred_slot = self.preferred_slot_entry.get().strip() or None
            is_vip = self.vip_var.get()
            
            result = manager.park_vehicle(vehicle, preferred_slot, is_vip)
            
            if result == "queued":
                queue_type = "VIP" if is_vip else "regular"
                self.show_status(f"Parking full. Added to {queue_type} queue.")
            else:
                self.show_status(f"Vehicle {vehicle.vehicle_number} parked in slot {result}")
                
            self.clear_inputs()
            self.update_statistics()
            
        except ValidationError as e:
            self.show_status(str(e), True)
            
    def remove_vehicle(self):
        """Remove a vehicle with receipt generation"""
        number = self.number_entry.get().strip()
        if not number:
            self.show_status("Please enter vehicle number to remove", True)
            return
            
        try:
            receipt = manager.remove_vehicle(number)
            messagebox.showinfo("Parking Receipt", receipt)
            self.show_status(f"Vehicle {number} removed successfully")
            self.clear_inputs()
            self.update_statistics()
            
        except ValidationError as e:
            self.show_status(str(e), True)
            
    def check_status(self):
        """Check vehicle status with detailed information"""
        number = self.number_entry.get().strip()
        if not number:
            self.show_status("Please enter vehicle number to check", True)
            return
            
        try:
            status = manager.check_vehicle_status(number)
            
            if status["found"]:
                info = (f"Vehicle Number: {number}\\n"
                       f"Vehicle Type: {status['vehicle_type']}\\n"
                       f"Slot: {status['slot_id']}\\n"
                       f"Entry Time: {status['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}\\n"
                       f"Duration: {status['duration_hours']} hours\\n"
                       f"Current Fee: ${status['current_fee']:.2f}")
            else:
                info = f"Vehicle {number} not found in parking lot"
                
            messagebox.showinfo("Vehicle Status", info)
            self.show_status(f"Status checked for {number}")
            
        except Exception as e:
            self.show_status(f"Error checking status: {e}", True)
            
        self.clear_inputs()
        
    def show_slots(self):
        """Display available slots"""
        try:
            slots = manager.parking_lot.display_available_slots()
            if slots:
                slots_text = "\\n".join(slots[:20])  # Limit display
                if len(slots) > 20:
                    slots_text += f"\\n... and {len(slots) - 20} more slots"
            else:
                slots_text = "No slots available"
                
            messagebox.showinfo("Available Slots", slots_text)
            self.show_status("Available slots displayed")
            
        except Exception as e:
            self.show_status(f"Error showing slots: {e}", True)
            
    def show_logs(self):
        """Display parking logs"""
        try:
            with open("parking_log.json", "r") as f:
                logs = json.load(f)
                
            if logs:
                # Show last 10 entries
                recent_logs = logs[-10:]
                log_text = "\\n".join([
                    f"{log['vehicle_number']} | {log['vehicle_type']} | "
                    f"${log['fee']:.2f} | {log['exit_time'][:19]}"
                    for log in recent_logs
                ])
                
                if len(logs) > 10:
                    log_text = f"Showing last 10 of {len(logs)} entries:\\n\\n" + log_text
            else:
                log_text = "No parking logs available"
                
            messagebox.showinfo("Parking Logs", log_text)
            self.show_status("Parking logs displayed")
            
        except FileNotFoundError:
            self.show_status("No parking logs found", True)
        except Exception as e:
            self.show_status(f"Error loading logs: {e}", True)
            
    def show_detailed_stats(self):
        """Show detailed parking statistics"""
        try:
            stats = manager.parking_lot.get_parking_statistics()
            
            stats_text = f"""Parking Statistics:
            
Total Slots: {stats['total_slots']}
Occupied Slots: {stats['occupied_slots']}
Available Slots: {stats['available_slots']}
Reserved Slots: {stats['reserved_slots']}
Occupancy Rate: {stats['occupancy_rate']:.1f}%

Vehicle Types Currently Parked:"""
            
            for vtype, count in stats['vehicle_types'].items():
                stats_text += f"\\n- {vtype}: {count}"
                
            if not stats['vehicle_types']:
                stats_text += "\\nNo vehicles currently parked"
                
            messagebox.showinfo("Detailed Statistics", stats_text)
            
        except Exception as e:
            self.show_status(f"Error generating statistics: {e}", True)
            
    def show_daily_report(self):
        """Show daily revenue report"""
        try:
            report = manager.generate_daily_report()
            
            report_text = f"""Daily Report for {report['date']}:
            
Total Vehicles: {report['total_vehicles']}
Total Revenue: ${report['total_revenue']:.2f}
Average Fee: ${report['average_fee']:.2f}

Vehicle Breakdown:"""
            
            for vtype, count in report['vehicle_breakdown'].items():
                report_text += f"\\n- {vtype}: {count}"
                
            messagebox.showinfo("Daily Report", report_text)
            
        except Exception as e:
            self.show_status(f"Error generating report: {e}", True)
            
    def show_long_parked(self):
        """Show vehicles parked for long duration"""
        try:
            hours = simpledialog.askfloat("Long Parked Vehicles", 
                                        "Show vehicles parked for more than how many hours?",
                                        initialvalue=24.0, minvalue=1.0)
            if hours is None:
                return
                
            long_parked = manager.find_long_parked_vehicles(hours)
            
            if long_parked:
                text = f"Vehicles parked for more than {hours} hours:\\n\\n"
                for vehicle in long_parked:
                    text += (f"{vehicle['vehicle_number']} ({vehicle['vehicle_type']}) - "
                           f"Slot {vehicle['slot_id']} - {vehicle['duration_hours']:.1f}h\\n")
            else:
                text = f"No vehicles parked for more than {hours} hours"
                
            messagebox.showinfo("Long Parked Vehicles", text)
            
        except Exception as e:
            self.show_status(f"Error finding long parked vehicles: {e}", True)
            
    def show_queue_status(self):
        """Show waiting queue status"""
        try:
            queue_status = manager.get_waiting_queue_status()
            
            status_text = f"""Waiting Queue Status:
            
VIP Queue: {queue_status['vip_queue']} vehicles
Regular Queue: {queue_status['regular_queue']} vehicles
Total Waiting: {queue_status['total_waiting']} vehicles"""
            
            messagebox.showinfo("Queue Status", status_text)
            
        except Exception as e:
            self.show_status(f"Error getting queue status: {e}", True)
            
    def reserve_vip_slot(self):
        """Reserve a slot for VIP parking"""
        slot_id = simpledialog.askstring("Reserve VIP Slot", "Enter slot ID to reserve:")
        if slot_id:
            try:
                result = manager.reserve_slot_for_vip(slot_id.upper())
                self.show_status(result)
                self.update_statistics()
            except Exception as e:
                self.show_status(f"Error reserving slot: {e}", True)
                
    def manage_blacklist(self):
        """Manage blacklisted vehicles"""
        action = messagebox.askyesnocancel("Manage Blacklist", 
                                          "Yes = Add to blacklist\\nNo = Remove from blacklist\\nCancel = View blacklist")
        
        if action is None:  # View blacklist
            try:
                blacklisted = list(manager._blacklisted_vehicles)
                if blacklisted:
                    text = "Blacklisted Vehicles:\\n\\n" + "\\n".join(blacklisted)
                else:
                    text = "No vehicles in blacklist"
                messagebox.showinfo("Blacklist", text)
            except Exception as e:
                self.show_status(f"Error viewing blacklist: {e}", True)
        else:
            vehicle_number = simpledialog.askstring("Vehicle Number", "Enter vehicle number:")
            if vehicle_number:
                try:
                    if action:  # Add to blacklist
                        manager.add_to_blacklist(vehicle_number)
                        self.show_status(f"Added {vehicle_number} to blacklist")
                    else:  # Remove from blacklist
                        manager.remove_from_blacklist(vehicle_number)
                        self.show_status(f"Removed {vehicle_number} from blacklist")
                except Exception as e:
                    self.show_status(f"Error managing blacklist: {e}", True)
                    
    def export_data(self):
        """Export parking data"""
        try:
            from datetime import datetime
            export_data = {
                "export_time": datetime.now().isoformat(),
                "statistics": manager.parking_lot.get_parking_statistics(),
                "queue_status": manager.get_waiting_queue_status(),
                "blacklisted_vehicles": list(manager._blacklisted_vehicles)
            }
            
            filename = f"parking_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)
                
            self.show_status(f"Data exported to {filename}")
            
        except Exception as e:
            self.show_status(f"Error exporting data: {e}", True)
            
    def run(self):
        """Start the application"""
        self.toggle_custom_input()
        self.app.mainloop()

def main():
    try:
        gui = ParkingGUI()
        gui.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

main()
