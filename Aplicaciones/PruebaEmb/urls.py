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
    path('indexpEmb/', indexpEmb, name='indexpEmb'),
    path('agregar_persona_pEmb/', agregar_persona_pEmb, name='agregar_persona_pEmb'),
    path('generar_csv_vp_pEmb/', generar_csv_vp_pEmb, name='generar_csv_vp_pEmb'),
    path('informes_pEmb/',informes_pEmb, name='informes_pEmb'),
    path('generar_pdf_persona_pEmb/<int:numero_de_muestra>/', generar_pdf_persona_pEmb, name='generar_pdf_persona_pEmb'),
    path('filtrarExpediente_pEmb/', filtrarExpediente_pEmb, name='filtrarExpediente_pEmb'),
    path('guardar_cambio_pEmb/', guardar_cambio_pEmb, name='guardar_cambio_pEmb'),
    path('actualizar_institucion_pEmb/', actualizar_institucion_pEmb, name='actualizar_institucion_pEmb'),
    path('actualizar_depar_pEmb/', actualizar_depar_pEmb, name='actualizar_depar_pEmb'),
    path('actualizar_res_pEmb/', actualizar_res_pEmb, name='actualizar_res_pEmb'),
    path('actualizar_fecha_pEmb/', actualizar_fecha_pEmb, name='actualizar_fecha_pEmb'),
    path('borrar_pEmb/<int:id_per>/', borrar_pEmb, name='borrar_pEmb'),
]