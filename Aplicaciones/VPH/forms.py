from django import forms
from .models import Persona 

class ExpedienteForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['expediente']

class BuscarPersonaForm(forms.Form):
    class Meta:
        model = Persona
        fields = ['numero_de_muestra']

class CSV(forms.Form):
    class Meta:
        model = Persona
        fields = ['fecha']
        fields = ['institucion_id']
