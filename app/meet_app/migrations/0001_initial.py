# Generated by Django 4.2.2 on 2023-06-30 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Participant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("avatar", models.ImageField(upload_to="media/")),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "Мужской"), ("F", "Женский"), ("O", "Другой")],
                        max_length=1,
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
            ],
        ),
    ]
