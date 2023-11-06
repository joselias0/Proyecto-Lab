import openpyxl
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from Aplicaciones.VPH.models import Persona, resultado, resultado_per, Institucion, departamento
from django.http import Http404, HttpResponse, HttpResponseNotFound, JsonResponse
from datetime import date, datetime
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_protect
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.core.exceptions import ObjectDoesNotExist
from Aplicaciones.VPH.forms import *
# Create your views here.

@login_required
@csrf_protect
def inicio(request):
    return render(request,'inicio.html')

@login_required
@csrf_protect
def index(request):
    PersonaL = Persona.objects.all()
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    depar= departamento.objects.all().order_by('nombreDep') 
    result=resultado.objects.all()
    resulta=resultado_per.objects.all()

    if request.user.has_perm('VPH.can_view_persona'):
        return render(request, 'gestionVPH.html', {'Persona': PersonaL, 'Institucion':Insti, 'departamento': depar, 'resultado_per': resulta, 'resultado': result})
    else:
        error_message = 'No tienes permiso para gestionar pruebas VPH'
        return render(request, 'inicio.html', {'error_message' :error_message})

    


@login_required
@csrf_protect
def salir(request):
    logout(request)
    return redirect('/')


@login_required
@csrf_protect
def informes(request):
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    
    if request.user.has_perm('VPH.can_view_persona'):
        return render(request, 'resultado.html', {'Institucion':Insti})
    else:
        error_message = 'No tienes permiso para gestionar pruebas VPH'
        return render(request, 'inicio.html', {'error_message' :error_message})


@login_required
@csrf_protect
def generar_csv_vp(request):
    if request.method == 'POST': 
        Insti = Institucion.objects.all().order_by('nombreInstitucion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        institucion_id = request.POST.get('institucion')
        btn = request.POST.get('action')
        PersonaF = Persona.objects.all()
        result=resultado.objects.all()
        resulta=resultado_per.objects.all()
        
        if institucion_id=="None":
            institucion_id=""
        else:
            if institucion_id:
                PersonaF = PersonaF.filter(institucion_id=institucion_id)

        if fecha_inicio and fecha_fin:
            PersonaF = PersonaF.filter(fecha__range=[fecha_inicio, fecha_fin])

        if fecha_inicio > fecha_fin:
            error_message = "La fecha de inicio no puede ser mayor que la fecha final."
            return render(request, 'resultado.html', {'error_message': error_message, 'Institucion': Insti, 'Persona': PersonaF})

        if btn == 'vista_previa':
            return render(request, 'resultado.html', {'Institucion': Insti, 'Persona': PersonaF, 'resultado':result, 'resultado_per':resulta})
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
                resultados_per = resultado_per.objects.filter(numero_de_muestra=persona)

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
        
    
    return render (request,'resultado.html',{'Institucion':Insti,'Persona':PersonaF})

@login_required
@csrf_protect
def generar_pdf_persona(request, numero_de_muestra):

    if request.method == 'GET':
        form = BuscarPersonaForm(request.GET)
        try:
            persona_vph = Persona.objects.get(numero_de_muestra=numero_de_muestra)
            resul_per = resultado_per.objects.get(numero_de_muestra=persona_vph)
            resultado_vph = resultado.objects.get(pk=resul_per.id_res.id_res)
        except Persona.DoesNotExist:
            raise Http404("Persona no encontrada")

        if form.is_valid():
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="resultado_{numero_de_muestra}_vph.pdf'

            doc = SimpleDocTemplate(response, pagesize=letter)
            elements = []

            
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
            text = f"<br/><b>Tipo de prueba:</b> VPH<br/>"
            text += f"<br/><b>Nombre:</b> {persona_vph.nombre} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Edad:</b> {persona_vph.edad}<br/>"
            text += f"<br/><b>DUI:</b> {persona_vph.dui} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Expediente:</b> {persona_vph.expediente}<br/>"
            text += f"<br/><b>Nombre de Institución:</b> {persona_vph.institucion_id.nombreInstitucion} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Resultado: <b>{resultado_vph.resultado}</b><br/>"
            if persona_vph.fecha is not None:
                text += f"<br/><b>Fecha:</b> {persona_vph.fecha.strftime('%d/%m/%Y')}<br/>"
            else:
                text += "<br/><b>Fecha:</b> N/A<br/>"
            
            para = Paragraph(text, style)
            elements.append(para)
            doc.build(elements)

            return response

    return HttpResponse("Error: No se pudo generar el PDF")


@login_required
@csrf_protect
def filtrarExpediente(request):
    PersonaL = Persona.objects.all()
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    depar= departamento.objects.all().order_by('nombreDep') 
    result = resultado.objects.all()
    res_per = resultado_per.objects.all()
    

    if request.method == 'POST':
        form = ExpedienteForm(request.POST)
        if form.is_valid():
            expediente = form.cleaned_data['expediente']
            PersonaL = Persona.objects.filter(expediente__startswith=expediente)
            return render(request, 'gestionVPH.html', {'Persona': PersonaL, 'Institucion':Insti, 'departamento': depar, 'resultado': result, 'resultado_per':res_per})
    return HttpResponse('El filtrado no ha sido realizado')



@login_required
@csrf_protect
def agregar_persona(request):
    PersonaL = Persona.objects.all()
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    depar = departamento.objects.all().order_by('nombreDep') 
    result = resultado.objects.all()
    res_per = resultado_per.objects.all()

    if request.method == 'POST':
        nombre = request.POST['nombre']
        edad = request.POST['edad']
        direccion = request.POST['direccion']
        dui = request.POST['dui']
        expediente = request.POST['expediente']
        id_de=request.POST['id_dep']
        id_depar=departamento.objects.get(pk=id_de)
        resultado_id = request.POST['resultado']
        institucion_id = request.POST['institucion']
        institucion = Institucion.objects.get(pk=institucion_id)  
        

        persona = Persona.objects.create(
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
        persona_inst = Persona.objects.get(pk=persona_id)
        resultado_add = resultado.objects.get(pk=resultado_id)
        resultado_save=resultado_per.objects.create(
            numero_de_muestra=persona_inst,
            id_res=resultado_add
        )

        return render(request, 'gestionVPH.html', {'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result}) 
    if request.user.has_perm('VPH.can_view_persona'):
        if request.user.has_perm('VPH.can_add_persona'):
            return render(request, 'agregarPersona.html', {'Institucion': Insti, 'departamento': depar, 'resultado': result})
        else:
            error_message = 'No tienes permiso para agregar pruebas VPH'
            return render(request, 'gestionVPH.html', {'error_message' :error_message, 'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result})
    else:
        error_message = 'No tienes permiso para agregar pruebas VPH'
        return render(request, 'inicio.html', {'error_message' :error_message})


    
    


@login_required
@csrf_protect
def guardar_cambio(request):
    PersonaL = Persona.objects.all()
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    depar = departamento.objects.all().order_by('nombreDep') 
    result = resultado.objects.all()
    res_per = resultado_per.objects.all()

    if request.user.has_perm('VPH.can_change_persona'):
        if request.method == 'POST':
            persona_id = request.POST.get('id')
            campo = request.POST.get('campo')
            valor = request.POST.get('valor')
            try:
                persona = Persona.objects.get(numero_de_muestra=persona_id)
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
                    
                    persona.save()
                    return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Registro no encontrado'})
    else:
        error_message = 'No tienes permiso para editar pruebas VPH'
        return redirect(request, 'gestionVPH.html', {'error_message' :error_message, 'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result})
    

@login_required
@csrf_protect
def actualizar_institucion(request):
    PersonaL = Persona.objects.all()
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    depar = departamento.objects.all().order_by('nombreDep') 
    result = resultado.objects.all()
    res_per = resultado_per.objects.all()
    
    if request.user.has_perm('VPH.can_change_persona'):
        if request.method == 'POST':
            try:
                persona_id = int(request.POST.get('id_per'))
                institucion_id = int(request.POST.get('id_ins'))
                persona = Persona.objects.get(numero_de_muestra=persona_id)
                
                institucion = Institucion.objects.get(pk=institucion_id)
                persona.institucion_id = institucion
                persona.save()

                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})
    else:
        error_message = 'No tienes permiso para editar pruebas VPH'
        return render(request, 'gestionVPH.html', {'error_message' :error_message, 'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result})

@login_required
@csrf_protect
def actualizar_depar(request):
    PersonaL = Persona.objects.all()
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    depar = departamento.objects.all().order_by('nombreDep') 
    result = resultado.objects.all()
    res_per = resultado_per.objects.all()
    if request.user.has_perm('VPH.can_change_persona'):
        if request.method == 'POST':
            try:
                pers_id = int(request.POST.get('id_per2'))
                depar_id = int(request.POST.get('id_dep'))
                persona = Persona.objects.get(numero_de_muestra=pers_id)
                depart = departamento.objects.get(pk=depar_id)
                persona.id_dep = depart
                persona.save()

                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})

        return JsonResponse({'error': 'Solicitud no válida'}) 
    else:
        error_message = 'No tienes permiso para editar pruebas VPH'
        return render(request, 'gestionVPH.html', {'error_message' :error_message, 'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result})

@login_required
@csrf_protect
def actualizar_fecha(request):
    PersonaL = Persona.objects.all()
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    depar = departamento.objects.all().order_by('nombreDep') 
    result = resultado.objects.all()
    res_per = resultado_per.objects.all()
    if request.user.has_perm('VPH.can_change_persona'):
        if request.method == 'POST':
            try:
                pers_id = int(request.POST.get('id_per4'))
                fecha_nueva = request.POST.get('fecha')

                try:
                    persona = Persona.objects.get(numero_de_muestra=pers_id)
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
                    persona.save() 

                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except ValueError:
                return JsonResponse({'error': 'ID de Persona no válido'})
        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para editar pruebas VPH'
        return render(request, 'gestionVPH.html', {'error_message' :error_message, 'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result})
    


@login_required
@csrf_protect
def actualizar_res(request):
    PersonaL = Persona.objects.all()
    Insti = Institucion.objects.all().order_by('nombreInstitucion')
    depar = departamento.objects.all().order_by('nombreDep') 
    result = resultado.objects.all()
    res_per = resultado_per.objects.all()
    if request.user.has_perm('VPH.can_change_res_per'):
        if request.method == 'POST':
            try:
                persona_id = int(request.POST.get('id_per'))
                resultado_id = int(request.POST.get('id_res'))
                resultado_per_objeto = resultado_per.objects.get(numero_de_muestra_id=persona_id)
                nuevo_res=resultado.objects.get(id_res=resultado_id)
                resultado_per_objeto.id_res = nuevo_res
                resultado_per_objeto.save()
                return JsonResponse({'message': 'Cambio guardado exitosamente'})
            except Persona.DoesNotExist:
                return JsonResponse({'error': 'Registro de Persona no encontrado'})
            except Institucion.DoesNotExist:
                return JsonResponse({'error': 'Registro de Institución no encontrado'})

        return JsonResponse({'error': 'Solicitud no válida'})
    else:
        error_message = 'No tienes permiso para agregar pruebas VPH'
        return render(request, 'gestionVPH.html', {'error_message' :error_message, 'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result})
    


@login_required
@csrf_protect
def borrar(request, id_per):
    try:
        PersonaL = Persona.objects.all()
        Insti = Institucion.objects.all().order_by('nombreInstitucion')
        depar = departamento.objects.all().order_by('nombreDep') 
        result = resultado.objects.all()
        res_per = resultado_per.objects.all()
        if request.user.has_perm('VPH.can_delete_persona'):
            p_delete = Persona.objects.get(numero_de_muestra=id_per)
            p_delete.delete()
            return render(request, 'gestionVPH.html', {'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result})
        else:
            error_message = 'No tienes permiso para eliminar pruebas VPH'
            return render(request, 'gestionVPH.html', {'error_message' :error_message, 'Persona': PersonaL, 'Institucion': Insti, 'departamento': depar, 'resultado_per':res_per, 'resultado':result})
    except:
        return JsonResponse({'error': 'El registro no ha sido borrado'})
    






