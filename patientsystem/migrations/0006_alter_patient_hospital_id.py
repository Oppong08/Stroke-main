from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('patientsystem', '0005_populate_hospital_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='hospital_id',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
    ] 