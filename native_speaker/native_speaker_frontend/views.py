from django.shortcuts import render

# Create your views here.
def get_record_view(request):
    return render(request, "main.html")


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import whisper
# import llama_cpp
# import Levenshtein  # Biblioteka do mierzenia różnic w tekście
# from .models import Nagranie

# import os

# from pathlib import Path
# import llama_cpp

# # Pobranie katalogu głównego projektu
# BASE_DIR = Path(__file__).resolve().parent.parent  # Przechodzi dwa poziomy wyżej
# from pathlib import Path

# MODEL_PATH = Path(r"C:\Users\Szymon\Desktop\Programy\native_speaker\native_speaker\models\llama-2-7b-chat.Q2_K.gguf")

# print("Ścieżka do modelu:", MODEL_PATH)
# print("Czy plik istnieje?", MODEL_PATH.exists())

# # Ścieżka do modelu
# MODEL_PATH = BASE_DIR / "models" / "llama-2-7b-chat.Q2_K.gguf"

# # Wczytanie modelu
# llm = llama_cpp.Llama(model_path=str(MODEL_PATH))

# # BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # To wskazuje na katalog "native_speaker_frontend"
# # PROJECT_DIR = os.path.dirname(BASE_DIR).parent  # To przesuwa nas do katalogu głównego "native_speaker"

# # # Poprawna ścieżka do modelu
# # MODEL_PATH = os.path.join(PROJECT_DIR, "models", "llama-2-7b-chat.ggmlv3.q2_K.bin")

# # # Wczytanie modelu AI
# # llm = llama_cpp.Llama(model_path=MODEL_PATH)
# # # model_path = "models/llama-2-7b-chat.ggmlv3.q2_K.bin"
# # # llm = llama_cpp.Llama(model_path=model_path)

# @csrf_exempt
# def upload_audio(request):
#     print(f"Zapytanie POST: {request.method}")  # Sprawdzamy metodę HTTP
#     if request.method == 'POST' and request.FILES.get('audio'):
#         print(f"Plik audio: {request.FILES['audio']}")
#         print("1")
#         plik_audio = request.FILES['audio']
#         nagranie = Nagranie.objects.create(plik_audio=plik_audio)
#         print("2")
#         # **Transkrypcja audio**
#         print("Ładowanie modelu Whisper...")
#         model = whisper.load_model("base")
#         print("Model załadowany. Rozpoczynamy transkrypcję.")
#         result = model.transcribe(nagranie.plik_audio.path, language="hr")
#         print(f"Transkrypcja zakończona: {result['text']}")
#         nagranie.save()
#         print("3")
#         # **Poproś AI o poprawną wersję zdania**
#         # prompt_correct = f"Popraw to zdanie gramatycznie, ale nie zmieniaj znaczenia: {nagranie.transkrypcja}"
#         # poprawne_zdanie = llm(prompt_correct)['choices'][0]['text'].strip()
#         # print("4")
#         # # **Porównaj poprawność wypowiedzi użytkownika**
#         # accuracy = 1 - (Levenshtein.distance(nagranie.transkrypcja, poprawne_zdanie) / max(len(poprawne_zdanie), 1))
#         # accuracy_percentage = round(accuracy * 100, 2)
#         # print("5")
#         # **AI daje feedback na temat błędów**
#         # prompt_feedback = f"Użytkownik powiedział: {nagranie.transkrypcja}. Jakie są w tym błędy gramatyczne i wymowy?"
#         # feedback = llm(prompt_feedback)['choices'][0]['text'].strip()
#         print("6")
#         # **Odpowiedź AI (kontynuacja rozmowy)**
#         prompt_reply = f"Jesteś nauczycielem chorwackiego. Odpowiedz na zdanie użytkownika: {nagranie.transkrypcja}"
#         response = llm(prompt_reply)['choices'][0]['text'].strip()
#         print("7")
#         return JsonResponse({
#             'transkrypcja': nagranie.transkrypcja,
#             # 'poprawna_wersja': poprawne_zdanie,
#             # 'poprawność': f"{accuracy_percentage}%",
#             # 'ocena': feedback,
#             'odpowiedz_ai': response
#         })

#     return JsonResponse({'error': 'Błędne żądanie'}, status=400)

# import openai
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json

# openai.api_key = "TWOJ_KLUCZ_API"  # Możesz użyć darmowego triala OpenAI

# @csrf_exempt
# def chatbot(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_message = data.get("message", "")

#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": user_message}]
#         )

#         bot_reply = response["choices"][0]["message"]["content"]

#         return JsonResponse({"response": bot_reply})
#     return JsonResponse({"error": "Błędne żądanie"}, status=400)

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import whisper
import os
import g4f  
from gtts import gTTS
from django.conf import settings
from io import BytesIO

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        plik_audio = request.FILES['audio']
        sciezka_audio = os.path.join("media", plik_audio.name)
        
        with open(sciezka_audio, 'wb') as f:
            for chunk in plik_audio.chunks():
                f.write(chunk)

        # **Transkrypcja audio**
        model = whisper.load_model("base")

        result = model.transcribe(sciezka_audio, language="hr")


        transkrypcja = result['text']

        # **Zapisujemy historię rozmowy w sesji**
        if 'chat_history' not in request.session:
            request.session['chat_history'] = []

        request.session['chat_history'].append({"role": "user", "content": transkrypcja})

        request.session['chat_history'] = request.session['chat_history'][-10:]
        # **Tworzymy prompt do AI**
        messages = [{"role": "system", "content": "You are a native speaker from Croatia. \
                  You answer only in Croatian. Correct mistakes in a subtle way, \
                  but also respond as in a conversation. Your response MUST be short \
                  (maximum 15 words). Be very concise. Keep the conversation going and suggest new words \
                  related to the topic."}]
        

        # **Tworzymy prompt do AI**
        messages = request.session['chat_history']
        messages.append({"role": "system", "content": "Zachowuj się jak kolega, proponuj różne tematu, zapytaj o coś czasem. Odpowiadaj tylko w języku angielskim, maksymalnie jednym zdaniem. Jeżeli użytkownik powie coś źle gramatycznie, zapytaj: 'Czy chciałeś powiedzieć: (i tutaj daj poprawioną wersję)'. Jeżeli w następnej wiadomości użytkownik powe poprawnie, wtedy odpowiedz na zadane wcześniej pytanie."})


        odpowiedz_ai = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=40  

        )

        # **Zapisujemy odpowiedź AI w historii**
        request.session['chat_history'].append({"role": "assistant", "content": odpowiedz_ai})
        request.session.modified = True  # Zapisujemy zmiany w sesji

        # **Tworzenie pliku audio**

        tts = gTTS(text=odpowiedz_ai, lang='hr')


        audio_path = os.path.join(settings.MEDIA_ROOT, "response.mp3")
        tts_io = BytesIO()
        tts.write_to_fp(tts_io)
        tts_io.seek(0)

        with open(audio_path, "wb") as f:
            f.write(tts_io.read())

        audio_url = os.path.join(settings.MEDIA_URL, "response.mp3")

        return JsonResponse({
            'transkrypcja': transkrypcja,
            'odpowiedz_ai': odpowiedz_ai,
            'audio_url': audio_url  
        })

    return JsonResponse({'error': 'Błędne żądanie'}, status=400)


"""PONIZEJ OSTATNIA DZIALAJACA WERSJA
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import whisper
import os
import g4f  # Dodajemy g4f
from gtts import gTTS
import tempfile
from django.conf import settings

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        plik_audio = request.FILES['audio']
        sciezka_audio = os.path.join("media", plik_audio.name)
        
        with open(sciezka_audio, 'wb') as f:
            for chunk in plik_audio.chunks():
                f.write(chunk)

        # **Transkrypcja audio**
        model = whisper.load_model("base")
        result = model.transcribe(sciezka_audio, language="hr")
        transkrypcja = result['text']
        prompt = f"{transkrypcja}\nOdpowiedz maksymalnie jednym zdaniem. Odpowiedz w języku"
        # **Przekazujemy transkrypcję do chatu AI z ograniczeniem długości odpowiedzi**
        odpowiedz_ai = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100  # Ograniczenie długości odpowiedzi (maks. 100 tokenów)
        )
        print("Odpowiedź AI:", odpowiedz_ai)

        audio_path = os.path.join(settings.MEDIA_ROOT, "tmpwdhxtg1e.mp3")

        # **Tworzymy mowę z odpowiedzi chatbota za pomocą gTTS**
        tts = gTTS(text=odpowiedz_ai, lang='hr')  # Używamy języka chorwackiego
        audio_path = os.path.join(settings.MEDIA_ROOT, "response.mp3")
        
        # Zapisz plik MP3
        tts.save(audio_path)
        
        # Upewnij się, że plik został zapisany
        if not os.path.exists(audio_path):
            return JsonResponse({'error': 'Błąd zapisu pliku MP3'}, status=500)

        # Przekazujemy odpowiedź z chatbotem oraz URL pliku MP3
        audio_url = os.path.join(settings.MEDIA_URL, "response.mp3")


        return JsonResponse({
            'transkrypcja': transkrypcja,
            'odpowiedz_ai': odpowiedz_ai,
            'audio_url': audio_url  # Zwracamy URL do pliku audio
        })

    return JsonResponse({'error': 'Błędne żądanie'}, status=400)"
    """