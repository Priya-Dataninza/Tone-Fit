from django.db import models
import random

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Created on {self.created_at} and last updation was on {self.updated_at}."
    

# def generate_otp():
#     return str(random.randint(100000, 999999))


# def send_otp(mobile, otp):
#     # For development (prints OTP in terminal)
#     print(f"OTP for {mobile}: {otp}")

