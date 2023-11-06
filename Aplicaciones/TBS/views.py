import openpyxl
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Aplicaciones.TBS.forms import *
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
def indexTBS(request):

    PersonaL = Persona_TBS.objects.all()
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    depar= departamento_tbs.objects.all().order_by('nombreDep') 
    result=resultado_tbs.objects.all()
    resulta=resultado_per_tbs.objects.all()

    
    if request.user.has_perm('TBS.can_view_persona'):
        return render(request, 'gestionTBS.html', {'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': resulta, 'resultado_tbs': result})
    else:
        error_message = 'No tienes permiso para gestionar las pruebas tuberculosis'
        return render(request, 'inicio.html', {'error_message' :error_message})



@login_required
@csrf_protect
def agregar_persona_tbs(request):
    PersonaL = Persona_TBS.objects.all()
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    depar = departamento_tbs.objects.all().order_by('nombreDep') 
    result = resultado_tbs.objects.all()
    res_per = resultado_per_tbs.objects.all()
    
    if request.method == 'POST':
        nombre = request.POST['nombre']
        edad = request.POST['edad']
        direccion = request.POST['direccion']
        dui = request.POST['dui']
        expediente = request.POST['expediente']
        id_de=request.POST['id_dep']
        id_depar=departamento_tbs.objects.get(pk=id_de)
        resultado_id = request.POST['resultado']
        institucion_id = request.POST['institucion']
        institucion = Institucion_tbs.objects.get(pk=institucion_id)  
        

        persona = Persona_TBS.objects.create(
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
        persona_inst = Persona_TBS.objects.get(pk=persona_id)
        resultado_add = resultado_tbs.objects.get(pk=resultado_id)
        resultado_save=resultado_per_tbs.objects.create(
            numero_de_muestra=persona_inst,
            id_res=resultado_add
        )

        return render(request, 'gestionTBS.html', {'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})  
    
    if request.user.has_perm('TBS.can_view_persona'):
        if request.user.has_perm('TBS.can_add_persona'):
            return render(request, 'agregarPerTBS.html', {'Institucion_tbs': Insti, 'departamento_tbs': depar, 'resultado_tbs': result})
        else:
            error_message = 'No tienes permiso para agregar las pruebas tuberculosis'
            return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})
    else:
        error_message = 'No tienes permiso para agregar pruebas tuberculosis'
        return render(request, 'inicio.html', {'error_message' :error_message})
    



@login_required
@csrf_protect
def informes_tbs(request):
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    if request.user.has_perm('TBS.can_view_persona'):
        return render(request, 'resul_tbs.html', {'Institucion_tbs':Insti})
    else:
        error_message = 'No tienes permiso para gestionar las pruebas tuberculosis'
        return render(request, 'inicio.html', {'error_message' :error_message})



@login_required
@csrf_protect
def generar_csv_vp_tbs(request):
    if request.method == 'POST': 
        Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        institucion_id = request.POST.get('institucion')
        btn = request.POST.get('action')
        PersonaF = Persona_TBS.objects.all()
        result=resultado_tbs.objects.all()
        resulta=resultado_per_tbs.objects.all()
        
        if institucion_id=="None":
            institucion_id=""
        else:
            if institucion_id:
                PersonaF = PersonaF.filter(institucion_id=institucion_id)

        if fecha_inicio and fecha_fin:
            PersonaF = PersonaF.filter(fecha__range=[fecha_inicio, fecha_fin])

        if fecha_inicio > fecha_fin:
            error_message = "La fecha de inicio no puede ser mayor que la fecha final."
            return render(request, 'resul_tbs.html', {'error_message': error_message, 'Institucion_tbs': Insti, 'Persona_TBS': PersonaF})

        if btn == 'vista_previa':
            return render(request, 'resul_tbs.html', {'Institucion_tbs': Insti, 'Persona_TBS': PersonaF, 'resultado_tbs':result, 'resultado_per_tbs':resulta})
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
                resultados_per = resultado_per_tbs.objects.filter(numero_de_muestra=persona)

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
        
    
    return render (request,'resul_tbs.html',{'Institucion_tbs':Insti,'Persona_TBS':PersonaF})




@login_required
@csrf_protect
def generar_pdf_persona_tbs(request, numero_de_muestra):

    if request.method == 'GET':
        form = BuscarPersonaForm(request.GET)
        try:
            persona = Persona_TBS.objects.get(numero_de_muestra=numero_de_muestra)
            resultado_per = resultado_per_tbs.objects.get(numero_de_muestra=persona)
            resultado = resultado_tbs.objects.get(pk=resultado_per.id_res.id_res)
        except Persona_TBS.DoesNotExist:
            raise Http404("Persona no encontrada")

        if form.is_valid():
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="resultado_{numero_de_muestra}_tbs.pdf'

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
            text += f"<br/><b>Tipo de prueba:</b> Tuberculosis "
            para = Paragraph(text, style)
            elements.append(para)
            doc.build(elements)

            return response

    return HttpResponse("Error: No se pudo generar el PDF")


@login_required
@csrf_protect
def filtrarExpediente_tbs(request):
    PersonaL = Persona_TBS.objects.all()
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    depar= departamento_tbs.objects.all().order_by('nombreDep') 
    result = resultado_tbs.objects.all()
    res_per = resultado_per_tbs.objects.all()
    if request.method == 'POST':
        form = ExpedienteForm(request.POST)
        if form.is_valid():
            expediente = form.cleaned_data['expediente']
            PersonaL = Persona_TBS.objects.filter(expediente__startswith=expediente)
            return render(request, 'gestionTBS.html', {'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_tbs': result, 'resultado_per_tbs':res_per})
    return HttpResponse('El filtrado no ha sido realizado')

"""
if request.user.has_perm('TBS.can_change_persona'):
    return render(request, 'agregarPerTBS.html', {'Institucion_tbs': Insti, 'departamento_tbs': depar, 'resultado_tbs': result})
else:
    error_message = 'No tienes permiso para editar las pruebas tuberculosis'
    return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})
"""
"""
if request.user.has_perm('TBS.can_change_res_per'):
    return render(request, 'agregarPerTBS.html', {'Institucion_tbs': Insti, 'departamento_tbs': depar, 'resultado_tbs': result})
else:
    error_message = 'No tienes permiso para editar las pruebas tuberculosis'
    return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})
"""
@login_required
@csrf_protect
def guardar_cambio_tbs(request):
    PersonaL = Persona_TBS.objects.all()
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    depar= departamento_tbs.objects.all().order_by('nombreDep') 
    result = resultado_tbs.objects.all()
    res_per = resultado_per_tbs.objects.all()
    if request.user.has_perm('TBS.can_change_persona'):
        if request.method == 'POST':
        
            persona_id = request.POST.get('id')
            campo = request.POST.get('campo')
            valor = request.POST.get('valor')
            fecha2 = request.POST.get('fecha')
            try:
                persona = Persona_TBS.objects.get(numero_de_muestra=persona_id)
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
        error_message = 'No tienes permiso para editar las pruebas tuberculosis'
        return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})
    
    

@login_required
@csrf_protect
def actualizar_institucion_tbs(request):
    PersonaL = Persona_TBS.objects.all()
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    depar= departamento_tbs.objects.all().order_by('nombreDep') 
    result = resultado_tbs.objects.all()
    res_per = resultado_per_tbs.objects.all()
    if request.user.has_perm('TBS.can_change_persona'):
        if request.method == 'POST':
            try:
                persona_id = int(request.POST.get('id_per'))
                institucion_id = int(request.POST.get('id_ins'))
                persona = Persona_TBS.objects.get(numero_de_muestra=persona_id)
                
                institucion = Institucion_tbs.objects.get(pk=institucion_id)
                persona.institucion_id = institucion
                persona.save()

                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona_TBS.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion_tbs.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})

        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para editar las pruebas tuberculosis'
        return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})
    
@login_required
@csrf_protect
def actualizar_depar_tbs(request):
    PersonaL = Persona_TBS.objects.all()
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    depar= departamento_tbs.objects.all().order_by('nombreDep') 
    result = resultado_tbs.objects.all()
    res_per = resultado_per_tbs.objects.all()
    if request.user.has_perm('TBS.can_change_persona'):
        if request.method == 'POST':
            try:
                pers_id = int(request.POST.get('id_per2'))
                depar_id = int(request.POST.get('id_dep'))
                persona = Persona_TBS.objects.get(numero_de_muestra=pers_id)
                depart = departamento_tbs.objects.get(pk=depar_id)
                persona.id_dep = depart
                persona.save()

                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona_TBS.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion_tbs.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})

        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para editar las pruebas tuberculosis'
        return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})
    

@login_required
@csrf_protect
def actualizar_fecha_tbs(request):
    PersonaL = Persona_TBS.objects.all()
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    depar= departamento_tbs.objects.all().order_by('nombreDep') 
    result = resultado_tbs.objects.all()
    res_per = resultado_per_tbs.objects.all()
    if request.user.has_perm('TBS.can_change_persona'):
        if request.method == 'POST':
            try:
                pers_id = int(request.POST.get('id_per4'))
                fecha_nueva = request.POST.get('fecha')

                try:
                    persona = Persona_TBS.objects.get(numero_de_muestra=pers_id)
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
        error_message = 'No tienes permiso para editar las pruebas tuberculosis'
        return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})
   


@login_required
@csrf_protect
def actualizar_res_tbs(request):
    PersonaL = Persona_TBS.objects.all()
    Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
    depar= departamento_tbs.objects.all().order_by('nombreDep') 
    result = resultado_tbs.objects.all()
    res_per = resultado_per_tbs.objects.all()
    if request.user.has_perm('TBS.can_change_res_per'):
        if request.method == 'POST':
            try:
                persona_id = int(request.POST.get('id_per'))
                resultado_id = int(request.POST.get('id_res'))
                resultado_per_objeto = resultado_per_tbs.objects.get(numero_de_muestra_id=persona_id)
                nuevo_res=resultado_tbs.objects.get(id_res=resultado_id)
                resultado_per_objeto.id_res = nuevo_res
                resultado_per_objeto.save()
                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona_TBS.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion_tbs.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})

        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para editar las pruebas tuberculosis'
        return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs':Insti, 'departamento_tbs': depar, 'resultado_per_tbs': res_per, 'resultado_tbs': result})
    


@login_required
@csrf_protect
def borrar_tbs(request, id_per):
    try:
        PersonaL = Persona_TBS.objects.all()
        Insti = Institucion_tbs.objects.all().order_by('nombreInstitucion')
        depar = departamento_tbs.objects.all().order_by('nombreDep') 
        result = resultado_tbs.objects.all()
        res_per = resultado_per_tbs.objects.all()
        if request.user.has_perm('TBS.can_delete_persona'):
            p_delete = Persona_TBS.objects.get(numero_de_muestra=id_per)
            p_delete.delete()
            return render(request, 'gestionTBS.html', {'Persona_TBS': PersonaL, 'Institucion_tbs': Insti, 'departamento_tbs': depar, 'resultado_per_tbs':res_per, 'resultado_tbs':result})
        else:
            error_message = 'No tienes permiso para eliminar pruebas de tuberculosis'
            return render(request, 'gestionTBS.html', {'error_message' :error_message, 'Persona_TBS': PersonaL, 'Institucion_tbs': Insti, 'departamento_tbs': depar, 'resultado_per_tbs':res_per, 'resultado_tbs':result})
    except:
        return JsonResponse({'error': 'El registro no ha sido borrado'})
    





