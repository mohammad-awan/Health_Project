import os
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from docx import Document
from django.views import View


# @method_decorator(csrf_exempt, name='dispatch')
# class ChatPlaceholderView(View):
#
#     def get(self, request):
#         return render(request, "test_chat.html")
#
#     def post(self, request):
#         try:
#             data = json.loads(request.body.decode("utf-8"))
#             question = data.get("question", "").strip()
#
#             if not question:
#                 return JsonResponse({"response": "Please ask something."})
#
#             file_path = find_matching_file(question)
#             if not file_path:
#                 return JsonResponse({"response": "No information found.", "follow_up": ""})
#
#             text = extract_rephrased_from_docx(file_path)
#             if not text:
#                 return JsonResponse({"response": "Rephrased section not found.", "follow_up": ""})
#
#             categorized = categorize_text(text)
#
#             return JsonResponse({
#                 "response": categorized,
#                 "follow_up": follow_up_question()
#             })
#
#         except Exception as e:
#             return JsonResponse({"error": str(e)})



class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "Ok"})


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_PATH = os.path.join(BASE_DIR, "api/data/DISEASES.docx")


QUESTIONS = [
    ("Disease", "Which disease are you asking about?"),
    ("Symptoms", "What symptoms do you have?"),
    ("Causes", "Do you know the cause or history of this problem?"),
    ("When", "When did these symptoms start?"),
    ("Age", "What is your age?"),
    ("Dosage", "Do you want dosage guidance?"),
]


def parse_docx(path):
    disease_data = {}
    doc = Document(path)
    current_disease = None
    current_section = None

    SECTIONS = {
        "overview",
        "symptoms",
        "causes",
        "why it happens",
        "how it can be reduced",
        "long-term outlook",
        "treatments"
    }

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue


        if text.upper().startswith("DISEASE"):
            if ":" in text:
                current_disease = text.split(":", 1)[1].strip()
            else:
                current_disease = text.strip()

            disease_data[current_disease] = {}
            current_section = None
            continue


        section = text.lower().replace(":", "")
        if section in SECTIONS:
            current_section = section.title()
            disease_data[current_disease][current_section] = ""
            continue


        if current_disease and current_section:
            disease_data[current_disease][current_section] += text + "\n"

    return disease_data


DISEASE_DATA = parse_docx(DOC_PATH)



def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()



@csrf_exempt
def chatbot(request):

    if request.method == "GET":
        return render(request, "chatbot.html")

    try:
        user_msg = request.POST.get("message", "").strip()
        if not user_msg:
            return JsonResponse({"reply": "Please type something."})

        # Init state
        if "chat_state" not in request.session:
            request.session["chat_state"] = {
                "step": 0,
                "answers": {
                    "Product": "Immune Support"
                }
            }

        state = request.session["chat_state"]


        if state["step"] < len(QUESTIONS):
            key, _ = QUESTIONS[state["step"]]
            state["answers"][key] = user_msg
            state["step"] += 1
            request.session.modified = True


        if state["step"] >= len(QUESTIONS):

            disease_name = state["answers"].get("Disease", "")
            match = None

            for d in DISEASE_DATA:
                if normalize_text(d) == normalize_text(disease_name):
                    match = d
                    break

            result = DISEASE_DATA.get(match, {})

            final_data = {
                "answers": state["answers"],
                "disease_info": result
            }

            request.session["chat_state"] = {
                "step": 0,
                "answers": {"Product": "Immune Support"}
            }
            request.session.modified = True

            return JsonResponse({
                "reply": "Here is the complete information based on your answers.",
                "final_data": final_data
            })

        _, next_q = QUESTIONS[state["step"]]
        return JsonResponse({"reply": next_q})

    except Exception as e:
        return JsonResponse({"reply": f"Oops! Error: {str(e)}"})


def backend_view(request):
    state = request.session.get("chat_state", {
        "answers": {"Product": "Immune Support"},
        "step": 0
    })

    return render(request, "backend_view.html", {"data": state["answers"]})



# Errors
def error_404(request, exception):
    return JsonResponse({"error": "Route not found"}, status=404)


def error_500(request):
    return JsonResponse({"error": "Internal server error"}, status=500)





