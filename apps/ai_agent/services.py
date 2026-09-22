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
]

AVAILABLE_FUNCTIONS = {
    "get_my_appointments": tools.get_my_appointments,
    "cancel_appointment": tools.cancel_appointment,
    "search_doctors": tools.search_doctors,
}


def run_agent(user, user_message):
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=SYSTEM_PROMPT,
        tools=[{"function_declarations": TOOL_DEFINITIONS}],
    )

    chat = model.start_chat()
    response = chat.send_message(user_message)

    # Check if Gemini wants to call a tool
    part = response.candidates[0].content.parts[0]

    if hasattr(part, "function_call") and part.function_call.name:
        function_name = part.function_call.name
        function_args = dict(part.function_call.args)

        # Identity binding: always inject the real logged-in user
        if function_name == "cancel_appointment":
            result = AVAILABLE_FUNCTIONS[function_name](user, function_args.get("appointment_id"))
        elif function_name == "search_doctors":
            result = AVAILABLE_FUNCTIONS[function_name](function_args.get("specialization_name"))
        else:
            result = AVAILABLE_FUNCTIONS[function_name](user)

        # Send the tool result back to Gemini to get a natural language answer
        final_response = chat.send_message(
            genai.protos.Content(
                parts=[genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=function_name,
                        response={"result": json.dumps(result)}
                    )
                )]
            )
        )
        return final_response.text

    return response.text