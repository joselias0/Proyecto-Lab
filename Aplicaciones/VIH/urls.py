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
    path('indexVIH/', indexVIH, name='indexVIH'),
    path('agregar_persona_vih/', agregar_persona_vih, name='agregar_persona_vih'),
    path('generar_csv_vp_vih/', generar_csv_vp_vih, name='generar_csv_vp_vih'),
    path('informes_vih',informes_vih, name='informes_vih'),
    path('generar_pdf_persona_vih/<int:numero_de_muestra>/', generar_pdf_persona_vih, name='generar_pdf_persona_vih'),
    path('filtrarExpediente_vih/', filtrarExpediente_vih, name='filtrarExpediente_vih'),
    path('guardar_cambio_vih/', guardar_cambio_vih, name='guardar_cambio_vih'),
    path('actualizar_institucion_vih/', actualizar_institucion_vih, name='actualizar_institucion_vih'),
    path('actualizar_depar_vih/', actualizar_depar_vih, name='actualizar_depar_vih'),
    path('actualizar_res_vih/', actualizar_res_vih, name='actualizar_res_vih'),
    path('actualizar_fecha_vih/', actualizar_fecha_vih, name='actualizar_fecha_vih'),
    path('borrar_vih/<int:id_per>/', borrar_vih, name='borrar_vih'),
]