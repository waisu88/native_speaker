from django.db import models


class Nagranie(models.Model):
    plik_audio = models.FileField(upload_to='nagrania/')
    transkrypcja = models.TextField(blank=True, null=True)
    data_dodania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Nagranie {self.id} - {self.data_dodania}'