from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from datetime import datetime
from .models import Patient, Consultation, Alert, Vitals, UserProfile, LabResults, ImagingStudy, RecentEvents, Consent, CTScanImage
from .decorators import technician_required, neurologist_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@login_required
def dashboard(request):
    """Display role-specific dashboard"""
    # Ensure user has a profile with a role
    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'technician'}
    )
    
    # Force a fresh database query for all patients, ordered by most recently updated
    all_patients = Patient.objects.all().order_by('-updated_at')
    
    if user_profile.role == 'technician':
        return render(request, 'patientsystem/technician_dashboard.html', {
            'patients': all_patients
        })
    else:  # neurologist
        return render(request, 'patientsystem/neurologist_dashboard.html', {
            'patients': all_patients,
            'alerts': Alert.objects.filter(acknowledged=False).order_by('-timestamp')[:5]
        })

@login_required
def patient_detail(request, patient_id):
    """Display patient details for both roles"""
    try:
        # Get the patient by ID
        patient = get_object_or_404(Patient, id=patient_id)
        consultations = patient.consultations.all().order_by('-date')
        
        # Get CT scan images with more debugging
        ct_scan_images = patient.ct_scan_images.all().order_by('-uploaded_at')
        print(f"Retrieved {ct_scan_images.count()} CT scan images for patient {patient.id}")
        for img in ct_scan_images:
            print(f"Image {img.id}: {img.image.name} - exists: {bool(img.image)}")
        
        # Check if user is neurologist or technician
        is_neurologist = hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'neurologist'
        is_technician = hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'technician'
        
        if not (is_neurologist or is_technician):
            messages.error(request, 'You do not have permission to view patient details.')
            return redirect('patientsystem:dashboard')
        
        context = {
            'patient': patient,
            'consultations': consultations,
            'is_neurologist': is_neurologist,
            'is_technician': is_technician,
            'ct_scan_images': ct_scan_images,
        }
        
        # Debug the context
        print(f"Context ct_scan_images length: {len(context['ct_scan_images'])}")
        
        return render(request, 'patientsystem/patient_detail.html', context)
    except Exception as e:
        import traceback
        print(f"Error in patient_detail: {str(e)}")
        print(traceback.format_exc())
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
                # Create new Vitals record specific to this consultation
                consultation_vitals = Vitals.objects.create(
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
                    vitals=consultation_vitals,  # Link the consultation-specific vitals
                    nihss_score=int(request.POST['nihss_score']), # Store NIHSS assessed during consultation
                    tpa_approved=request.POST.get('tpa_approved') == 'yes',  # Set TPA approval status
                    tpa_approval_notes=request.POST.get('tpa_approval_notes', '')  # Store TPA approval notes
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
                
                # Check for alerts based on the data from *this* consultation
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

@ensure_csrf_cookie
def csrf_debug(request):
    """View to debug CSRF token issues"""
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': 'CSRF token is valid!',
            'post_data': dict(request.POST)
        })
    return render(request, 'csrf_debug.html')

@login_required
@technician_required
def new_patient(request):
    """Handle new patient form submission (technician only)"""
    if request.method == 'POST':
        try:
            # Create new Vitals record
            vitals = Vitals.objects.create(
                blood_pressure=request.POST.get('blood_pressure'),
                heart_rate=int(request.POST.get('heart_rate')) if request.POST.get('heart_rate') else 0,
                oxygen_saturation=float(request.POST.get('oxygen_saturation')) if request.POST.get('oxygen_saturation') else 0,
                temperature=float(request.POST.get('temperature')) if request.POST.get('temperature') else 0,
                blood_glucose=int(request.POST.get('blood_glucose')) if request.POST.get('blood_glucose') else None
            )
            
            # Automatically calculate NIHSS score from vitals
            nihss_score = vitals.calculate_nihss()
            
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
                vitals=vitals,
                nihss_score=nihss_score  # Set the calculated NIHSS score
            )
            
            # Handle symptom onset time
            symptom_onset_time = request.POST.get('symptom_onset_time')
            if symptom_onset_time:
                # Create a new consultation with the symptom onset time
                consultation = Consultation.objects.create(
                    patient=patient,
                    symptom_onset_time=symptom_onset_time,
                    diagnosis="Pending neurologist evaluation",
                    treatment_plan="Pending",
                    vitals=vitals,
                    nihss_score=nihss_score
                )
                
                # Check for TPA window alerts
                check_alerts(patient, consultation)
            
            # Handle CT scan image uploads
            ct_scan_images = request.FILES.getlist('ct_scan_images')
            print(f"Number of CT scans uploaded: {len(ct_scan_images)}")
            
            for image in ct_scan_images:
                try:
                    ct_image = CTScanImage.objects.create(
                        patient=patient,
                        image=image,
                        description=request.POST.get('image_description', '')
                    )
                    print(f"Saved CT scan image: {ct_image.image.path}")
                except Exception as img_err:
                    print(f"Error saving image {image.name}: {str(img_err)}")
                    messages.warning(request, f"Error saving image {image.name}: {str(img_err)}")
            
            # Check for stroke alerts based on the NIHSS score
            if nihss_score >= 10:
                Alert.objects.create(
                    type='critical',
                    description=f'SEVERE STROKE ALERT: NIHSS score {nihss_score} indicates major stroke. Immediate intervention required.',
                    patient=patient
                )
            elif nihss_score >= 4:
                Alert.objects.create(
                    type='warning',
                    description=f'MODERATE STROKE ALERT: NIHSS score {nihss_score} indicates moderate stroke. Close monitoring required.',
                    patient=patient
                )
            
            messages.success(request, f'Patient {patient.name} added successfully!')
            # Redirect to dashboard instead of patient detail
            return redirect('patientsystem:dashboard')
            
        except Exception as e:
            import traceback
            print(f"Error adding patient: {str(e)}")
            print(traceback.format_exc())
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
        # Print debug information
        print(f"Attempting to acknowledge alert with ID: {alert_id}")
        print(f"Available alert IDs: {list(Alert.objects.values_list('id', flat=True))}")
        
        # Check if alert exists
        if not Alert.objects.filter(id=alert_id).exists():
            messages.error(request, f"Error: Alert with ID {alert_id} does not exist")
            return redirect('patientsystem:alerts')
            
        alert = get_object_or_404(Alert, id=alert_id)
        alert.acknowledge(request.user)
        messages.success(request, 'Alert acknowledged successfully')
        return redirect('patientsystem:alerts')  # Redirect to alerts page instead of dashboard
    except Exception as e:
        messages.error(request, f'Error acknowledging alert: {str(e)}')
        return redirect('patientsystem:alerts')  # Redirect to alerts page for better user experience

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

@ensure_csrf_cookie
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
    """Handle editing patient vitals (technician only)"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        if request.method == 'POST':
            try:
                # Update existing Vitals record
                patient.vitals.blood_pressure = request.POST.get('blood_pressure')
                patient.vitals.heart_rate = int(request.POST.get('heart_rate'))
                patient.vitals.oxygen_saturation = float(request.POST.get('oxygen_saturation'))
                patient.vitals.temperature = float(request.POST.get('temperature'))
                
                # Optional fields
                blood_glucose = request.POST.get('blood_glucose')
                respiratory_rate = request.POST.get('respiratory_rate')
                
                if blood_glucose and blood_glucose.strip():
                    patient.vitals.blood_glucose = int(blood_glucose)
                
                if respiratory_rate and respiratory_rate.strip():
                    patient.vitals.respiratory_rate = int(respiratory_rate)
                
                # Save the vitals record
                patient.vitals.save()
                
                # Recalculate NIHSS score
                patient.nihss_score = patient.vitals.calculate_nihss()
                patient.save()
                
                # Handle symptom onset time
                symptom_onset_time = request.POST.get('symptom_onset_time')
                if symptom_onset_time:
                    # Get the latest consultation or create a new one
                    latest_consultation = patient.consultations.order_by('-date').first()
                    if latest_consultation:
                        latest_consultation.symptom_onset_time = symptom_onset_time
                        latest_consultation.save()
                    else:
                        # Create a new consultation with the symptom onset time
                        from .models import Consultation
                        new_consultation = Consultation.objects.create(
                            patient=patient,
                            symptom_onset_time=symptom_onset_time,
                            diagnosis="Pending neurologist evaluation",
                            treatment_plan="Pending",
                            vitals=patient.vitals,
                            nihss_score=patient.nihss_score
                        )
                        
                        # Check for TPA window alerts
                        check_alerts(patient, new_consultation)
                
                # Check for alerts based on the updated vitals
                if patient.nihss_score >= 10:
                    Alert.objects.create(
                        type='critical',
                        description=f'UPDATED VITALS: NIHSS score {patient.nihss_score} indicates major stroke. Immediate intervention required.',
                        patient=patient
                    )
                elif patient.nihss_score >= 4:
                    Alert.objects.create(
                        type='warning',
                        description=f'UPDATED VITALS: NIHSS score {patient.nihss_score} indicates moderate stroke. Close monitoring required.',
                        patient=patient
                    )
                
                messages.success(request, f'Vitals for {patient.name} updated successfully!')
                return redirect('patientsystem:patient_detail', patient_id=patient_id)
                
            except (ValueError, KeyError) as e:
                messages.error(request, f'Error updating vitals: {str(e)}')
        
        # GET request - display the form
        return render(request, 'patientsystem/edit_vitals.html', {
            'patient': patient
        })
    except Exception as e:
        messages.error(request, f'Error accessing vitals form: {str(e)}')
        return redirect('patientsystem:dashboard')

@login_required
@neurologist_required
def edit_consultation(request, consultation_id):
    """Handle editing consultation data (neurologist only)"""
    try:
        consultation = get_object_or_404(Consultation, id=consultation_id)
        patient = consultation.patient
        
        if request.method == 'POST':
            try:
                # Update consultation data
                consultation.diagnosis = request.POST.get('diagnosis')
                consultation.treatment_plan = request.POST.get('treatment_plan')
                consultation.test_orders = request.POST.get('test_orders', '')
                consultation.nihss_score = int(request.POST.get('nihss_score'))
                
                # Update TPA approval status
                consultation.tpa_approved = request.POST.get('tpa_approved') == 'yes'
                consultation.tpa_approval_notes = request.POST.get('tpa_approval_notes', '')
                
                # Save the consultation
                consultation.save()
                
                # Update patient's NIHSS score if this is the most recent consultation
                latest_consultation = patient.consultations.order_by('-date').first()
                if latest_consultation and latest_consultation.id == consultation.id:
                    patient.nihss_score = consultation.nihss_score
                    patient.save()
                
                messages.success(request, f'Consultation for {patient.name} updated successfully!')
                return redirect('patientsystem:patient_detail', patient_id=patient.id)
                
            except (ValueError, KeyError) as e:
                messages.error(request, f'Error updating consultation: {str(e)}')
        
        # GET request - display the form
        return render(request, 'patientsystem/edit_consultation.html', {
            'consultation': consultation,
            'patient': patient
        })
    except Exception as e:
        messages.error(request, f'Error accessing consultation form: {str(e)}')
        return redirect('patientsystem:dashboard')

@login_required
@technician_required
def edit_patient(request, patient_id):
    """Handle editing patient details (technician only)"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        if request.method == 'POST':
            try:
                # Update patient information
                patient.first_name = request.POST.get('first_name')
                patient.last_name = request.POST.get('last_name')
                patient.date_of_birth = request.POST.get('date_of_birth')
                patient.gender = request.POST.get('gender')
                patient.chief_complaint = request.POST.get('chief_complaint')
                patient.address = request.POST.get('address')
                patient.phone_number = request.POST.get('phone_number')
                patient.emergency_contact = request.POST.get('emergency_contact')
                patient.medical_history = request.POST.get('medical_history')
                patient.current_medications = request.POST.get('current_medications')
                patient.allergies = request.POST.get('allergies')
                
                # Save the patient record
                patient.save()
                
                # Handle CT scan image uploads
                ct_scan_images = request.FILES.getlist('ct_scan_images')
                if ct_scan_images:
                    print(f"Number of CT scans uploaded during edit: {len(ct_scan_images)}")
                    
                    for image in ct_scan_images:
                        try:
                            ct_image = CTScanImage.objects.create(
                                patient=patient,
                                image=image,
                                description=request.POST.get('image_description', '')
                            )
                            print(f"Saved CT scan image during edit: {ct_image.image.path}")
                        except Exception as img_err:
                            print(f"Error saving image {image.name}: {str(img_err)}")
                            messages.warning(request, f"Error saving image {image.name}: {str(img_err)}")
                
                messages.success(request, f'Details for {patient.name} updated successfully!')
                return redirect('patientsystem:patient_detail', patient_id=patient_id)
                
            except (ValueError, KeyError) as e:
                messages.error(request, f'Error updating patient details: {str(e)}')
        
        # GET request - display the form
        return render(request, 'patientsystem/edit_patient.html', {
            'patient': patient
        })
    except Exception as e:
        messages.error(request, f'Error accessing patient form: {str(e)}')
        return redirect('patientsystem:dashboard')

@login_required
@technician_required
def upload_ct_scan(request, patient_id):
    """Handle CT scan image upload (technician only)"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        if request.method == 'POST':
            try:
                # Handle CT scan image uploads
                ct_scan_images = request.FILES.getlist('ct_scan_images')
                description = request.POST.get('image_description', '')
                
                if not ct_scan_images:
                    messages.warning(request, 'No images were selected for upload.')
                    return render(request, 'patientsystem/upload_ct_scan.html', {'patient': patient})
                
                print(f"Number of CT scans being uploaded: {len(ct_scan_images)}")
                
                uploaded_count = 0
                for image in ct_scan_images:
                    try:
                        ct_image = CTScanImage.objects.create(
                            patient=patient,
                            image=image,
                            description=description
                        )
                        print(f"Saved CT scan image: {ct_image.image.path}")
                        uploaded_count += 1
                    except Exception as img_err:
                        print(f"Error saving image {image.name}: {str(img_err)}")
                        messages.warning(request, f"Error saving image {image.name}: {str(img_err)}")
                
                if uploaded_count > 0:
                    messages.success(request, f'Successfully uploaded {uploaded_count} CT scan image(s) for {patient.name}.')
                    return redirect('patientsystem:patient_detail', patient_id=patient_id)
                else:
                    messages.error(request, 'Failed to upload any images. Please try again.')
                    
            except Exception as e:
                messages.error(request, f'Error processing image uploads: {str(e)}')
        
        # GET request - display the form
        return render(request, 'patientsystem/upload_ct_scan.html', {
            'patient': patient
        })
    except Exception as e:
        messages.error(request, f'Error accessing upload form: {str(e)}')
        return redirect('patientsystem:dashboard')
