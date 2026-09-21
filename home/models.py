from django.db import models
import random


# =========================
# USER MODEL (CUSTOM)
# =========================
class User(models.Model):
    mobile = models.CharField(max_length=15, unique=True)

    name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    age = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mobile


# =========================
# OTP MODEL
# =========================
class OTP(models.Model):
    mobile = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mobile} - {self.otp}"

    # optional helper
    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))


# =========================
# ADDRESS MODEL (MULTIPLE)
# =========================
class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    house_no = models.CharField(max_length=100)
    area = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"