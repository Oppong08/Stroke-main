import os
import django
from datetime import datetime, timedelta
import random
from django.db import transaction

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stroke_unit_system.settings')
django.setup()

from patientsystem.models import Patient, Vitals, Consultation, Alert, UserProfile
from django.contrib.auth.models import User

def setup_users():
    """Create or update users and their profiles"""
    # Create neurologists
    for i in range(2):
        username = f'neurologist{i+1}'
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password='password123')
        
        # Handle user profile
        try:
            profile = UserProfile.objects.get(user=user)
            profile.role = 'neurologist'
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=user, role='neurologist')

    # Create technicians
    for i in range(2):
        username = f'technician{i+1}'
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password='password123')
        
        # Handle user profile
        try:
            profile = UserProfile.objects.get(user=user)
            profile.role = 'technician'
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=user, role='technician')

def create_sample_patients():
    # Create sample vitals
    vitals_data = [
        {
            'blood_pressure': '120/80',
            'heart_rate': 75,
            'oxygen_saturation': 98.0,
            'temperature': 37.0,
            'blood_glucose': 100
        },
        {
            'blood_pressure': '140/90',
            'heart_rate': 85,
            'oxygen_saturation': 96.0,
            'temperature': 37.2,
            'blood_glucose': 120
        },
        {
            'blood_pressure': '160/100',
            'heart_rate': 95,
            'oxygen_saturation': 94.0,
            'temperature': 37.5,
            'blood_glucose': 150
        },
        {
            'blood_pressure': '180/110',
            'heart_rate': 110,
            'oxygen_saturation': 92.0,
            'temperature': 38.0,
            'blood_glucose': 200
        }
    ]

    # Create sample patients
    patients_data = [
        {
            'first_name': 'John',
            'last_name': 'Smith',
            'date_of_birth': datetime(1960, 5, 15),
            'gender': 'M',
            'chief_complaint': 'Sudden onset of right-sided weakness and speech difficulty',
            'medical_history': 'Hypertension, Type 2 Diabetes',
            'current_medications': 'Lisinopril, Metformin',
            'allergies': 'Penicillin'
        },
        {
            'first_name': 'Mary',
            'last_name': 'Johnson',
            'date_of_birth': datetime(1955, 8, 22),
            'gender': 'F',
            'chief_complaint': 'Acute onset of left-sided facial droop and arm weakness',
            'medical_history': 'Atrial Fibrillation, Hyperlipidemia',
            'current_medications': 'Warfarin, Atorvastatin',
            'allergies': 'None'
        },
        {
            'first_name': 'Robert',
            'last_name': 'Williams',
            'date_of_birth': datetime(1972, 3, 10),
            'gender': 'M',
            'chief_complaint': 'Sudden severe headache and confusion',
            'medical_history': 'Migraine, Hypertension',
            'current_medications': 'Propranolol',
            'allergies': 'NSAIDs'
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Brown',
            'date_of_birth': datetime(1948, 11, 30),
            'gender': 'F',
            'chief_complaint': 'Acute onset of vision loss in right eye',
            'medical_history': 'Diabetes, Coronary Artery Disease',
            'current_medications': 'Insulin, Aspirin',
            'allergies': 'Sulfa drugs'
        }
    ]

    # Create patients with vitals
    for i, (patient_data, vital_data) in enumerate(zip(patients_data, vitals_data)):
        try:
            with transaction.atomic():
                vitals = Vitals.objects.create(**vital_data)
                patient = Patient.objects.create(
                    **patient_data,
                    vitals=vitals,
                    nihss_score=random.randint(4, 20),
                    nihss_last_updated=datetime.now() - timedelta(hours=random.randint(1, 24))
                )

                # Create consultations for each patient
                for _ in range(random.randint(1, 3)):
                    consultation_vitals = Vitals.objects.create(
                        blood_pressure=f"{random.randint(100, 200)}/{random.randint(60, 120)}",
                        heart_rate=random.randint(50, 120),
                        oxygen_saturation=random.uniform(90.0, 100.0),
                        temperature=random.uniform(36.0, 39.0),
                        blood_glucose=random.randint(70, 300)
                    )
                    
                    consultation = Consultation.objects.create(
                        patient=patient,
                        diagnosis='Ischemic stroke',
                        treatment_plan='Monitor vitals, administer tPA if eligible',
                        test_orders='CT scan, blood work',
                        vitals=consultation_vitals,
                        nihss_score=random.randint(4, 20)
                    )

                    # Create alerts based on consultation data
                    if consultation.nihss_score >= 4:
                        Alert.objects.create(
                            type='warning',
                            description=f'NIHSS score ({consultation.nihss_score}) indicates potential stroke',
                            patient=patient
                        )
                    
                    systolic, diastolic = map(int, consultation.vitals.blood_pressure.split('/'))
                    if systolic > 185 or diastolic > 110:
                        Alert.objects.create(
                            type='critical',
                            description=f'High blood pressure ({consultation.vitals.blood_pressure}) detected - tPA contraindicated',
                            patient=patient
                        )
                    
                    if consultation.vitals.heart_rate < 60 or consultation.vitals.heart_rate > 100:
                        Alert.objects.create(
                            type='warning',
                            description=f'Abnormal heart rate ({consultation.vitals.heart_rate} bpm) detected',
                            patient=patient
                        )
                    
                    if consultation.vitals.oxygen_saturation < 95:
                        Alert.objects.create(
                            type='warning',
                            description=f'Low oxygen saturation ({consultation.vitals.oxygen_saturation}%) detected',
                            patient=patient
                        )
                    
                    if consultation.vitals.temperature < 36.1 or consultation.vitals.temperature > 38:
                        Alert.objects.create(
                            type='warning',
                            description=f'Abnormal temperature ({consultation.vitals.temperature}°C) detected',
                            patient=patient
                        )
                    
                    if consultation.vitals.blood_glucose is not None:
                        if consultation.vitals.blood_glucose < 50 or consultation.vitals.blood_glucose > 400:
                            Alert.objects.create(
                                type='critical',
                                description=f'Abnormal blood glucose ({consultation.vitals.blood_glucose} mg/dL) - tPA contraindicated',
                                patient=patient
                            )
                    
                    if patient.age < 18:
                        Alert.objects.create(
                            type='critical',
                            description=f'Patient age ({patient.age}) is below tPA eligibility threshold',
                            patient=patient
                        )
        except Exception as e:
            print(f"Error creating patient {patient_data['first_name']} {patient_data['last_name']}: {str(e)}")
            continue

if __name__ == '__main__':
    print("Seeding database...")
    try:
        setup_users()
        create_sample_patients()
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error during database seeding: {str(e)}") 