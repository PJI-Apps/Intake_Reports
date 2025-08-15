# test_data_generator.py
# Generate realistic but fake test data for PJI Law Reports

import pandas as pd
import random
from datetime import date, timedelta
from calendar import monthrange

def generate_fake_names(count=10):
    """Generate fake names for testing"""
    first_names = ["Alex", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Quinn", "Avery", "Blake", "Dakota"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    names = []
    for _ in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        names.append(f"{first} {last}")
    
    return names

def generate_fake_emails(names, count=None):
    """Generate fake emails based on names"""
    if count is None:
        count = len(names)
    
    domains = ["test.com", "example.com", "demo.org", "fake.net"]
    emails = []
    
    for i in range(count):
        if i < len(names):
            name = names[i].lower().replace(" ", ".")
        else:
            name = f"user{i}"
        
        domain = random.choice(domains)
        emails.append(f"{name}@{domain}")
    
    return emails

def generate_test_calls_data(months=12, staff_count=5):
    """Generate fake calls data for testing"""
    staff_names = generate_fake_names(staff_count)
    categories = ["Intake", "Receptionist", "Intake IC"]
    
    data = []
    current_date = date.today()
    
    for month_offset in range(months):
        # Go back in time month by month
        target_date = current_date.replace(day=1) - timedelta(days=30 * month_offset)
        year = target_date.year
        month = target_date.month
        
        for staff in staff_names:
            # Generate realistic call data
            total_calls = random.randint(80, 300)
            completed_calls = random.randint(int(total_calls * 0.6), int(total_calls * 0.9))
            outgoing = random.randint(int(total_calls * 0.3), int(total_calls * 0.7))
            received = total_calls - outgoing
            missed = random.randint(5, int(total_calls * 0.2))
            forwarded = random.randint(0, int(total_calls * 0.1))
            answered_other = random.randint(0, int(total_calls * 0.05))
            
            # Generate realistic call times
            avg_minutes = random.randint(2, 15)
            avg_seconds = random.randint(0, 59)
            avg_time = f"{avg_minutes:02d}:{avg_seconds:02d}"
            
            total_minutes = avg_minutes * completed_calls
            total_time = f"{total_minutes:02d}:00"
            
            hold_minutes = random.randint(0, 5)
            hold_time = f"{hold_minutes:02d}:00"
            
            data.append({
                "Name": staff,
                "Total Calls": total_calls,
                "Completed Calls": completed_calls,
                "Outgoing": outgoing,
                "Received": received,
                "Forwarded to Voicemail": forwarded,
                "Answered by Other": answered_other,
                "Missed": missed,
                "Avg Call Time": avg_time,
                "Total Call Time": total_time,
                "Total Hold Time": hold_time,
                "Month-Year": f"{year}-{month:02d}",
                "Category": random.choice(categories)
            })
    
    return pd.DataFrame(data)

def generate_test_leads_data(count=50):
    """Generate fake leads/PNCs data for testing"""
    names = generate_fake_names(count)
    emails = generate_fake_emails(names, count)
    
    stages = [
        "New Lead", "Consultation Scheduled", "Consultation Completed",
        "Discovery Meeting Scheduled", "Discovery Meeting Completed",
        "Client Retained", "Referred Out", "No Follow Up"
    ]
    
    practice_areas = ["Estate Planning", "Estate Administration", "Civil Litigation", "Business transactional"]
    attorneys = ["Test Attorney 1", "Test Attorney 2", "Test Attorney 3"]
    intake_specialists = ["Test Intake 1", "Test Intake 2", "Test Intake 3"]
    
    data = []
    for i in range(count):
        # Generate realistic dates
        start_date = date.today() - timedelta(days=random.randint(0, 365))
        ic_date = start_date + timedelta(days=random.randint(1, 30)) if random.random() > 0.3 else None
        dm_date = ic_date + timedelta(days=random.randint(7, 60)) if ic_date and random.random() > 0.4 else None
        
        # Format dates for display
        ic_date_str = ic_date.strftime("%m/%d/%Y") if ic_date else ""
        dm_date_str = dm_date.strftime("%m/%d/%Y") if dm_date else ""
        
        first_name, last_name = names[i].split(" ", 1)
        
        data.append({
            "First Name": first_name,
            "Last Name": last_name,
            "Email": emails[i],
            "Stage": random.choice(stages),
            "Assigned Intake Specialist": random.choice(intake_specialists),
            "Status": random.choice(["Active", "Inactive", "Pending"]),
            "Sub Status": random.choice(["", "Follow Up Required", "Waiting for Response"]),
            "Matter ID": f"MAT-{random.randint(1000, 9999)}",
            "Reason for Rescheduling": "" if random.random() > 0.2 else random.choice(["Conflict", "Emergency", "Weather"]),
            "No Follow Up (Reason)": "" if random.random() > 0.1 else random.choice(["Not Interested", "Went Elsewhere", "No Response"]),
            "Refer Out?": random.choice(["", "Yes", "No"]),
            "Lead Attorney": random.choice(attorneys),
            "Initial Consultation With Pji Law": ic_date_str,
            "Initial Consultation Rescheduled With Pji Law": "" if random.random() > 0.1 else "Yes",
            "Discovery Meeting Rescheduled With Pji Law": "" if random.random() > 0.1 else "Yes",
            "Discovery Meeting With Pji Law": dm_date_str,
            "Practice Area": random.choice(practice_areas)
        })
    
    return pd.DataFrame(data)

def generate_test_initial_consultation_data(count=30):
    """Generate fake initial consultation data"""
    names = generate_fake_names(count)
    emails = generate_fake_emails(names, count)
    
    data = []
    for i in range(count):
        first_name, last_name = names[i].split(" ", 1)
        consultation_date = date.today() - timedelta(days=random.randint(0, 180))
        
        data.append({
            "First Name": first_name,
            "Last Name": last_name,
            "Email": emails[i],
            "Matter ID": f"MAT-{random.randint(1000, 9999)}",
            "Assigned Intake Specialist": random.choice(["Test Intake 1", "Test Intake 2"]),
            "Sub Status": random.choice(["Completed", "Scheduled", "Cancelled"]),
            "Initial Consultation With Pji Law": consultation_date.strftime("%m/%d/%Y"),
            "Initial Consultation Rescheduled With Pji Law": "" if random.random() > 0.1 else "Yes",
            "Practice Area": random.choice(["Estate Planning", "Estate Administration", "Civil Litigation"]),
            "Lead Attorney": random.choice(["Test Attorney 1", "Test Attorney 2"]),
            "Status": random.choice(["Active", "Completed", "Cancelled"]),
            "Reason": "" if random.random() > 0.2 else random.choice(["Conflict", "Emergency", "Not Interested"])
        })
    
    return pd.DataFrame(data)

def generate_test_discovery_meeting_data(count=20):
    """Generate fake discovery meeting data"""
    names = generate_fake_names(count)
    emails = generate_fake_emails(names, count)
    
    data = []
    for i in range(count):
        first_name, last_name = names[i].split(" ", 1)
        meeting_date = date.today() - timedelta(days=random.randint(0, 120))
        
        data.append({
            "First Name": first_name,
            "Last Name": last_name,
            "Email": emails[i],
            "Matter ID": f"MAT-{random.randint(1000, 9999)}",
            "Assigned Intake Specialist": random.choice(["Test Intake 1", "Test Intake 2"]),
            "Sub Status": random.choice(["Completed", "Scheduled", "Cancelled"]),
            "Discovery Meeting With Pji Law": meeting_date.strftime("%m/%d/%Y"),
            "Discovery Meeting Rescheduled With Pji Law": "" if random.random() > 0.1 else "Yes",
            "Practice Area": random.choice(["Estate Planning", "Estate Administration", "Civil Litigation"]),
            "Lead Attorney": random.choice(["Test Attorney 1", "Test Attorney 2"]),
            "Status": random.choice(["Active", "Completed", "Cancelled"]),
            "Reason": "" if random.random() > 0.2 else random.choice(["Conflict", "Emergency", "Not Ready"])
        })
    
    return pd.DataFrame(data)

def generate_test_new_client_data(count=15):
    """Generate fake new client list data"""
    names = generate_fake_names(count)
    emails = generate_fake_emails(names, count)
    
    data = []
    for i in range(count):
        first_name, last_name = names[i].split(" ", 1)
        ic_date = date.today() - timedelta(days=random.randint(30, 365))
        payment_date = ic_date + timedelta(days=random.randint(1, 30))
        
        data.append({
            "First Name": first_name,
            "Last Name": last_name,
            "Email": emails[i],
            "Matter ID": f"MAT-{random.randint(1000, 9999)}",
            "Practice Area": random.choice(["Estate Planning", "Estate Administration", "Civil Litigation"]),
            "Initial Consultation With Pji Law": ic_date.strftime("%m/%d/%Y"),
            "Date we had BOTH the signed CLA and full payment": payment_date.strftime("%m/%d/%Y"),
            "Lead Attorney": random.choice(["Test Attorney 1", "Test Attorney 2"]),
            "Primary Intake?": random.choice(["Yes", "No"])
        })
    
    return pd.DataFrame(data)

def create_test_environment():
    """Create a complete test environment with all datasets"""
    print("🧪 Creating test environment...")
    
    # Generate all test datasets
    calls_data = generate_test_calls_data()
    leads_data = generate_test_leads_data()
    init_data = generate_test_initial_consultation_data()
    disc_data = generate_test_discovery_meeting_data()
    ncl_data = generate_test_new_client_data()
    
    # Save to CSV files (for testing)
    calls_data.to_csv("test_calls_data.csv", index=False)
    leads_data.to_csv("test_leads_data.csv", index=False)
    init_data.to_csv("test_initial_consultation_data.csv", index=False)
    disc_data.to_csv("test_discovery_meeting_data.csv", index=False)
    ncl_data.to_csv("test_new_client_data.csv", index=False)
    
    print("✅ Test data generated successfully!")
    print(f"📊 Generated {len(calls_data)} call records")
    print(f"📊 Generated {len(leads_data)} lead records")
    print(f"📊 Generated {len(init_data)} initial consultation records")
    print(f"📊 Generated {len(disc_data)} discovery meeting records")
    print(f"📊 Generated {len(ncl_data)} new client records")
    
    return {
        "calls": calls_data,
        "leads": leads_data,
        "init": init_data,
        "disc": disc_data,
        "ncl": ncl_data
    }

def main():
    """Main function to generate test data"""
    print("🧪 PJI Law Reports - Test Data Generator")
    print("=" * 50)
    print("This generates realistic but FAKE data for testing.")
    print("No real client information is used.")
    print()
    
    # Create test environment
    test_data = create_test_environment()
    
    print("\n📁 Test files created:")
    print("- test_calls_data.csv")
    print("- test_leads_data.csv")
    print("- test_initial_consultation_data.csv")
    print("- test_discovery_meeting_data.csv")
    print("- test_new_client_data.csv")
    
    print("\n🔒 Security Note:")
    print("- All data is completely fake")
    print("- No real names, emails, or client information")
    print("- Safe to use for testing and development")
    
    print("\n🚀 Next Steps:")
    print("1. Use these CSV files to test your modular app")
    print("2. Import them into your test environment")
    print("3. Verify all functionality works with test data")

if __name__ == "__main__":
    main()
