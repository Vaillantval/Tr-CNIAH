from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_fix_historical_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membrecomite',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='comite/'),
        ),
        migrations.AlterField(
            model_name='membrecommission',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='commission/'),
        ),
        migrations.AlterField(
            model_name='membreconseil',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='conseil/'),
        ),
    ]
