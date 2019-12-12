# Generated by Django 2.2.8 on 2019-12-12 03:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('match_id', models.IntegerField(primary_key=True, serialize=False)),
                ('country_name', models.CharField(max_length=50)),
                ('league_name', models.CharField(max_length=70)),
                ('match_date', models.DateField()),
                ('match_status', models.CharField(max_length=50, null=True)),
                ('match_time', models.TimeField()),
                ('match_hometeam_name', models.CharField(max_length=70)),
                ('match_hometeam_score', models.IntegerField(null=True)),
                ('match_awayteam_name', models.CharField(max_length=70)),
                ('match_awayteam_score', models.IntegerField(null=True)),
                ('prob_HW', models.FloatField()),
                ('prob_D', models.FloatField()),
                ('prob_AW', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_bet', models.CharField(choices=[('HW', 'Home Win'), ('D', 'Draw'), ('AW', 'Away Win')], max_length=2)),
                ('amount', models.FloatField(default=0)),
                ('game_finished', models.BooleanField(default=False)),
                ('balance', models.FloatField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bets.Game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
