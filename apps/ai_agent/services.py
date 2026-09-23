import json
import google.generativeai as genai
from decouple import config
from . import tools
from .prompts import SYSTEM_PROMPT

genai.configure(api_key=config('GEMINI_API_KEY'))

# Tool definitions in the format Gemini expects
TOOL_DEFINITIONS = [
    {
        "name": "get_my_appointments",
        "description": "Get all appointments belonging to the current logged-in patient.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "cancel_appointment",
        "description": "Cancel a specific appointment belonging to the current patient.",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {"type": "integer", "description": "The ID of the appointment to cancel."}
            },
            "required": ["appointment_id"],
        },
    },
    {
        "name": "search_doctors",
        "description": "Search for doctors, optionally filtered by specialization name.",
        "parameters": {
            "type": "object",
            "properties": {
                "specialization_name": {"type": "string", "description": "Specialization to filter by, e.g. Cardiology."}
            },
        },
    },
    {
        "name": "book_appointment",
        "description": "Book an appointment for the current patient with a specific doctor, date and time. Only call this after the user has clearly confirmed the doctor, date and time.",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {"type": "integer", "description": "The ID of the doctor to book with."},
                "date": {"type": "string", "description": "Appointment date in YYYY-MM-DD format."},
                "time": {"type": "string", "description": "Appointment time in HH:MM 24-hour format."},
                "notes": {"type": "string", "description": "Optional notes for the appointment."},
            },
            "required": ["doctor_id", "date", "time"],
        },
    },
]

AVAILABLE_FUNCTIONS = {
    "get_my_appointments": tools.get_my_appointments,
    "cancel_appointment": tools.cancel_appointment,
    "search_doctors": tools.search_doctors,
    "book_appointment": tools.book_appointment,
}


def run_agent(user, user_message):
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=SYSTEM_PROMPT,
        tools=[{"function_declarations": TOOL_DEFINITIONS}],
    )

    chat = model.start_chat()
    response = chat.send_message(user_message)

    # Keep looping as long as Gemini keeps requesting tool calls
    max_turns = 5
    for _ in range(max_turns):
        part = response.candidates[0].content.parts[0]

        if not (hasattr(part, "function_call") and part.function_call and part.function_call.name):
            # No more tool calls, this is the final natural-language answer
            return response.text

        function_name = part.function_call.name
        function_args = dict(part.function_call.args)

        # Identity binding: always inject the real logged-in user
        if function_name == "cancel_appointment":
            result = AVAILABLE_FUNCTIONS[function_name](user, function_args.get("appointment_id"))
        elif function_name == "search_doctors":
            result = AVAILABLE_FUNCTIONS[function_name](function_args.get("specialization_name"))
        elif function_name == "book_appointment":
            result = AVAILABLE_FUNCTIONS[function_name](
                user,
                function_args.get("doctor_id"),
                function_args.get("date"),
                function_args.get("time"),
                function_args.get("notes", ""),
            )
        else:
            result = AVAILABLE_FUNCTIONS[function_name](user)

        # Send the tool result back to Gemini; it may reply with text or ask for another tool
        response = chat.send_message(
            genai.protos.Content(
                parts=[genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=function_name,
                        response={"result": json.dumps(result)}
                    )
                )]
            )
        )

    return "Sorry, I couldn't complete that request after multiple attempts. Please try rephrasing."