# Generated by Django 4.2.18 on 2025-02-05 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_payment_rate_tariff_telegramuser_email_and_more'),
        ('indexer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rate',
            name='from_contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates_from', to='indexer.contract'),
        ),
        migrations.AddField(
            model_name='rate',
            name='to_contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates_to', to='indexer.contract'),
        ),
        migrations.AddField(
            model_name='payment',
            name='tariff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='bot.tariff'),
        ),
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='bot.telegramuser'),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together={('from_contract', 'to_contract')},
        ),
    ]
