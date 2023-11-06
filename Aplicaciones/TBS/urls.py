"""
URL configuration for VPHWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *

urlpatterns = [
    path('indexTBS/', indexTBS, name='indexTBS'),
    path('agregar_persona_tbs/', agregar_persona_tbs, name='agregar_persona_tbs'),
    path('generar_csv_vp_tbs/', generar_csv_vp_tbs, name='generar_csv_vp_tbs'),
    path('informes_tbs/',informes_tbs, name='informes_tbs'),
    path('generar_pdf_persona_tbs/<int:numero_de_muestra>/', generar_pdf_persona_tbs, name='generar_pdf_persona_tbs'),
    path('filtrarExpediente_tbs/', filtrarExpediente_tbs, name='filtrarExpediente_tbs'),
    path('guardar_cambio_tbs/', guardar_cambio_tbs, name='guardar_cambio_tbs'),
    path('actualizar_institucion_tbs/', actualizar_institucion_tbs, name='actualizar_institucion_tbs'),
    path('actualizar_depar_tbs/', actualizar_depar_tbs, name='actualizar_depar_tbs'),
    path('actualizar_res_tbs/', actualizar_res_tbs, name='actualizar_res_tbs'),
    path('actualizar_fecha_tbs/', actualizar_fecha_tbs, name='actualizar_fecha_tbs'),
    path('borrar_tbs/<int:id_per>/', borrar_tbs, name='borrar_tbs'),
]