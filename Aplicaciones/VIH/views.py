import openpyxl
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Aplicaciones.VIH.forms import *
from .models import *
from django.http import Http404, HttpResponse, HttpResponseNotFound, JsonResponse
from datetime import date, datetime
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


@login_required
@csrf_protect
def indexVIH(request):

    PersonaL = Persona_VIH.objects.all()
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    depar= departamento_vih.objects.all().order_by('nombreDep') 
    result=resultado_vih.objects.all()
    resulta=resultado_per_vih.objects.all()

    if request.user.has_perm('VIH.can_view_persona_vih'):
        return render(request, 'gestionVIH.html', {'Persona_VIH': PersonaL, 'Institucion_vih':Insti, 'departamento_vih': depar, 'resultado_per_vih': resulta, 'resultado_vih': result})
    else:
        error_message = 'No tienes permiso para gestionar las pruebas VIH'
        return render(request, 'inicio.html', {'error_message' :error_message})



@login_required
@csrf_protect
def agregar_persona_vih(request):
    PersonaL = Persona_VIH.objects.all()
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    depar = departamento_vih.objects.all().order_by('nombreDep') 
    result = resultado_vih.objects.all()
    res_per = resultado_per_vih.objects.all()
    
    if request.method == 'POST':
        nombre = request.POST['nombre']
        edad = request.POST['edad']
        direccion = request.POST['direccion']
        dui = request.POST['dui']
        expediente = request.POST['expediente']
        id_de=request.POST['id_dep']
        id_depar=departamento_vih.objects.get(pk=id_de)
        resultado_id = request.POST['resultado']
        institucion_id = request.POST['institucion']
        institucion = Institucion_vih.objects.get(pk=institucion_id)  
        

        persona = Persona_VIH.objects.create(
            nombre=nombre,
            edad=edad,
            direccion=direccion,
            dui=dui,
            expediente=expediente,
            id_dep=id_depar,
            institucion_id=institucion,
            fecha=None
        )

        persona.save()
        
        persona_id = persona.numero_de_muestra
        persona_inst = Persona_VIH.objects.get(pk=persona_id)
        resultado_add = resultado_vih.objects.get(pk=resultado_id)
        resultado_save=resultado_per_vih.objects.create(
            numero_de_muestra=persona_inst,
            id_res=resultado_add
        )

        return render(request, 'gestionVIH.html', {'Persona_VIH': PersonaL, 'Institucion_vih':Insti, 'departamento_vih': depar, 'resultado_per_vih': res_per, 'resultado_vih': result})  

    if request.user.has_perm('VIH.can_view_persona_vih'):
        if request.user.has_perm('VIH.can_add_persona'):
            return render(request, 'agregarPerVIH.html', {'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_vih': result})
        else:
            error_message = 'No tienes permiso para agregar pruebas VIH'
            return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
    else:
        error_message = 'No tienes permiso para agregar pruebas VIH'
        return render(request, 'inicio.html', {'error_message' :error_message})



@login_required
@csrf_protect
def informes_vih(request):
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    
    if request.user.has_perm('VIH.can_view_persona_vih'):
        return render(request, 'resul_vih.html', {'Institucion_vih':Insti})
    else:
        error_message = 'No tienes permiso para gestionar las pruebas VIH'
        return render(request, 'inicio.html', {'error_message' :error_message})



@login_required
@csrf_protect
def generar_csv_vp_vih(request):
    if request.method == 'POST': 
        Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        institucion_id = request.POST.get('institucion')
        btn = request.POST.get('action')
        PersonaF = Persona_VIH.objects.all()
        result=resultado_vih.objects.all()
        resulta=resultado_per_vih.objects.all()
        
        if institucion_id=="None":
            institucion_id=""
        else:
            if institucion_id:
                PersonaF = PersonaF.filter(institucion_id=institucion_id)

        if fecha_inicio and fecha_fin:
            PersonaF = PersonaF.filter(fecha__range=[fecha_inicio, fecha_fin])

        if fecha_inicio > fecha_fin:
            error_message = "La fecha de inicio no puede ser mayor que la fecha final."
            return render(request, 'resul_vih.html', {'error_message': error_message, 'Institucion_vih': Insti, 'Persona_VIH': PersonaF})

        if btn == 'vista_previa':
            return render(request, 'resul_vih.html', {'Institucion_vih': Insti, 'Persona_VIH': PersonaF, 'resultado_vih':result, 'resultado_per_vih':resulta})
        elif btn == 'generar_informe':
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = 'Personas'

            sheet.append(['Ministerio de Salud'])
            sheet.append(['Viceministerio de Servicio de Salud'])
            sheet.append(['Unidad Nacional para la Prevención y Control del Cáncer'])
            sheet.append([])  
            sheet.append(['Número de Muestra', 'Nombre', 'Edad', 'Dirección', 'DUI', 'Expediente', 'Departamento', 'Resultado', 'Nombre de Institución', 'Fecha'])

            for persona in PersonaF:
                resultados_per = resultado_per_vih.objects.filter(numero_de_muestra=persona)

                for resul_per in resultados_per:
                    resultados = resul_per.id_res

                    row = [
                        persona.numero_de_muestra,
                        persona.nombre,
                        persona.edad,
                        persona.direccion,
                        persona.dui,
                        persona.expediente,
                        persona.id_dep.nombreDep,
                        resultados.resultado,
                        persona.institucion_id.nombreInstitucion,
                        persona.fecha.strftime('%d/%m/%Y'),
                    ]
                    sheet.append(row)

        
            for columnaP in sheet.columns:
                maximo = 0
                columnas = columnaP[0].column_letter
                for celda in columnaP:
                    try:
                        if len(str(celda.value)) > maximo:
                            maximo = len(celda.value)
                    except:
                        pass
                adjusted_width = (maximo + 2)
                sheet.column_dimensions[columnas].width = adjusted_width

        
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="personas.xlsx"'

        
            workbook.save(response)

            return response
        
    
    return render (request,'resul_vih.html',{'Institucion_vih':Insti,'Persona_VIH':PersonaF})

@login_required
@csrf_protect
def generar_pdf_persona_vih(request, numero_de_muestra):

    if request.method == 'GET':
        form = BuscarPersonaForm(request.GET)
        try:
            persona = Persona_VIH.objects.get(numero_de_muestra=numero_de_muestra)
            resultado_per = resultado_per_vih.objects.get(numero_de_muestra=persona)
            resultado = resultado_vih.objects.get(pk=resultado_per.id_res.id_res)
        except Persona_VIH.DoesNotExist:
            raise Http404("Persona no encontrada")

        if form.is_valid():
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="resultado_{numero_de_muestra}_vih.pdf'

            doc = SimpleDocTemplate(response, pagesize=letter)
            elements = []

            # Crear un párrafo con los datos de la persona
            styles = getSampleStyleSheet()
            style = styles["Normal"]
            image_path = "Aplicaciones/img/logo.png"
            img = Image(image_path)
            img.drawHeight = 80 
            img.drawWidth = 200
            elements.append(img)
            

            # Estilo para centrar solo la fecha
            centered_style = ParagraphStyle(name='CenteredStyle', alignment=1)
            
            centered_text= f"Ministerio de salud<br/>"
            centered_text+= f"Viceministerio de Servicio de Salud<br/>"
            centered_text+= f"Unidad Nacional para la Prevención y Control del Cáncer<br/>"
            centered_para = Paragraph(centered_text, centered_style)
            elements.append(centered_para)
            text = f"<br/><b>Nombre:</b> {persona.nombre} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Edad:</b> {persona.edad}<br/>"
            text += f"<br/><b>DUI:</b> {persona.dui} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Expediente:</b> {persona.expediente}<br/>"
            text += f"<br/><b>Nombre de Institución:</b> {persona.institucion_id.nombreInstitucion} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Resultado: <b>{resultado.resultado}</b><br/>"
            if persona.fecha is not None:
                text += f"<br/><b>Fecha:</b> {persona.fecha.strftime('%d/%m/%Y')}<br/>"
            else:
                text += "<br/><b>Fecha:</b> N/A<br/>"
            text += f"<br/><b>Tipo de prueba:</b> VIH "
            para = Paragraph(text, style)
            elements.append(para)
            doc.build(elements)

            return response

    return HttpResponse("Error: No se pudo generar el PDF")


@login_required
@csrf_protect
def filtrarExpediente_vih(request):
    PersonaL = Persona_VIH.objects.all()
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    depar= departamento_vih.objects.all().order_by('nombreDep') 
    result = resultado_vih.objects.all()
    res_per = resultado_per_vih.objects.all()
    

    if request.method == 'POST':
        form = ExpedienteForm(request.POST)
        if form.is_valid():
            expediente = form.cleaned_data['expediente']
            PersonaL = Persona_VIH.objects.filter(expediente__startswith=expediente)
            return render(request, 'gestionVIH.html', {'Persona_VIH': PersonaL, 'Institucion_vih':Insti, 'departamento_vih': depar, 'resultado_vih': result, 'resultado_per_vih':res_per})
    return HttpResponse('El filtrado no ha sido realizado')

"""
PersonaL = Persona_VIH.objects.all()
Insti = Institucion_vih.objects.all()
depar= departamento_vih.objects.all()
result = resultado_vih.objects.all()
res_per = resultado_per_vih.objects.all()
if request.user.has_perm('VIH.can_change_persona'):
        return render(request, 'agregarPersona.html', {'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_vih': result})
    else:
        error_message = 'No tienes permiso para agregar pruebas VIH'
        return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
"""

"""
if request.user.has_perm('VIH.can_change_res_per'):
        return render(request, 'agregarPersona.html', {'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_vih': result})
    else:
        error_message = 'No tienes permiso para agregar pruebas VPH'
        return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
"""
@login_required
@csrf_protect
def guardar_cambio_vih(request):
    PersonaL = Persona_VIH.objects.all()
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    depar= departamento_vih.objects.all().order_by('nombreDep') 
    result = resultado_vih.objects.all()
    res_per = resultado_per_vih.objects.all()
    if request.user.has_perm('VIH.can_change_persona'):
        if request.method == 'POST':
        
            persona_id = request.POST.get('id')
            campo = request.POST.get('campo')
            valor = request.POST.get('valor')
            fecha2 = request.POST.get('fecha')
            try:
                persona = Persona_VIH.objects.get(numero_de_muestra=persona_id)
                valor_actual = getattr(persona, campo)
                
                if valor_actual != valor:
                    if campo == 'nombre':
                        persona.nombre = valor
                    elif campo == 'edad':
                        persona.edad = int(valor)
                    elif campo == 'direccion':
                        persona.direccion = valor
                    elif campo == 'dui':
                        persona.dui = valor
                    elif campo == 'expediente':
                        persona.expediente = valor
                    elif campo == 'fecha':
                        fecha2 = datetime.strptime(valor, '%d/%m/%y')
                        persona.fecha = fecha2
                    
                    persona.save()
                    return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Registro no encontrado'})
        return JsonResponse({'message': ''})
    else:
        error_message = 'No tienes permiso para agregar pruebas VIH'
        return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
    
    

@login_required
@csrf_protect
def actualizar_institucion_vih(request):
    PersonaL = Persona_VIH.objects.all()
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    depar= departamento_vih.objects.all().order_by('nombreDep') 
    result = resultado_vih.objects.all()
    res_per = resultado_per_vih.objects.all()
    if request.user.has_perm('VIH.can_change_persona'):
        if request.method == 'POST':
            try:
                persona_id = int(request.POST.get('id_per'))
                institucion_id = int(request.POST.get('id_ins'))
                persona = Persona_VIH.objects.get(numero_de_muestra=persona_id)
                
                institucion = Institucion_vih.objects.get(pk=institucion_id)
                persona.institucion_id = institucion
                persona.save()

                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona_VIH.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion_vih.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})

        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para agregar pruebas VIH'
        return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
    

@login_required
@csrf_protect
def actualizar_depar_vih(request):
    PersonaL = Persona_VIH.objects.all()
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    depar= departamento_vih.objects.all().order_by('nombreDep') 
    result = resultado_vih.objects.all()
    res_per = resultado_per_vih.objects.all()
    if request.user.has_perm('VIH.can_change_persona'):
        if request.method == 'POST':
            try:
                pers_id = int(request.POST.get('id_per2'))
                depar_id = int(request.POST.get('id_dep'))
                persona = Persona_VIH.objects.get(numero_de_muestra=pers_id)
                depart = departamento_vih.objects.get(pk=depar_id)
                persona.id_dep = depart
                persona.save()

                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona_VIH.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion_vih.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})

        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para agregar pruebas VIH'
        return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
    

@login_required
@csrf_protect
def actualizar_fecha_vih(request):
    PersonaL = Persona_VIH.objects.all()
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    depar= departamento_vih.objects.all().order_by('nombreDep') 
    result = resultado_vih.objects.all()
    res_per = resultado_per_vih.objects.all()
    if request.user.has_perm('VIH.can_change_persona'):
        if request.method == 'POST':
            try:
                pers_id = int(request.POST.get('id_per4'))
                fecha_nueva = request.POST.get('fecha')

                try:
                    persona = Persona_VIH.objects.get(numero_de_muestra=pers_id)
                except ObjectDoesNotExist:
                    return HttpResponseNotFound('Registro de Persona no encontrado')

                if fecha_nueva is None:
                    persona.fecha = fecha_nueva
                    persona.save()
                
                valor_actual = persona.fecha
                fecha_nueva = fecha_nueva.replace('-', '/')

                try:
                    fecha_obj = datetime.strptime(fecha_nueva, '%Y/%m/%d')
                    fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                    fecha2 = datetime.strptime(fecha_formateada, '%d/%m/%Y')
                except ValueError:
                    return JsonResponse({'error': 'Fecha no válida'})

                if valor_actual != fecha2:
                    persona.fecha = fecha2
                    persona.save()  # Save the updated date to the database

                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except ValueError:
                return JsonResponse({'error': 'ID de Persona no válido'})
        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para agregar pruebas VIH'
        return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
    


@login_required
@csrf_protect
def actualizar_res_vih(request):
    PersonaL = Persona_VIH.objects.all()
    Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
    depar= departamento_vih.objects.all().order_by('nombreDep') 
    result = resultado_vih.objects.all()
    res_per = resultado_per_vih.objects.all()
    if request.user.has_perm('VIH.can_change_res_per'):
        if request.method == 'POST':
            try:
                persona_id = int(request.POST.get('id_per'))
                resultado_id = int(request.POST.get('id_res'))
                resultado_per_objeto = resultado_per_vih.objects.get(numero_de_muestra_id=persona_id)
                nuevo_res=resultado_vih.objects.get(id_res=resultado_id)
                resultado_per_objeto.id_res = nuevo_res
                resultado_per_objeto.save()
                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona_VIH.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion_vih.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})

        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para agregar pruebas VPH'
        return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
    


@login_required
@csrf_protect
def borrar_vih(request, id_per):
    try:
        PersonaL = Persona_VIH.objects.all()
        Insti = Institucion_vih.objects.all().order_by('nombreInstitucion')
        depar = departamento_vih.objects.all().order_by('nombreDep') 
        result = resultado_vih.objects.all()
        res_per = resultado_per_vih.objects.all()
        if request.user.has_perm('VIH.can_delete_persona'):
            p_delete = Persona_VIH.objects.get(numero_de_muestra=id_per)
            p_delete.delete()
            return render(request, 'gestionVIH.html', {'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
        else:
            error_message = 'No tienes permiso para eliminar pruebas VIH'
            return render(request, 'gestionVIH.html', {'error_message' :error_message, 'Persona_VIH': PersonaL, 'Institucion_vih': Insti, 'departamento_vih': depar, 'resultado_per_vih':res_per, 'resultado_vih':result})
    except:
        return JsonResponse({'error': 'El registro no ha sido borrado'})
    

