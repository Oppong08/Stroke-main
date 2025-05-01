import os
import django
from datetime import datetime, date
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stroke_unit_system.settings')
django.setup()

from patientsystem.models import Patient, Vitals, Consultation

def create_patient(data):
    # Check if patient already exists
    first_name = data['name'].split()[0]
    last_name = data['name'].split()[1]
    existing_patient = Patient.objects.filter(first_name=first_name, last_name=last_name).first()
    if existing_patient:
        print(f"Patient {first_name} {last_name} already exists, skipping...")
        return existing_patient

    # Create vitals first
    vitals = Vitals.objects.create(
        blood_pressure=data['vitals']['blood_pressure'],
        heart_rate=data['vitals']['heart_rate'],
        oxygen_saturation=data['vitals']['oxygen_saturation'],
        temperature=data['vitals']['temperature'],
        blood_glucose=data['vitals'].get('blood_glucose')
    )
    
    # Calculate age to get date of birth
    today = date.today()
    birth_year = today.year - data['age']
    date_of_birth = date(birth_year, 1, 1)  # Using Jan 1st as default
    
    # Create patient
    patient = Patient.objects.create(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        gender=data['sex'][0].upper(),  # Take first letter
        medical_history=data['medical_history'],
        vitals=vitals,
        nihss_score=data.get('nihss_score', 0)
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
            treatment_plan=data['consultation']['treatment'],
            vitals=consultation_vitals,
            nihss_score=data.get('nihss_score', 0)
        )
    
    return patient

# Sample patient data
patients_data = [
    {
        'name': 'John Doe',
        'age': 65,
        'sex': 'Male',
        'medical_history': 'Hypertension, hyperlipidemia, diabetes',
        'vitals': {
            'blood_pressure': '180/100',
            'heart_rate': 100,
            'oxygen_saturation': 95.0,
            'temperature': 37.0,
            'blood_glucose': 200
        },
        'nihss_score': 15,
        'consultation': {
            'diagnosis': 'Acute ischemic stroke',
            'treatment': 'tPA administration, blood pressure management, and admission to the ICU'
        }
    },
    {
        'name': 'Jane Smith',
        'age': 50,
        'sex': 'Female',
        'medical_history': 'None',
        'vitals': {
            'blood_pressure': '120/80',
            'heart_rate': 80,
            'oxygen_saturation': 98.0,
            'temperature': 37.0
        },
        'nihss_score': 8,
        'consultation': {
            'diagnosis': 'Acute ischemic stroke',
            'treatment': 'tPA administration, speech therapy, and admission to the hospital for close monitoring'
        }
    },
    {
        'name': 'Bob Johnson',
        'age': 70,
        'sex': 'Male',
        'medical_history': 'Atrial fibrillation, coronary artery disease',
        'vitals': {
            'blood_pressure': '150/90',
            'heart_rate': 110,
            'oxygen_saturation': 92.0,
            'temperature': 37.0
        },
        'nihss_score': 12,
        'consultation': {
            'diagnosis': 'Acute ischemic stroke',
            'treatment': 'tPA administration, blood pressure management, and admission to the ICU for close monitoring'
        }
    },
    {
        'name': 'Maria Rodriguez',
        'age': 40,
        'sex': 'Female',
        'medical_history': 'Migraines, depression',
        'vitals': {
            'blood_pressure': '140/90',
            'heart_rate': 90,
            'oxygen_saturation': 96.0,
            'temperature': 37.0
        },
        'nihss_score': 10,
        'consultation': {
            'diagnosis': 'Acute hemorrhagic stroke',
            'treatment': 'blood pressure management, admission to the ICU for close monitoring, and possible surgical intervention'
        }
    }
]

# Add patients to database
for patient_data in patients_data:
    try:
        patient = create_patient(patient_data)
        print(f"Created patient: {patient.first_name} {patient.last_name}")
    except Exception as e:
        print(f"Error creating patient {patient_data['name']}: {str(e)}")

print("Finished adding sample patients.") 