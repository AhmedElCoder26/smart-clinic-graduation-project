from datetime import datetime
from apps.clinic.models import Appointment, Doctor, Patient


def get_my_appointments(user):
    """Returns all appointments for the logged-in patient."""
    patient = Patient.objects.filter(user=user).first()
    if not patient:
        return {"error": "No patient profile found for this user."}

    appointments = Appointment.objects.filter(patient=patient)
    result = []
    for appt in appointments:
        result.append({
            "id": appt.id,
            "doctor": appt.doctor.user.get_full_name() or appt.doctor.user.username,
            "date": str(appt.date),
            "time": str(appt.time),
            "status": appt.status,
        })
    return {"appointments": result}


def cancel_appointment(user, appointment_id):
    """Cancels a specific appointment, only if it belongs to the requesting user."""
    patient = Patient.objects.filter(user=user).first()
    if not patient:
        return {"error": "No patient profile found for this user."}

    appointment = Appointment.objects.filter(id=appointment_id, patient=patient).first()
    if not appointment:
        return {"error": "Appointment not found or does not belong to you."}

    appointment.status = Appointment.Status.CANCELLED
    appointment.save()
    return {"success": f"Appointment #{appointment_id} has been cancelled."}


def search_doctors(specialization_name=None):
    """Searches for doctors, optionally filtered by specialization."""
    doctors = Doctor.objects.all()
    if specialization_name:
        doctors = doctors.filter(specialization__name__icontains=specialization_name)

    result = []
    for doc in doctors:
        result.append({
            "id": doc.id,
            "name": doc.user.get_full_name() or doc.user.username,
            "specialization": doc.specialization.name if doc.specialization else None,
            "fee": str(doc.consultation_fee),
        })
    return {"doctors": result}