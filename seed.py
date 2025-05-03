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
            'first_name': 'Elena',
            'last_name': 'Rodriguez',
            'date_of_birth': datetime(1953, 5, 12),
            'gender': 'F',
            'chief_complaint': 'Sudden difficulty speaking and right arm weakness',
            'address': '789 Cedar Lane, Riverside',
            'phone_number': '555-2341',
            'emergency_contact': 'Miguel Rodriguez (Son) - 555-6789',
            'medical_history': 'Hypertension, Atrial Fibrillation, Obesity',
            'current_medications': 'Metoprolol 50mg daily, Warfarin 5mg daily, Atorvastatin 20mg daily',
            'allergies': 'Aspirin'
        },
        {
            'first_name': 'Kevin',
            'last_name': 'Park',
            'date_of_birth': datetime(1968, 9, 14),
            'gender': 'M',
            'chief_complaint': 'Sudden onset of left facial droop and arm weakness',
            'address': '456 Birch Street, Lakeside',
            'phone_number': '555-8765',
            'emergency_contact': 'Grace Park (Wife) - 555-4321',
            'medical_history': 'Type 2 Diabetes, Hyperlipidemia, Former smoker',
            'current_medications': 'Glimepiride 4mg daily, Rosuvastatin 10mg daily',
            'allergies': 'Shellfish'
        },
        {
            'first_name': 'Amelia',
            'last_name': 'Thompson',
            'date_of_birth': datetime(1951, 3, 26),
            'gender': 'F',
            'chief_complaint': 'Acute vision loss in right eye and dizziness',
            'address': '234 Maple Drive, Hillview',
            'phone_number': '555-3456',
            'emergency_contact': 'Daniel Thompson (Husband) - 555-7654',
            'medical_history': 'Hypertension, Previous TIA, Migraines',
            'current_medications': 'Lisinopril 20mg daily, Aspirin 81mg daily, Sumatriptan PRN',
            'allergies': 'Penicillin, Codeine'
        },
        {
            'first_name': 'Marcus',
            'last_name': 'Washington',
            'date_of_birth': datetime(1957, 11, 3),
            'gender': 'M',
            'chief_complaint': 'Sudden loss of balance and slurred speech',
            'address': '567 Walnut Avenue, Plainfield',
            'phone_number': '555-9012',
            'emergency_contact': 'Tanya Washington (Daughter) - 555-8901',
            'medical_history': 'Coronary Artery Disease, Hypertension, COPD',
            'current_medications': 'Clopidogrel 75mg daily, Amlodipine 5mg daily, Albuterol inhaler PRN',
            'allergies': 'None'
        },
        {
            'first_name': 'Olivia',
            'last_name': 'Garcia',
            'date_of_birth': datetime(1960, 7, 19),
            'gender': 'F',
            'chief_complaint': 'Severe headache and neck stiffness with nausea',
            'address': '890 Pine Court, Westville',
            'phone_number': '555-5678',
            'emergency_contact': 'Alejandro Garcia (Son) - 555-2345',
            'medical_history': 'Hypertension, Depression, Osteoarthritis',
            'current_medications': 'Hydrochlorothiazide 25mg daily, Sertraline 50mg daily, Acetaminophen PRN',
            'allergies': 'Sulfa drugs'
        },
        {
            'first_name': 'Jamal',
            'last_name': 'Wilson',
            'date_of_birth': datetime(1955, 2, 28),
            'gender': 'M',
            'chief_complaint': 'Confusion, right-sided weakness and aphasia',
            'address': '123 Elm Street, Oakwood',
            'phone_number': '555-4567',
            'emergency_contact': 'Keisha Wilson (Wife) - 555-7890',
            'medical_history': 'Hypertension, Type 2 Diabetes, Previous Stroke',
            'current_medications': 'Losartan 100mg daily, Metformin 1000mg BID, Atorvastatin 40mg daily',
            'allergies': 'ACE inhibitors'
        },
        {
            'first_name': 'Sofia',
            'last_name': 'Patel',
            'date_of_birth': datetime(1947, 10, 5),
            'gender': 'F',
            'chief_complaint': 'Sudden onset of slurred speech and facial asymmetry',
            'address': '345 Lakeview Road, Greenfield',
            'phone_number': '555-6789',
            'emergency_contact': 'Raj Patel (Son) - 555-9012',
            'medical_history': 'Atrial Fibrillation, Heart Failure, Hypothyroidism',
            'current_medications': 'Apixaban 5mg BID, Furosemide 40mg daily, Levothyroxine 100mcg daily',
            'allergies': 'Iodine contrast'
        },
        {
            'first_name': 'Benjamin',
            'last_name': 'Nguyen',
            'date_of_birth': datetime(1963, 8, 15),
            'gender': 'M',
            'chief_complaint': 'Left arm numbness and visual changes',
            'address': '678 Sunset Boulevard, Riverdale',
            'phone_number': '555-1234',
            'emergency_contact': 'Linda Nguyen (Wife) - 555-5432',
            'medical_history': 'Hyperlipidemia, Sleep Apnea, Gout',
            'current_medications': 'Rosuvastatin 20mg daily, CPAP at night, Allopurinol 300mg daily',
            'allergies': 'None'
        },
        {
            'first_name': 'Isabella',
            'last_name': 'Martinez',
            'date_of_birth': datetime(1958, 4, 23),
            'gender': 'F',
            'chief_complaint': 'Sudden weakness on right side and difficulty finding words',
            'address': '901 Highland Avenue, Centreville',
            'phone_number': '555-8901',
            'emergency_contact': 'Carlos Martinez (Husband) - 555-3456',
            'medical_history': 'Hypertension, Rheumatoid Arthritis, Osteoporosis',
            'current_medications': 'Valsartan 160mg daily, Methotrexate 15mg weekly, Alendronate 70mg weekly',
            'allergies': 'NSAIDs'
        },
        {
            'first_name': 'Ethan',
            'last_name': 'Jackson',
            'date_of_birth': datetime(1970, 6, 11),
            'gender': 'M',
            'chief_complaint': 'Sudden severe headache and altered level of consciousness',
            'address': '432 River Road, Brookside',
            'phone_number': '555-7123',
            'emergency_contact': 'Michelle Jackson (Wife) - 555-8234',
            'medical_history': 'Uncontrolled Hypertension, Chronic Kidney Disease',
            'current_medications': 'Amlodipine 10mg daily, Carvedilol 25mg BID',
            'allergies': 'Latex'
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