from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import datetime
from .models import Patient, Consultation, Alert, Vitals, UserProfile, LabResults, ImagingStudy, RecentEvents, Consent
from .decorators import technician_required, neurologist_required

@login_required
def dashboard(request):
    """Display role-specific dashboard"""
    # Ensure user has a profile with a role
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'technician'}
    )
    
    if user_profile.role == 'technician':
        return render(request, 'patientsystem/technician_dashboard.html', {
            'patients': Patient.objects.all()
        })
    else:  # neurologist
        return render(request, 'patientsystem/neurologist_dashboard.html', {
            'patients': Patient.objects.all(),
            'alerts': Alert.objects.filter(acknowledged=False).order_by('-timestamp')[:5]
        })

@login_required
def patient_detail(request, patient_id):
    """Display patient details for both roles"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        consultations = patient.consultations.all().order_by('-date')
        
        # Check user role
        is_technician = hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'technician'
        is_neurologist = hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'neurologist'
        
        if not (is_technician or is_neurologist):
            messages.error(request, 'You do not have permission to view patient details.')
            return redirect('patientsystem:dashboard')
        
        return render(request, 'patientsystem/patient_detail.html', {
            'patient': patient,
            'consultations': consultations,
            'is_technician': is_technician,
            'is_neurologist': is_neurologist,
            'can_create_consultation': is_neurologist  # Add this to control button visibility
        })
    except Exception as e:
        messages.error(request, f'Error accessing patient details: {str(e)}')
        return redirect('patientsystem:dashboard')

@login_required
@neurologist_required
def new_consultation(request, patient_id):
    """Handle new consultation form submission"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        if request.method == 'POST':
            try:
                # Create new Vitals record
                vitals = Vitals.objects.create(
                    blood_pressure=request.POST['blood_pressure'],
                    heart_rate=int(request.POST['heart_rate']),
                    oxygen_saturation=float(request.POST['oxygen_saturation']),
                    temperature=float(request.POST['temperature']),
                    respiratory_rate=int(request.POST['respiratory_rate'])
                )
                
                # Create new Consultation record
                consultation = Consultation.objects.create(
                    patient=patient,
                    symptom_onset_time=request.POST['symptom_onset_time'],
                    diagnosis=request.POST['diagnosis'],
                    treatment_plan=request.POST['treatment_plan'],
                    test_orders=request.POST.get('test_orders', ''),
                    vitals=vitals,
                    nihss_score=int(request.POST['nihss_score'])
                )
                
                # Create Lab Results record
                lab_results = LabResults.objects.create(
                    consultation=consultation,
                    cbc_plt=int(request.POST.get('cbc_plt', 0)) if request.POST.get('cbc_plt') else None,
                    inr=float(request.POST.get('inr', 0)) if request.POST.get('inr') else None
                )
                
                # Create Imaging Study record
                imaging_study = ImagingStudy.objects.create(
                    consultation=consultation,
                    study_type=request.POST['study_type'],
                    findings=request.POST['findings'],
                    stroke_type=request.POST['stroke_type']
                )
                
                # Create Recent Events record
                recent_events = RecentEvents.objects.create(
                    patient=patient,
                    recent_surgery=request.POST.get('recent_surgery') == 'on',
                    recent_biopsy=request.POST.get('recent_biopsy') == 'on',
                    recent_head_trauma=request.POST.get('recent_head_trauma') == 'on',
                    recent_stroke=request.POST.get('recent_stroke') == 'on',
                    recent_mi=request.POST.get('recent_mi') == 'on',
                    event_date=datetime.now().date()
                )
                
                # Create Consent record
                consent = Consent.objects.create(
                    consultation=consultation,
                    tpa_consent=request.POST.get('tpa_consent') == 'on',
                    consent_given_by=request.POST['consent_given_by'],
                    relationship_to_patient=request.POST['relationship_to_patient']
                )
                
                # Update patient's NIHSS score
                patient.nihss_score = consultation.nihss_score
                patient.vitals = vitals
                patient.save()
                
                # Check for alerts
                check_alerts(patient, consultation)
                
                messages.success(request, 'Consultation submitted successfully')
                return redirect('patientsystem:patient_detail', patient_id=patient_id)
                
            except (ValueError, KeyError) as e:
                messages.error(request, f'Error processing form: {str(e)}')
        
        return render(request, 'patientsystem/new_consultation.html', {
            'patient': patient
        })
    except Exception as e:
        messages.error(request, f'Error accessing consultation form: {str(e)}')
        return redirect('patientsystem:dashboard')

@login_required
@neurologist_required
def alerts(request):
    """Display all system alerts (neurologist only)"""
    try:
        alerts = Alert.objects.all().order_by('-timestamp')
        return render(request, 'patientsystem/alerts.html', {
            'alerts': alerts
        })
    except Exception as e:
        messages.error(request, f'Error accessing alerts: {str(e)}')
        return redirect('patientsystem:dashboard')

def custom_logout(request):
    """Custom logout view to handle both GET and POST requests"""
    logout(request)
    return redirect('login')

@login_required
@technician_required
def new_patient(request):
    """Handle new patient form submission (technician only)"""
    if request.method == 'POST':
        try:
            # Create new Vitals record
            vitals = Vitals.objects.create(
                blood_pressure=request.POST.get('blood_pressure'),
                heart_rate=request.POST.get('heart_rate'),
                oxygen_saturation=request.POST.get('oxygen_saturation'),
                temperature=request.POST.get('temperature'),
                blood_glucose=request.POST.get('blood_glucose')
            )
            
            # Create new Patient record
            patient = Patient.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                date_of_birth=request.POST.get('date_of_birth'),
                gender=request.POST.get('gender'),
                chief_complaint=request.POST.get('chief_complaint'),
                address=request.POST.get('address'),
                phone_number=request.POST.get('phone_number'),
                emergency_contact=request.POST.get('emergency_contact'),
                medical_history=request.POST.get('medical_history'),
                current_medications=request.POST.get('current_medications'),
                allergies=request.POST.get('allergies'),
                vitals=vitals
            )
            
            messages.success(request, 'Patient added successfully!')
            return redirect('patientsystem:patient_detail', patient_id=patient.id)
            
        except Exception as e:
            messages.error(request, f'Error adding patient: {str(e)}')
            return redirect('patientsystem:dashboard')
    
    return render(request, 'patientsystem/new_patient.html')

def check_alerts(patient, consultation):
    """Check for conditions that should trigger alerts"""
    # Check NIHSS score
    if consultation.nihss_score >= 4:
        Alert.objects.create(
            type='warning',
            description=f'NIHSS score ({consultation.nihss_score}) indicates potential stroke',
            patient=patient
        )
    
    # Check blood pressure
    systolic, diastolic = map(int, consultation.vitals.blood_pressure.split('/'))
    if systolic > 185 or diastolic > 110:
        Alert.objects.create(
            type='critical',
            description=f'High blood pressure ({consultation.vitals.blood_pressure}) detected - tPA contraindicated',
            patient=patient
        )
    
    # Check heart rate
    if consultation.vitals.heart_rate < 60 or consultation.vitals.heart_rate > 100:
        Alert.objects.create(
            type='warning',
            description=f'Abnormal heart rate ({consultation.vitals.heart_rate} bpm) detected',
            patient=patient
        )
    
    # Check oxygen saturation
    if consultation.vitals.oxygen_saturation < 95:
        Alert.objects.create(
            type='warning',
            description=f'Oxygen saturation below normal range ({consultation.vitals.oxygen_saturation:.1f}% < 95%) - Supplemental oxygen may be required',
            patient=patient
        )
    
    # Check temperature
    if consultation.vitals.temperature < 36.1 or consultation.vitals.temperature > 38:
        Alert.objects.create(
            type='warning',
            description=f'Abnormal temperature detected ({consultation.vitals.temperature:.1f}°C) - Normal range: 36.1°C to 38°C',
            patient=patient
        )
    
    # Check respiratory rate
    if consultation.vitals.respiratory_rate and (consultation.vitals.respiratory_rate < 12 or consultation.vitals.respiratory_rate > 20):
        Alert.objects.create(
            type='warning',
            description=f'Abnormal respiratory rate detected ({consultation.vitals.respiratory_rate} breaths/min) - Normal range: 12-20 breaths/min',
            patient=patient
        )
    
    # Check blood glucose if available
    if consultation.vitals.blood_glucose is not None:
        if consultation.vitals.blood_glucose < 50 or consultation.vitals.blood_glucose > 400:
            Alert.objects.create(
                type='critical',
                description=f'Blood glucose outside tPA administration range ({consultation.vitals.blood_glucose} mg/dL) - Normal range: 50-400 mg/dL',
                patient=patient
            )
    
    # Check age for tPA eligibility
    if patient.age < 18:
        Alert.objects.create(
            type='critical',
            description=f'Patient age ({patient.age}) is below tPA eligibility threshold',
            patient=patient
        )
    
    # Check recent events
    recent_events = patient.recent_events.first()
    if recent_events:
        if recent_events.recent_surgery:
            Alert.objects.create(
                type='critical',
                description='Recent surgery detected - tPA contraindicated',
                patient=patient
            )
        if recent_events.recent_biopsy:
            Alert.objects.create(
                type='critical',
                description='Recent biopsy detected - tPA contraindicated',
                patient=patient
            )
        if recent_events.recent_head_trauma:
            Alert.objects.create(
                type='critical',
                description='Recent head trauma detected - tPA contraindicated',
                patient=patient
            )
        if recent_events.recent_stroke:
            Alert.objects.create(
                type='critical',
                description='Recent stroke detected - tPA contraindicated',
                patient=patient
            )
        if recent_events.recent_mi:
            Alert.objects.create(
                type='critical',
                description='Recent myocardial infarction detected - tPA contraindicated',
                patient=patient
            )
    
    # Check lab results
    lab_results = consultation.lab_results.first()
    if lab_results:
        if lab_results.inr and lab_results.inr > 1.7:
            Alert.objects.create(
                type='critical',
                description=f'INR too high for tPA administration ({lab_results.inr:.1f} > 1.7) - tPA contraindicated',
                patient=patient
            )
        if lab_results.cbc_plt and lab_results.cbc_plt < 100000:
            Alert.objects.create(
                type='critical',
                description=f'Platelet count too low for tPA administration ({lab_results.cbc_plt} x10³/μL < 100,000) - tPA contraindicated',
                patient=patient
            )
    
    # Check symptom onset time
    if consultation.symptom_onset_time:
        if not consultation.within_tpa_window:
            Alert.objects.create(
                type='critical',
                description='Patient outside tPA treatment window (>4.5 hours)',
                patient=patient
            )
    
    # Check consent
    consent = consultation.consents.first()
    if consent and not consent.tpa_consent:
        Alert.objects.create(
            type='critical',
            description='No consent for tPA administration',
            patient=patient
        )

@login_required
@neurologist_required
def acknowledge_alert(request, alert_id):
    """Handle alert acknowledgment by neurologist"""
    try:
        alert = get_object_or_404(Alert, id=alert_id)
        alert.acknowledge(request.user)
        messages.success(request, 'Alert acknowledged successfully')
    except Exception as e:
        messages.error(request, f'Error acknowledging alert: {str(e)}')
    return redirect('patientsystem:dashboard')

def register(request):
    """Handle user registration with role selection"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        role = request.POST.get('role')
        
        # Validate role selection
        if not role:
            messages.error(request, 'Please select a role.')
            return render(request, 'registration/register.html', {'form': form})
        
        if role not in ['technician', 'neurologist']:
            messages.error(request, 'Invalid role selected.')
            return render(request, 'registration/register.html', {'form': form})
        
        if form.is_valid():
            try:
                # Create the user
                user = form.save()
                
                # Check if user profile already exists
                try:
                    profile = UserProfile.objects.get(user=user)
                    profile.role = role
                    profile.save()
                except UserProfile.DoesNotExist:
                    # Create new profile if it doesn't exist
                    UserProfile.objects.create(user=user, role=role)
                
                messages.success(request, 'Registration successful! Please log in with your credentials.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error during registration: {str(e)}')
                # Delete the user if profile creation failed
                user.delete()
                return render(request, 'registration/register.html', {'form': form})
        else:
            # Handle form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def custom_login(request):
    """Custom login view to handle role selection"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        role = request.POST.get('role')
        
        if form.is_valid() and role in ['neurologist', 'technician']:
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    if user_profile.role == role:
                        login(request, user)
                        messages.success(request, f'Welcome back, {username}!')
                        return redirect('patientsystem:dashboard')
                    else:
                        messages.error(request, 'Invalid role for this user.')
                except UserProfile.DoesNotExist:
                    messages.error(request, 'User profile not found.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

@login_required
@neurologist_required
def consultations(request):
    """Display all consultations (neurologist only)"""
    try:
        consultations = Consultation.objects.all().order_by('-date')
        return render(request, 'patientsystem/consultations.html', {
            'consultations': consultations
        })
    except Exception as e:
        messages.error(request, f'Error accessing consultations: {str(e)}')
        return redirect('patientsystem:dashboard')

@login_required
@technician_required
def edit_vitals(request, patient_id):
    """Handle vital sign updates (technician only)"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        if request.method == 'POST':
            try:
                # Update existing Vitals record
                vitals = patient.vitals
                vitals.blood_pressure = request.POST.get('blood_pressure')
                vitals.heart_rate = int(request.POST.get('heart_rate'))
                vitals.oxygen_saturation = float(request.POST.get('oxygen_saturation'))
                vitals.temperature = float(request.POST.get('temperature'))
                vitals.respiratory_rate = int(request.POST.get('respiratory_rate'))
                vitals.blood_glucose = int(request.POST.get('blood_glucose')) if request.POST.get('blood_glucose') else None
                vitals.save()
                
                messages.success(request, 'Vital signs updated successfully')
                return redirect('patientsystem:patient_detail', patient_id=patient_id)
                
            except (ValueError, KeyError) as e:
                messages.error(request, f'Error updating vitals: {str(e)}')
        
        return render(request, 'patientsystem/edit_vitals.html', {
            'patient': patient
        })
    except Exception as e:
        messages.error(request, f'Error accessing vitals form: {str(e)}')
        return redirect('patientsystem:dashboard')
