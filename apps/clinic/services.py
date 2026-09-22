from django.db import transaction
from .models import Appointment, Doctor


def find_doctors(specialization_name=None):
    doctors = Doctor.objects.all()
    if specialization_name:
        doctors = doctors.filter(specialization__name__icontains=specialization_name)
    return doctors


def is_slot_taken(doctor, date, time):
    return Appointment.objects.filter(
        doctor=doctor, date=date, time=time
    ).exclude(status=Appointment.Status.CANCELLED).exists()


@transaction.atomic
def create_appointment(patient, doctor, date, time, notes="", booked_by=None):
    if is_slot_taken(doctor, date, time):
        return None, "This time slot is already booked. Please choose another time."

    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        date=date,
        time=time,
        notes=notes,
        booked_by=booked_by or patient.user,
    )
    return appointment, None


def cancel_appointment_for_patient(patient, appointment_id):
    appointment = Appointment.objects.filter(id=appointment_id, patient=patient).first()
    if not appointment:
        return False, "Appointment not found or does not belong to you."
    if appointment.status == Appointment.Status.CANCELLED:
        return False, "This appointment is already cancelled."
    appointment.status = Appointment.Status.CANCELLED
    appointment.save()
    return True, None