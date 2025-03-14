from django.urls import path
from .views import upload_audio, get_record_view

urlpatterns = [
    path('', get_record_view, name='record_view'),
    path('upload/', upload_audio, name='upload_audio'),
]