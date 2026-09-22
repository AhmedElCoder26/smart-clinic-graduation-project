from datetime import datetime
from apps.clinic.models import Doctor, Patient, Appointment
from apps.clinic import services as clinic_services


def get_my_appointments(user):
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
    patient = Patient.objects.filter(user=user).first()
    if not patient:
        return {"error": "No patient profile found for this user."}

    success, error = clinic_services.cancel_appointment_for_patient(patient, appointment_id)
    if not success:
        return {"error": error}
    return {"success": f"Appointment #{appointment_id} has been cancelled."}


def search_doctors(specialization_name=None):
    doctors = clinic_services.find_doctors(specialization_name)
    result = []
    for doc in doctors:
        result.append({
            "id": doc.id,
            "name": doc.user.get_full_name() or doc.user.username,
            "specialization": doc.specialization.name if doc.specialization else None,
            "fee": str(doc.consultation_fee),
        })
    return {"doctors": result}


def book_appointment(user, doctor_id, date, time, notes=""):
    """Books an appointment for the current authenticated patient with the given doctor."""
    patient = Patient.objects.filter(user=user).first()
    if not patient:
        return {"error": "No patient profile found for this user."}

    doctor = Doctor.objects.filter(id=doctor_id).first()
    if not doctor:
        return {"error": f"No doctor found with id {doctor_id}."}

    try:
        appt_date = datetime.strptime(date, "%Y-%m-%d").date()
        appt_time = datetime.strptime(time, "%H:%M").time()
    except ValueError:
        return {"error": "Invalid date or time format. Use YYYY-MM-DD and HH:MM."}

    appointment, error = clinic_services.create_appointment(
        patient=patient, doctor=doctor, date=appt_date, time=appt_time,
        notes=notes, booked_by=user
    )
    if error:
        return {"error": error}

    return {
        "success": True,
        "appointment_id": appointment.id,
        "doctor": doctor.user.get_full_name() or doctor.user.username,
        "date": str(appointment.date),
        "time": str(appointment.time),
        "status": appointment.status,
    }