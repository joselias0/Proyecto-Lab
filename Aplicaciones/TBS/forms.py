from django import forms
from .models import *


class BuscarPersonaForm(forms.Form):
    class Meta:
        model = Persona_TBS
        fields = ['numero_de_muestra']

class ExpedienteForm(forms.ModelForm):
    class Meta:
        model = Persona_TBS
        fields = ['expediente']