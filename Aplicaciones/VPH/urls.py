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
from django.urls import include, path
from .views import *


urlpatterns = [
    path('', inicio, name='inicio'),
    path('generar_csv_vp/', generar_csv_vp, name='generar_csv_vp'),
    path('resultado/', resultado, name='resultado'),
    path('informes',informes, name='informes'),
    path('index', index, name='index'),
    path('generar_pdf_persona/<int:numero_de_muestra>/', generar_pdf_persona, name='generar_pdf_persona'),
    path('filtrarExpediente/', filtrarExpediente, name='filtrarExpediente'),
    path('agregar_persona/', agregar_persona, name='agregar_persona'),
    path('salir/', salir, name='salir' ),
    path('guardar_cambio/', guardar_cambio, name='guardar_cambio'),
    path('actualizar_institucion/', actualizar_institucion, name='actualizar_institucion'),
    path('actualizar_depar/', actualizar_depar, name='actualizar_depar'),
    path('actualizar_res/', actualizar_res, name='actualizar_res'),
    path('actualizar_fecha/', actualizar_fecha, name='actualizar_fecha'),
    path('borrar/<int:id_per>/', borrar, name='borrar'),
]
