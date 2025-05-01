import os
import django
from datetime import datetime, date
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stroke_unit_system.settings')
django.setup()

from patientsystem.models import Patient, Vitals, Consultation

def create_patient(data):
    # Create vitals first
    vitals = Vitals.objects.create(
        blood_pressure=data['vitals']['blood_pressure'],
        heart_rate=data['vitals']['heart_rate'],
        oxygen_saturation=data['vitals']['oxygen_saturation'],
        temperature=data['vitals']['temperature'],
        blood_glucose=data['vitals'].get('blood_glucose')
    )
    
    # Create patient
    patient = Patient.objects.create(
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=data['date_of_birth'],
        gender=data['gender'],
        address=data['address'],
        phone_number=data['phone_number'],
        emergency_contact=data['emergency_contact'],
        medical_history=data['medical_history'],
        current_medications=data['current_medications'],
        allergies=data['allergies'],
        vitals=vitals,
        nihss_score=data['nihss_score']
    )
    
    # Create consultation if provided
    if 'consultation' in data:
        consultation_vitals = Vitals.objects.create(
            blood_pressure=data['vitals']['blood_pressure'],
            heart_rate=data['vitals']['heart_rate'],
            oxygen_saturation=data['vitals']['oxygen_saturation'],
            temperature=data['vitals']['temperature']
        )
        
        Consultation.objects.create(
            patient=patient,
            diagnosis=data['consultation']['diagnosis'],
            treatment_plan=data['consultation']['treatment_plan'],
            vitals=consultation_vitals,
            nihss_score=data['nihss_score']
        )
    
    return patient

# Sample patient data
patients_data = [
    {
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'date_of_birth': date(1965, 3, 15),
        'gender': 'F',
        'address': '123 Oak Street, Springfield, IL 62701',
        'phone_number': '555-123-4567',
        'emergency_contact': 'Michael Johnson (Husband)',
        'medical_history': 'Hypertension, Type 2 Diabetes, Hyperlipidemia',
        'current_medications': 'Lisinopril 10mg daily, Metformin 500mg BID, Atorvastatin 20mg daily',
        'allergies': 'Penicillin, Sulfa drugs',
        'vitals': {
            'blood_pressure': '160/95',
            'heart_rate': 88,
            'oxygen_saturation': 96.0,
            'temperature': 37.2,
            'blood_glucose': 180
        },
        'nihss_score': 12,
        'consultation': {
            'diagnosis': 'Acute ischemic stroke in the left middle cerebral artery territory',
            'treatment_plan': 'tPA administration, blood pressure management, admission to ICU for monitoring'
        }
    },
    {
        'first_name': 'Robert',
        'last_name': 'Williams',
        'date_of_birth': date(1958, 7, 22),
        'gender': 'M',
        'address': '456 Maple Avenue, Chicago, IL 60601',
        'phone_number': '555-234-5678',
        'emergency_contact': 'Emily Williams (Wife)',
        'medical_history': 'Atrial Fibrillation, Coronary Artery Disease, Previous TIA',
        'current_medications': 'Warfarin 5mg daily, Metoprolol 50mg BID, Aspirin 81mg daily',
        'allergies': 'None known',
        'vitals': {
            'blood_pressure': '140/85',
            'heart_rate': 110,
            'oxygen_saturation': 94.0,
            'temperature': 37.0
        },
        'nihss_score': 8,
        'consultation': {
            'diagnosis': 'Acute ischemic stroke in the right posterior circulation',
            'treatment_plan': 'Mechanical thrombectomy, anticoagulation management, speech therapy evaluation'
        }
    },
    {
        'first_name': 'Maria',
        'last_name': 'Garcia',
        'date_of_birth': date(1972, 11, 5),
        'gender': 'F',
        'address': '789 Pine Road, Evanston, IL 60201',
        'phone_number': '555-345-6789',
        'emergency_contact': 'Carlos Garcia (Husband)',
        'medical_history': 'Migraine with aura, Depression, Anxiety',
        'current_medications': 'Propranolol 40mg daily, Sertraline 50mg daily',
        'allergies': 'Codeine',
        'vitals': {
            'blood_pressure': '170/100',
            'heart_rate': 95,
            'oxygen_saturation': 97.0,
            'temperature': 37.1
        },
        'nihss_score': 15,
        'consultation': {
            'diagnosis': 'Acute hemorrhagic stroke in the left basal ganglia',
            'treatment_plan': 'Blood pressure management, ICU admission, neurosurgery consultation'
        }
    },
    {
        'first_name': 'James',
        'last_name': 'Chen',
        'date_of_birth': date(1949, 2, 18),
        'gender': 'M',
        'address': '321 Elm Street, Naperville, IL 60540',
        'phone_number': '555-456-7890',
        'emergency_contact': 'Lisa Chen (Daughter)',
        'medical_history': 'Hypertension, Hyperlipidemia, Chronic Kidney Disease Stage 3',
        'current_medications': 'Amlodipine 10mg daily, Rosuvastatin 20mg daily',
        'allergies': 'Iodine contrast',
        'vitals': {
            'blood_pressure': '190/105',
            'heart_rate': 75,
            'oxygen_saturation': 95.0,
            'temperature': 37.3
        },
        'nihss_score': 20,
        'consultation': {
            'diagnosis': 'Acute ischemic stroke in the right middle cerebral artery territory with hemorrhagic transformation',
            'treatment_plan': 'ICU admission, blood pressure management, close neurological monitoring'
        }
    }
]

# Add patients to database
for patient_data in patients_data:
    try:
        patient = create_patient(patient_data)
        print(f"Created patient: {patient.first_name} {patient.last_name}")
    except Exception as e:
        print(f"Error creating patient {patient_data['first_name']} {patient_data['last_name']}: {str(e)}")

print("Finished adding patients.") 