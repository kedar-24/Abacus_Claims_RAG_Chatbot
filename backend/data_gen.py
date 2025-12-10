import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_data(num_records=1000):
    print(f"Generating {num_records} mock records...")
    
    # 1. Patients
    patients = []
    for _ in range(num_records // 5): # Fewer patients than claims
        patients.append({
            "patient_id": fake.unique.uuid4(),
            "patient_name": fake.name(),
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            "state": fake.state_abbr()
        })
    df_patients = pd.DataFrame(patients)
    
    # 2. Providers (Doctors)
    specialties = ["Cardiology", "Orthopedics", "Pediatrics", "Dermatology", "Oncology", "General Practice"]
    providers = []
    for _ in range(50):
        providers.append({
            "provider_id": fake.unique.uuid4(),
            "provider_name": f"Dr. {fake.last_name()}",
            "specialty": random.choice(specialties),
            "hospital": fake.company()
        })
    df_providers = pd.DataFrame(providers)
    
    # 3. Claims
    claims = []
    diagnoses = {
        "Cardiology": ["Hypertension", "Atrial Fibrillation", "Heart Failure"],
        "Orthopedics": ["Fracture", "Arthritis", "Tendonitis"],
        "Pediatrics": ["Otitis Media", "Asthma", "Chickenpox"],
        "Dermatology": ["Acne", "Eczema", "Psoriasis"],
        "Oncology": ["Lung Cancer", "Breast Cancer", "Melanoma"],
        "General Practice": ["Flu", "Diabetes Type 2", "Back Pain"]
    }
    
    for _ in range(num_records):
        provider = random.choice(providers)
        patient = random.choice(patients)
        diagnosis = random.choice(diagnoses[provider["specialty"]])
        
        # Logic for status
        status_options = ["Approved", "Denied", "Pending"]
        status = random.choices(status_options, weights=[0.6, 0.3, 0.1])[0]
        
        denial_reason = None
        if status == "Denied":
            reasons = ["Duplicate Claim", "Service Not Covered", "Pre-auth Missing", "Incorrect Coding"]
            denial_reason = random.choice(reasons)
            
        claim_date = fake.date_between(start_date='-1y', end_date='today')
        amount = round(random.uniform(100.0, 5000.0), 2)
        
        claims.append({
            "claim_id": fake.unique.uuid4(),
            "date": claim_date.isoformat(),
            "patient_id": patient["patient_id"],
            "patient_name": patient["patient_name"],
            "provider_name": provider["provider_name"],
            "specialty": provider["specialty"],
            "diagnosis": diagnosis,
            "treatment_description": f"Treatment for {diagnosis}",
            "claim_amount": amount,
            "status": status,
            "denial_reason": denial_reason if denial_reason else "N/A"
        })
        
    df_claims = pd.DataFrame(claims)
    
    # Save to CSV
    df_claims.to_csv("backend/claims_data.csv", index=False)
    print("MetaData Generated: backend/claims_data.csv")
    return df_claims

if __name__ == "__main__":
    generate_data()
