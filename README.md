# Smart Clinic & Appointment Booking Platform

A full-stack clinic appointment booking system built with Django and PostgreSQL, featuring role-based access control and an integrated Agentic AI assistant that performs real backend actions (searching doctors, booking, viewing, and cancelling appointments) through controlled tool-calling with Google Gemini.

## 1. Project Overview

Smart Clinic digitizes the appointment booking process for a small clinic. Patients can browse doctors by specialization, book and manage their own appointments, and interact with an AI assistant that can search for doctors and book/cancel appointments on their behalf through a secure, permission-checked tool-calling flow — not as a generic chatbot.

## 2. Features

- User registration, login, and logout
- Role-based access control: Admin, Doctor, Patient, Receptionist
- Doctor and specialization management (via Django Admin)
- Public doctor listing with specialization and consultation fee
- Appointment booking with double-booking prevention
- Patient appointment history with status tracking (Pending, Confirmed, Completed, Cancelled)
- Agentic AI chat assistant (Gemini tool-calling): search doctors, view my appointments, book an appointment, cancel an appointment
- Identity-bound AI actions: the agent always acts as the authenticated user, never a user identity supplied by the model

## 3. Technology Stack

- **Backend:** Python 3.12+, Django (MVT architecture)
- **Database:** PostgreSQL
- **Frontend:** HTML5, CSS3, JavaScript (ES6+, fetch API)
- **AI:** Google Gemini API (function/tool calling)
- **Config:** python-decouple (.env-based configuration)

## 4. Requirements

- Python 3.12+
- PostgreSQL 14+
- Git
- A Google Gemini API key (free tier available at https://aistudio.google.com/apikey)

## 5. Environment Setup

```bash
git clone https://github.com/AhmedElCoder26/smart-clinic-graduation-project.git
cd smart-clinic-graduation-project
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt