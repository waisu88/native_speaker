from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import whisper
import os
import g4f  
from gtts import gTTS
from django.conf import settings
from io import BytesIO

# Create your views here.
def get_record_view(request):
    return render(request, "main.html")


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
        result = model.transcribe(sciezka_audio, language="en")
        transkrypcja = result['text']

        # **Zapisujemy historię rozmowy w sesji**
        if 'chat_history' not in request.session:
            request.session['chat_history'] = []

        request.session['chat_history'].append({"role": "user", "content": transkrypcja})

        # **Tworzymy prompt do AI**
        messages = request.session['chat_history']
        messages.append({"role": "system", "content": "Zachowuj się jak kolega, proponuj różne tematu, zapytaj o coś czasem. Odpowiadaj tylko w języku angielskim, maksymalnie jednym zdaniem. Jeżeli użytkownik powie coś źle gramatycznie, zapytaj: 'Czy chciałeś powiedzieć: (i tutaj daj poprawioną wersję)'. Jeżeli w następnej wiadomości użytkownik powe poprawnie, wtedy odpowiedz na zadane wcześniej pytanie."})

        odpowiedz_ai = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=100  
        )

        # **Zapisujemy odpowiedź AI w historii**
        request.session['chat_history'].append({"role": "assistant", "content": odpowiedz_ai})
        request.session.modified = True  # Zapisujemy zmiany w sesji

        # **Tworzenie pliku audio**
        tts = gTTS(text=odpowiedz_ai, lang='en')
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
