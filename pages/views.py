<<<<<<< HEAD
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .services.plantbot import generate_answer
=======
from django.http import HttpResponse
from django.shortcuts import render
>>>>>>> b0548c3294d8b00c66890a6c51f462e421424374

# Create your views here
def home_view(request, *args, **kwargs):
    return render (request, "home.html", {})

def intro_view(request, *args, **kwargs):
    return render (request, "intro.html", {})

def aloevera_view(request, *args, **kwargs):
    return render (request, "aloevera.html", {})

def amla_view(request, *args, **kwargs):
    return render (request, "amla.html", {})

def ashwagandha_view(request, *args, **kwargs):
    return render (request, "ashwagandha.html", {})

def babool_view(request, *args, **kwargs):
    return render (request, "babool.html", {})

def bhringraj_view(request, *args, **kwargs):
    return render (request, "bhringraj.html", {})

def cinnamon_view(request, *args, **kwargs):
    return render (request, "cinnamon.html", {})

def clove_view(request, *args, **kwargs):
    return render (request, "clove.html", {})

def cumin_view(request, *args, **kwargs):
    return render (request, "cumin.html", {})

def curry_view(request, *args, **kwargs):
    return render (request, "curry.html", {})

def eucalyptus_view(request, *args, **kwargs):
    return render (request, "eucalyptus.html", {})

def ginger_view(request, *args, **kwargs):
    return render (request, "ginger.html", {})

def lavender_view(request, *args, **kwargs):
    return render (request, "lavender.html", {})

def mehndi_view(request, *args, **kwargs):
    return render (request, "mehndi.html", {})

def neem_view(request, *args, **kwargs):
    return render (request, "neem.html", {})

def peppermint_view(request, *args, **kwargs):
    return render (request, "peppermint.html", {})

def tulsi_view(request, *args, **kwargs):
    return render (request, "tulsi.html", {})

def turmeric_view(request, *args, **kwargs):
    return render (request, "turmeric.html", {})

<<<<<<< HEAD
@ensure_csrf_cookie
def plantbot_view(request, *args, **kwargs):
    return render(request, "plantbot.html", {})

@require_POST
def plantbot_api(request, *args, **kwargs):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid payload."}, status=400)

    question = payload.get("question", "").strip()
    if not question:
        return JsonResponse({"error": "Please include a question."}, status=400)

    focus = payload.get("focus")
    if isinstance(focus, str):
        focus = focus.strip().lower() or None
    else:
        focus = None

    answer, source = generate_answer(question, focus=focus)
    return JsonResponse({"answer": answer, "source": source})

=======
>>>>>>> b0548c3294d8b00c66890a6c51f462e421424374
