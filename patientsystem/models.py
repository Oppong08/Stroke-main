from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver

class Vitals(models.Model):
    blood_pressure = models.CharField(max_length=20)
    heart_rate = models.IntegerField()
    oxygen_saturation = models.FloatField()
    temperature = models.FloatField()
    blood_glucose = models.IntegerField(null=True, blank=True)
    respiratory_rate = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"BP: {self.blood_pressure}, HR: {self.heart_rate}, O2: {self.oxygen_saturation}%, Temp: {self.temperature}°C, RR: {self.respiratory_rate}"
        
    def calculate_nihss(self):
        """
        Calculate an estimated NIHSS score based on vital signs.
        This is a simplified estimation algorithm - not a clinically validated approach.
        In a real system, this would be based on actual neurological examination findings.
        """
        score = 0
        
        # BP contribution - high BP often associated with more severe strokes
        try:
            systolic, diastolic = map(int, self.blood_pressure.split('/'))
            if systolic > 180 or diastolic > 110:
                score += 6  # Severe hypertension
            elif systolic > 160 or diastolic > 100:
                score += 4  # Moderate hypertension
            elif systolic > 140 or diastolic > 90:
                score += 2  # Mild hypertension
        except (ValueError, TypeError):
            # Handle cases where BP might not be properly formatted
            pass
            
        # Heart rate contribution - abnormal heart rate may indicate more severe cases
        if self.heart_rate > 120:
            score += 3  # Severe tachycardia
        elif self.heart_rate > 100:
            score += 2  # Moderate tachycardia
        elif self.heart_rate < 60:
            score += 2  # Bradycardia
            
        # Oxygen saturation contribution - low O2 sat can worsen brain injury
        if self.oxygen_saturation < 90:
            score += 4  # Severe hypoxemia
        elif self.oxygen_saturation < 94:
            score += 2  # Moderate hypoxemia
            
        # Temperature contribution - fever can worsen outcomes
        if self.temperature > 38.5:
            score += 3  # High fever
        elif self.temperature > 37.5:
            score += 1  # Mild fever
            
        # Blood glucose contribution - hyperglycemia associated with worse outcomes
        if self.blood_glucose:
            if self.blood_glucose > 300:
                score += 3  # Severe hyperglycemia
            elif self.blood_glucose > 180:
                score += 2  # Moderate hyperglycemia
            elif self.blood_glucose < 60:
                score += 3  # Hypoglycemia
                
        # Limit score to valid NIHSS range (0-42)
        return min(max(score, 0), 42)

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    hospital_id = models.CharField(max_length=10, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    chief_complaint = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    medical_history = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    vitals = models.OneToOneField(Vitals, on_delete=models.CASCADE)
    nihss_score = models.IntegerField(default=0)
    nihss_last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.hospital_id:
            # Generate hospital ID if not set
            last_patient = Patient.objects.order_by('-id').first()
            if last_patient and last_patient.hospital_id:
                last_number = int(last_patient.hospital_id.split('-')[1])
                self.hospital_id = f"P-{last_number + 1:04d}"
            else:
                self.hospital_id = "P-1001"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.hospital_id} - {self.first_name} {self.last_name}"
    
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
        
    @property
    def age(self):
        today = datetime.now()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        
    @property
    def sex(self):
        return 'Male' if self.gender == 'M' else 'Female' if self.gender == 'F' else 'Other'
        
    @property
    def tpa_status(self):
        """Return TPA status from most recent consultation"""
        latest_consultation = self.consultations.order_by('-date').first()
        if not latest_consultation:
            return 'No Data'
        
        if latest_consultation.tpa_approved:
            return 'Approved'
        return 'Not Approved'

class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    date = models.DateTimeField(auto_now_add=True)
    symptom_onset_time = models.DateTimeField(null=True, blank=True)
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    test_orders = models.TextField(blank=True)
    vitals = models.OneToOneField(Vitals, on_delete=models.CASCADE)
    nihss_score = models.IntegerField()
    tpa_approved = models.BooleanField(default=False, verbose_name="TPA Approved")
    tpa_approval_notes = models.TextField(blank=True, verbose_name="TPA Approval Notes")
    
    def __str__(self):
        return f"Consultation for {self.patient.name} on {self.date}"
    
    @property
    def within_tpa_window(self):
        if not self.symptom_onset_time:
            return None
        time_diff = self.date - self.symptom_onset_time
        return time_diff.total_seconds() <= 16200  # 4.5 hours in seconds

class Alert(models.Model):
    ALERT_TYPES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Information'),
    ]
    
    type = models.CharField(max_length=20, choices=ALERT_TYPES)
    description = models.TextField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='alerts')
    timestamp = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_type_display()} alert for {self.patient.name}"
    
    def acknowledge(self, user):
        self.acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = datetime.now()
        self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('technician', 'Technician'),
        ('neurologist', 'Neurologist')
    ], default='technician')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# Sample data
sample_patients = [
    Patient(
        first_name="John",
        last_name="Doe",
        date_of_birth="1956-05-15",
        gender="M",
        address="123 Main St, Anytown, USA",
        phone_number="555-1234",
        emergency_contact="Jane Doe",
        medical_history="Hypertension, Type 2 Diabetes",
        current_medications="Lisinopril, Metformin",
        allergies="Penicillin",
        vitals=Vitals(
            blood_pressure="150/90",
            heart_rate=85,
            oxygen_saturation=95.0,
            temperature=37.0
        ),
        nihss_score=8,
        nihss_last_updated=datetime.now()
    ),
    Patient(
        first_name="Jane",
        last_name="Smith",
        date_of_birth="1949-07-22",
        gender="F",
        address="456 Elm St, Anytown, USA",
        phone_number="555-5678",
        emergency_contact="John Smith",
        medical_history="Atrial Fibrillation, Hyperlipidemia",
        current_medications="Simvastatin, Aspirin",
        allergies="Shellfish",
        vitals=Vitals(
            blood_pressure="180/100",
            heart_rate=110,
            oxygen_saturation=92.0,
            temperature=37.5
        ),
        nihss_score=12,
        nihss_last_updated=datetime.now()
    )
]

# Initialize global storage
patients = sample_patients
consultations = []
alerts = []

class LabResults(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='lab_results')
    cbc_wbc = models.FloatField(null=True, blank=True, verbose_name="WBC Count")
    cbc_hgb = models.FloatField(null=True, blank=True, verbose_name="Hemoglobin")
    cbc_plt = models.IntegerField(null=True, blank=True, verbose_name="Platelet Count")
    bmp_glucose = models.FloatField(null=True, blank=True, verbose_name="Glucose")
    bmp_creatinine = models.FloatField(null=True, blank=True, verbose_name="Creatinine")
    inr = models.FloatField(null=True, blank=True, verbose_name="INR")
    pt = models.FloatField(null=True, blank=True, verbose_name="Prothrombin Time")
    ptt = models.FloatField(null=True, blank=True, verbose_name="PTT")
    
    def __str__(self):
        return f"Lab Results for {self.consultation.patient.name} on {self.consultation.date}"

class ImagingStudy(models.Model):
    STROKE_TYPES = [
        ('ischemic', 'Ischemic Stroke'),
        ('hemorrhagic', 'Hemorrhagic Stroke'),
        ('none', 'No Stroke'),
    ]
    
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='imaging_studies')
    study_type = models.CharField(max_length=50, choices=[
        ('CT', 'CT Scan'),
        ('MRI', 'MRI'),
    ])
    findings = models.TextField()
    stroke_type = models.CharField(max_length=20, choices=STROKE_TYPES)
    performed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.study_type} for {self.consultation.patient.name} on {self.performed_at}"

class RecentEvents(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='recent_events')
    recent_surgery = models.BooleanField(default=False)
    recent_biopsy = models.BooleanField(default=False)
    recent_head_trauma = models.BooleanField(default=False)
    recent_stroke = models.BooleanField(default=False)
    recent_mi = models.BooleanField(default=False)  # Myocardial Infarction
    event_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Recent Events for {self.patient.name}"

class Consent(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='consents')
    tpa_consent = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)
    consent_given_by = models.CharField(max_length=100, blank=True)
    relationship_to_patient = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Consent for {self.consultation.patient.name} on {self.consent_date}"
