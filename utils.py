"""
Utility functions for parking management system
"""
import json
import os
from datetime import datetime, timedelta
import csv


class ParkingUtils:
    def __init__(self, log_file="parking_log.json", receipt_file="parking_receipts.json"):
        self.log_file = log_file
        self.receipt_file = receipt_file

    def backup_data(self, backup_dir="backups"):
        """Create backup of all data files"""
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files_to_backup = [
            self.log_file,
            self.receipt_file,
            "blacklist.json",
            "config.json"
        ]
        
        backup_files = []
        for file in files_to_backup:
            if os.path.exists(file):
                backup_name = f"{backup_dir}/{timestamp}_{file}"
                with open(file, 'r') as src, open(backup_name, 'w') as dst:
                    dst.write(src.read())
                backup_files.append(backup_name)
        
        return backup_files

    def export_to_csv(self, output_file="parking_data.csv"):
        """Export parking logs to CSV format"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            if not logs:
                return False
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = logs[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(logs)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def generate_monthly_report(self, year, month):
        """Generate monthly revenue and usage report"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            monthly_logs = []
            for log in logs:
                exit_date = datetime.fromisoformat(log["exit_time"])
                if exit_date.year == year and exit_date.month == month:
                    monthly_logs.append(log)
            
            if not monthly_logs:
                return None
            
            total_revenue = sum(log["fee"] for log in monthly_logs)
            total_vehicles = len(monthly_logs)
            
            vehicle_types = {}
            daily_revenue = {}
            
            for log in monthly_logs:
                # Vehicle type breakdown
                vtype = log["vehicle_type"]
                vehicle_types[vtype] = vehicle_types.get(vtype, 0) + 1
                
                # Daily revenue
                day = datetime.fromisoformat(log["exit_time"]).date()
                daily_revenue[day.isoformat()] = daily_revenue.get(day.isoformat(), 0) + log["fee"]
            
            return {
                "year": year,
                "month": month,
                "total_vehicles": total_vehicles,
                "total_revenue": round(total_revenue, 2),
                "average_fee": round(total_revenue / total_vehicles, 2),
                "vehicle_breakdown": vehicle_types,
                "daily_revenue": daily_revenue,
                "peak_day": max(daily_revenue.items(), key=lambda x: x[1]) if daily_revenue else None
            }
            
        except Exception as e:
            print(f"Error generating monthly report: {e}")
            return None

    def clean_old_logs(self, days_to_keep=30):
        """Remove logs older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            filtered_logs = []
            removed_count = 0
            
            for log in logs:
                exit_date = datetime.fromisoformat(log["exit_time"])
                if exit_date > cutoff_date:
                    filtered_logs.append(log)
                else:
                    removed_count += 1
            
            with open(self.log_file, 'w') as f:
                json.dump(filtered_logs, f, indent=2)
            
            return removed_count
            
        except Exception as e:
            print(f"Error cleaning old logs: {e}")
            return 0

    def validate_data_integrity(self):
        """Check data integrity and report issues"""
        issues = []
        
        # Check log file
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            required_fields = ["vehicle_number", "vehicle_type", "entry_time", "exit_time", "fee"]
            for i, log in enumerate(logs):
                for field in required_fields:
                    if field not in log:
                        issues.append(f"Log entry {i}: Missing field '{field}'")
                    elif log[field] is None or log[field] == "":
                        issues.append(f"Log entry {i}: Empty field '{field}'")
                        
        except Exception as e:
            issues.append(f"Error reading log file: {e}")
        
        # Check receipt file
        try:
            with open(self.receipt_file, 'r') as f:
                receipts = json.load(f)
            
            required_fields = ["vehicle_number", "vehicle_type", "entry_time", "slot"]
            for i, receipt in enumerate(receipts):
                for field in required_fields:
                    if field not in receipt:
                        issues.append(f"Receipt entry {i}: Missing field '{field}'")
                        
        except Exception as e:
            issues.append(f"Error reading receipt file: {e}")
        
        return issues

    def get_peak_hours(self):
        """Analyze peak parking hours"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            hour_counts = {}
            for log in logs:
                entry_time = datetime.fromisoformat(log.get("entry_time", ""))
                hour = entry_time.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "peak_hours": sorted_hours[:5],  # Top 5 peak hours
                "hourly_distribution": hour_counts
            }
            
        except Exception as e:
            print(f"Error analyzing peak hours: {e}")
            return None

    def calculate_average_parking_duration(self):
        """Calculate average parking duration"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            if not logs:
                return 0
            
            total_duration = sum(log.get("duration_hours", 0) for log in logs)
            return round(total_duration / len(logs), 2)
            
        except Exception as e:
            print(f"Error calculating average duration: {e}")
            return 0


def main():
    """Utility script main function for command line usage"""
    import sys
    
    utils = ParkingUtils()
    
    if len(sys.argv) < 2:
        print("Usage: python utils.py <command> [args]")
        print("Commands:")
        print("  backup - Create backup of data files")
        print("  export - Export logs to CSV")
        print("  clean <days> - Clean logs older than specified days")
        print("  validate - Check data integrity")
        print("  report <year> <month> - Generate monthly report")
        print("  peak - Show peak parking hours")
        print("  duration - Show average parking duration")
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        files = utils.backup_data()
        print(f"Backed up {len(files)} files: {files}")
        
    elif command == "export":
        if utils.export_to_csv():
            print("Data exported to parking_data.csv")
        else:
            print("Export failed")
            
    elif command == "clean":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        removed = utils.clean_old_logs(days)
        print(f"Removed {removed} old log entries")
        
    elif command == "validate":
        issues = utils.validate_data_integrity()
        if issues:
            print("Data integrity issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("No data integrity issues found")
            
    elif command == "report":
        if len(sys.argv) < 4:
            print("Usage: python utils.py report <year> <month>")
            return
        year, month = int(sys.argv[2]), int(sys.argv[3])
        report = utils.generate_monthly_report(year, month)
        if report:
            print(f"Monthly Report for {month}/{year}:")
            print(f"Total Vehicles: {report['total_vehicles']}")
            print(f"Total Revenue: ${report['total_revenue']}")
            print(f"Average Fee: ${report['average_fee']}")
            print(f"Peak Day: {report['peak_day']}")
        else:
            print("No data found for the specified month")
            
    elif command == "peak":
        peak_data = utils.get_peak_hours()
        if peak_data:
            print("Peak parking hours:")
            for hour, count in peak_data["peak_hours"]:
                print(f"  {hour:02d}:00 - {count} vehicles")
        else:
            print("No peak hour data available")
            
    elif command == "duration":
        avg_duration = utils.calculate_average_parking_duration()
        print(f"Average parking duration: {avg_duration} hours")
        
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
