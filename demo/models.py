# from typing import Any
#
# from django.contrib.auth import get_user_model
# from django.db import models
# from django.db.models import TextChoices
# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
#
# User = get_user_model()
#
#
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE, null=False)
#     location = models.CharField(max_length=64, blank=True)
#
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender: Any, instance: User, created: bool, **kwargs) -> None:
#     if created or instance.profile is None:
#         UserProfile.objects.create(user=instance)
#     else:
#         instance.profile.save()
#
#
# class Trip(models.Model):
#     name = models.CharField(max_length=255, unique=True)
#     location = models.CharField(max_length=64)
#     starts_on = models.DateField(null=False)
#     ends_on = models.DateField(null=False)
#
#
# class Booking(models.Model):
#     trip = models.ForeignKey(Trip, on_delete=models.RESTRICT, null=False)
#     user_profile = models.ForeignKey(UserProfile, on_delete=models.RESTRICT, null=False)
#     state = models.CharField(max_length=32, blank=False, default="new", choices=[("new", "New"), ("ordered", "Ordered"), ("cancelled", "Cancelled"), ("paid", "Paid")])
#     room_type = models.CharField(max_length=32, blank=False, default="private", choices=[("shared", "Shared"), ("private", "Private"), ("ensuite", "Ensuite")])
#     arrives_on = models.DateField(null=False)
#     leaves_on = models.DateField(null=False)
#
#
# class Notification(models.Model):
#     class NotificationState(TextChoices):
#         UNREAD = "unread"
#         READ = "read"
#         ARCHIVED = "archived"
#         TRASH = "trash"
#
#     user_profile = models.ForeignKey(UserProfile, on_delete=models.RESTRICT, null=False)
#     state = models.CharField(max_length=32, choices=NotificationState.choices, default=NotificationState.UNREAD)
#     content = models.TextField()
