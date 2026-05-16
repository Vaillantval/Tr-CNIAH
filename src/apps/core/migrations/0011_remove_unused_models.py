from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_f4_f6_f8_contacts_plainte_certification'),
    ]

    operations = [
        migrations.DeleteModel(name='Banner'),
        migrations.DeleteModel(name='ServiceBlock'),
        migrations.DeleteModel(name='Proposition'),
        migrations.DeleteModel(name='EngineeringBranch'),
    ]
