# Generated by Django 3.0.3 on 2020-02-25 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('troop', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={'ordering': ('date',), 'verbose_name': 'attendance', 'verbose_name_plural': 'attendance'},
        ),
        migrations.AddField(
            model_name='attendance',
            name='is_main',
            field=models.BooleanField(default=False, verbose_name='main day'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='age_section',
            field=models.CharField(blank=True, choices=[(None, 'no section'), ('beaver', 'beaver'), ('cub', 'cub'), ('scout', 'scout'), ('venturer', 'venturer'), ('rover', 'rover')], max_length=16, verbose_name='age section'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='gender',
            field=models.CharField(choices=[('male', 'male'), ('female', 'female'), ('diverse', 'diverse')], default='diverse', max_length=16, verbose_name='gender'),
        ),
    ]
