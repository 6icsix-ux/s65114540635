from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Member

# Signal สำหรับบันทึก Member เมื่อ User ถูกบันทึก
@receiver(post_save, sender=User)
def save_member(sender, instance, **kwargs):
    if hasattr(instance, 'member'):
        instance.member.save()
