import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stroke_unit_system.settings')
django.setup()

from django.contrib.auth.models import User
from patientsystem.models import UserProfile, Patient, Vitals, Consultation, Alert
from django.utils import timezone

def clear_database():
    """Clear all existing data"""
    print("Clearing existing data...")
    Alert.objects.all().delete()
    Consultation.objects.all().delete()
    Patient.objects.all().delete()
    Vitals.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.all().delete()
    print("Database cleared successfully!")

def create_users():
    """Create initial users"""
    print("Creating users...")
    
    # Create neurologist
    neurologist, created = User.objects.get_or_create(
        username='neurologist',
        defaults={
            'email': 'neurologist@example.com',
            'first_name': 'John',
            'last_name': 'Smith'
        }
    )
    if created:
        neurologist.set_password('password123')
        neurologist.save()
    
    UserProfile.objects.update_or_create(
        user=neurologist,
        defaults={'role': 'neurologist'}
    )
    
    # Create technician
    technician, created = User.objects.get_or_create(
        username='technician',
        defaults={
            'email': 'technician@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe'
        }
    )
    if created:
        technician.set_password('password123')
        technician.save()
    
    UserProfile.objects.update_or_create(
        user=technician,
        defaults={'role': 'technician'}
    )
    
    print("Users created successfully!")

def create_patients():
    """Create sample patients"""
    print("Creating patients...")
    
    # Sample patient data with realistic stroke cases
    patients_data = [
        {
            'first_name': 'Maria',
            'last_name': 'Gonzalez',
            'date_of_birth': datetime(1951, 3, 15),
            'gender': 'F',
            'chief_complaint': 'Sudden onset of slurred speech and right facial droop',
            'address': '123 Main St, Anytown',
            'phone_number': '555-1234',
            'emergency_contact': 'Carlos Gonzalez (Son) - 555-5678',
            'medical_history': 'Hypertension, Type 2 Diabetes, Hyperlipidemia',
            'current_medications': 'Lisinopril 10mg daily, Metformin 500mg BID, Atorvastatin 40mg daily',
            'allergies': 'Penicillin'
        },
        {
            'first_name': 'Richard',
            'last_name': 'Kim',
            'date_of_birth': datetime(1965, 7, 22),
            'gender': 'M',
            'chief_complaint': 'Acute left-sided weakness and numbness',
            'address': '456 Oak Ave, Somewhere',
            'phone_number': '555-4321',
            'emergency_contact': 'Sarah Kim (Wife) - 555-8765',
            'medical_history': 'Atrial Fibrillation, Hypertension',
            'current_medications': 'Warfarin 5mg daily, Amlodipine 10mg daily',
            'allergies': 'None'
        },
        {
            'first_name': 'Patricia',
            'last_name': 'Johnson',
            'date_of_birth': datetime(1948, 11, 5),
            'gender': 'F',
            'chief_complaint': 'Sudden confusion and difficulty finding words',
            'address': '789 Pine St, Anywhere',
            'phone_number': '555-9876',
            'emergency_contact': 'Michael Johnson (Son) - 555-5432',
            'medical_history': 'Hypertension, Previous TIA',
            'current_medications': 'Losartan 50mg daily, Aspirin 81mg daily',
            'allergies': 'Sulfa drugs'
        },
        {
            'first_name': 'James',
            'last_name': 'Wilson',
            'date_of_birth': datetime(1958, 2, 18),
            'gender': 'M',
            'chief_complaint': 'Sudden loss of vision in right eye',
            'address': '321 Elm St, Nowhere',
            'phone_number': '555-2468',
            'emergency_contact': 'Emily Wilson (Daughter) - 555-1357',
            'medical_history': 'Type 2 Diabetes, Hyperlipidemia',
            'current_medications': 'Metformin 1000mg BID, Simvastatin 40mg daily',
            'allergies': 'None'
        },
        {
            'first_name': 'Susan',
            'last_name': 'Chen',
            'date_of_birth': datetime(1962, 9, 30),
            'gender': 'F',
            'chief_complaint': 'Sudden severe headache and vomiting',
            'address': '654 Maple Ave, Somewhere',
            'phone_number': '555-3698',
            'emergency_contact': 'David Chen (Husband) - 555-7412',
            'medical_history': 'Hypertension, Migraine',
            'current_medications': 'Amlodipine 5mg daily, Propranolol 40mg daily',
            'allergies': 'Codeine'
        },
        {
            'first_name': 'Robert',
            'last_name': 'Martinez',
            'date_of_birth': datetime(1953, 4, 12),
            'gender': 'M',
            'chief_complaint': 'Sudden dizziness and loss of balance',
            'address': '987 Cedar St, Anywhere',
            'phone_number': '555-8520',
            'emergency_contact': 'Lisa Martinez (Wife) - 555-9630',
            'medical_history': 'Atrial Fibrillation, Hypertension',
            'current_medications': 'Apixaban 5mg BID, Lisinopril 20mg daily',
            'allergies': 'None'
        },
        {
            'first_name': 'Elizabeth',
            'last_name': 'Taylor',
            'date_of_birth': datetime(1945, 8, 25),
            'gender': 'F',
            'chief_complaint': 'Sudden difficulty swallowing and speaking',
            'address': '147 Birch St, Nowhere',
            'phone_number': '555-7531',
            'emergency_contact': 'John Taylor (Son) - 555-1597',
            'medical_history': 'Hypertension, Type 2 Diabetes',
            'current_medications': 'Metoprolol 50mg BID, Metformin 1000mg BID',
            'allergies': 'Penicillin'
        },
        {
            'first_name': 'Thomas',
            'last_name': 'Anderson',
            'date_of_birth': datetime(1960, 1, 7),
            'gender': 'M',
            'chief_complaint': 'Sudden right arm weakness and facial droop',
            'address': '258 Oak St, Somewhere',
            'phone_number': '555-4567',
            'emergency_contact': 'Jennifer Anderson (Wife) - 555-7890',
            'medical_history': 'Hypertension, Hyperlipidemia',
            'current_medications': 'Losartan 100mg daily, Atorvastatin 40mg daily',
            'allergies': 'None'
        },
        {
            'first_name': 'Margaret',
            'last_name': 'Brown',
            'date_of_birth': datetime(1955, 6, 14),
            'gender': 'F',
            'chief_complaint': 'Sudden confusion and memory loss',
            'address': '369 Pine Ave, Anywhere',
            'phone_number': '555-1478',
            'emergency_contact': 'William Brown (Husband) - 555-2589',
            'medical_history': 'Hypertension, Previous Stroke',
            'current_medications': 'Amlodipine 10mg daily, Clopidogrel 75mg daily',
            'allergies': 'Sulfa drugs'
        },
        {
            'first_name': 'David',
            'last_name': 'Lee',
            'date_of_birth': datetime(1968, 3, 28),
            'gender': 'M',
            'chief_complaint': 'Sudden severe headache and left-sided weakness',
            'address': '741 Maple St, Nowhere',
            'phone_number': '555-3698',
            'emergency_contact': 'Sarah Lee (Wife) - 555-7412',
            'medical_history': 'Hypertension, Migraine',
            'current_medications': 'Lisinopril 20mg daily, Propranolol 40mg daily',
            'allergies': 'None'
        }
    ]
    
    for data in patients_data:
        # Create vitals first with realistic stroke-related values
        vitals = Vitals.objects.create(
            blood_pressure=f"{random.randint(140, 190)}/{random.randint(80, 110)}",
            heart_rate=random.randint(60, 100),
            oxygen_saturation=random.uniform(92.0, 100.0),
            temperature=random.uniform(36.5, 37.5),
            blood_glucose=random.randint(80, 200)
        )
        
        # Create patient with vitals and realistic NIHSS scores
        nihss_score = random.randint(0, 20)
        patient = Patient.objects.create(
            **data,
            vitals=vitals,
            nihss_score=nihss_score
        )
        
        # Create initial consultation with realistic findings
        consultation = Consultation.objects.create(
            patient=patient,
            diagnosis="Acute Ischemic Stroke",
            treatment_plan="IV tPA administration, monitoring for complications",
            test_orders="CT Head, CBC, BMP, PT/INR, CTA Head/Neck",
            vitals=Vitals.objects.create(
                blood_pressure=vitals.blood_pressure,
                heart_rate=vitals.heart_rate,
                oxygen_saturation=vitals.oxygen_saturation,
                temperature=vitals.temperature,
                blood_glucose=vitals.blood_glucose
            ),
            nihss_score=nihss_score
        )
        
        # Create alerts based on NIHSS score severity
        if nihss_score >= 10:
            # Critical alert for severe stroke (NIHSS >= 10)
            Alert.objects.create(
                type='critical',
                description=f'SEVERE STROKE ALERT: NIHSS score {nihss_score} indicates major stroke. Immediate intervention required.',
                patient=patient
            )
        elif nihss_score >= 4:
            # Warning alert for moderate stroke (NIHSS 4-9)
            Alert.objects.create(
                type='warning',
                description=f'MODERATE STROKE ALERT: NIHSS score {nihss_score} indicates moderate stroke. Close monitoring required.',
                patient=patient
            )
        
        # Create additional alerts based on vital signs
        systolic, diastolic = map(int, vitals.blood_pressure.split('/'))
        if systolic > 180 or diastolic > 110:
            Alert.objects.create(
                type='critical',
                description=f'CRITICAL BLOOD PRESSURE: {vitals.blood_pressure}. tPA contraindicated.',
                patient=patient
            )
        
        if vitals.oxygen_saturation < 94:
            Alert.objects.create(
                type='warning',
                description=f'LOW OXYGEN SATURATION: {vitals.oxygen_saturation}%. Supplemental oxygen may be required.',
                patient=patient
            )
        
        if vitals.blood_glucose and vitals.blood_glucose > 180:
            Alert.objects.create(
                type='warning',
                description=f'ELEVATED BLOOD GLUCOSE: {vitals.blood_glucose} mg/dL. Monitor for hyperglycemia.',
                patient=patient
            )
    
    print("Patients created successfully!")

def create_consultations():
    """Create sample consultations"""
    print("Creating consultations...")
    
    patients = Patient.objects.all()
    neurologist = User.objects.get(username='neurologist')
    
    for patient in patients:
        Consultation.objects.update_or_create(
            patient=patient,
            neurologist=neurologist,
            defaults={
                'notes': f'Initial consultation for {patient.name}',
                'timestamp': datetime.now() - timedelta(days=random.randint(1, 7))
            }
        )
    
    print("Consultations created successfully!")

def create_alerts():
    """Create sample alerts"""
    print("Creating alerts...")
    
    patients = Patient.objects.all()
    alert_types = ['critical', 'warning']
    alert_descriptions = [
        'Blood pressure above threshold',
        'Heart rate irregular',
        'Oxygen saturation low',
        'Temperature elevated'
    ]
    
    for patient in patients:
        Alert.objects.create(
            patient=patient,
            type=random.choice(alert_types),
            description=random.choice(alert_descriptions),
            timestamp=datetime.now() - timedelta(hours=random.randint(1, 24))
        )
    
    print("Alerts created successfully!")

def main():
    """Main function to run the seeding process"""
    try:
        clear_database()
        create_users()
        create_patients()
        create_consultations()
        create_alerts()
        print("\nDatabase seeding completed successfully!")
    except Exception as e:
        print(f"\nError during seeding: {str(e)}")

if __name__ == '__main__':
    main() 