from django.contrib import admin
from .models import Specialization, Doctor, Patient, DoctorAvailability, Appointment

admin.site.register(Specialization)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(DoctorAvailability)
admin.site.register(Appointment)