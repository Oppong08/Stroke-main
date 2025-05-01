from django.db import migrations

def populate_hospital_ids(apps, schema_editor):
    Patient = apps.get_model('patientsystem', 'Patient')
    for i, patient in enumerate(Patient.objects.all(), start=1001):
        patient.hospital_id = f"P-{i:04d}"
        patient.save()

class Migration(migrations.Migration):

    dependencies = [
        ('patientsystem', '0004_patient_hospital_id_alter_userprofile_role'),
    ]

    operations = [
        migrations.RunPython(populate_hospital_ids),
    ] 