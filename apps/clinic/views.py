from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor, Appointment, Patient


def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'clinic/doctor_list.html', {'doctors': doctors})


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    patient, created = Patient.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        notes = request.POST.get('notes', '')

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            notes=notes,
            booked_by=request.user
        )
        messages.success(request, 'Appointment booked successfully!')
        return redirect('my_appointments')

    return render(request, 'clinic/book_appointment.html', {'doctor': doctor})


@login_required
def my_appointments(request):
    patient = Patient.objects.filter(user=request.user).first()
    appointments = Appointment.objects.filter(patient=patient) if patient else []
    return render(request, 'clinic/my_appointments.html', {'appointments': appointments})