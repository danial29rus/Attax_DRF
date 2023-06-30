from PIL import Image
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from app.settings import watermar_path


class Participant(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другой'),
    ]
    id = models.AutoField(auto_created=True, primary_key=True, verbose_name='id')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='media/')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Match(models.Model):
    participant1 = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='matches_participant1')
    participant2 = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='matches_participant2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Match between {self.participant1} and {self.participant2}'



class Like(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.participant} liked by {self.liked_by}'


@receiver(post_save, sender=Participant)
def add_watermark_to_avatar(sender, instance, created, **kwargs):
    if created:
        watermark_path = watermar_path
        avatar = Image.open(instance.avatar.path)
        watermark = Image.open(watermark_path)
        watermark = watermark.convert("RGBA")
        watermark_width, watermark_height = watermark.size
        watermark = watermark.resize((watermark_width, watermark_height), Image.ANTIALIAS)

        offset = (avatar.width - watermark.width - 10, avatar.height - watermark.height - 10)  # Смещение вниз и вправо
        avatar.paste(watermark, offset, mask=watermark)

        avatar.save(instance.avatar.path)
