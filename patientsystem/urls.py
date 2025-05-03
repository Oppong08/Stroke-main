from django.urls import path
from . import views

app_name = 'patientsystem'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('patient/new/', views.new_patient, name='new_patient'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patient/<int:patient_id>/consultation/new/', views.new_consultation, name='new_consultation'),
    path('alerts/', views.alerts, name='alerts'),
    path('alert/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    path('consultations/', views.consultations, name='consultations'),
    path('logout/', views.custom_logout, name='logout'),
    path('patient/<int:patient_id>/edit_vitals/', views.edit_vitals, name='edit_vitals'),
    path('consultation/<int:consultation_id>/edit/', views.edit_consultation, name='edit_consultation'),
    path('patient/<int:patient_id>/edit/', views.edit_patient, name='edit_patient'),
    path('patient/<int:patient_id>/upload_ct_scan/', views.upload_ct_scan, name='upload_ct_scan'),
] 