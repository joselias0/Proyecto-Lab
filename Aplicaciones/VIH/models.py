from django.db import models

class Institucion_vih(models.Model):
    idInstitucion = models.AutoField(primary_key=True, unique=True)
    nombreInstitucion = models.CharField(max_length=100)

class departamento_vih(models.Model):
    id_dep=models.AutoField(primary_key=True, unique=True)
    nombreDep=models.CharField(max_length=50)

    def __str__(self):
        return f"Departamento #{self.id_dep}: {self.nombreDep}"

class Persona_VIH(models.Model):
    numero_de_muestra = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=50)
    edad = models.IntegerField()
    direccion = models.TextField()
    dui=models.CharField(max_length=50)
    expediente = models.CharField(max_length=50)
    id_dep = models.ForeignKey(departamento_vih, to_field='id_dep', on_delete=models.CASCADE)
    institucion_id = models.ForeignKey(Institucion_vih, to_field='idInstitucion', on_delete=models.CASCADE) 
    fecha = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Muestra #{self.numero_de_muestra}: {self.nombre}"
    
    class Meta:
        permissions = [
            ("can_view_persona_vih", "Can view persona_vih"),
            ("can_add_persona_vih", "Can add persona_vih"),
            ("can_change_persona_vih", "Can change persona_vih"),
            ("can_delete_persona_vih", "Can delete persona_vih"),
        ]

class resultado_vih(models.Model):
    id_res = models.AutoField(primary_key=True, unique=True)
    resultado = models.CharField(max_length=50)

class resultado_per_vih(models.Model):
    id_res_per = models.AutoField(primary_key=True, unique=True)
    numero_de_muestra = models.ForeignKey(Persona_VIH, to_field='numero_de_muestra', on_delete=models.CASCADE)
    id_res = models.ForeignKey(resultado_vih, to_field='id_res', on_delete=models.CASCADE)
    class Meta:
        permissions = [
            ("can_change_res_per", "Can change resultado_per_vih")
        ]




