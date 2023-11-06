
from django import forms
from .models import Persona_VIH


class BuscarPersonaForm(forms.Form):
    class Meta:
        model = Persona_VIH
        fields = ['numero_de_muestra']

class ExpedienteForm(forms.ModelForm):
    class Meta:
        model = Persona_VIH
        fields = ['expediente']