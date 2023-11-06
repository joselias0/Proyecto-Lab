from django.db import models

class Institucion_tbs(models.Model):
    idInstitucion = models.AutoField(primary_key=True, unique=True)
    nombreInstitucion = models.CharField(max_length=100)

class departamento_tbs(models.Model):
    id_dep=models.AutoField(primary_key=True, unique=True)
    nombreDep=models.CharField(max_length=50)
    def __str__(self):
        return f"Departamento #{self.id_dep}: {self.nombreDep}"

class Persona_TBS(models.Model):
    numero_de_muestra = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=50)
    edad = models.IntegerField()
    direccion = models.TextField()
    dui=models.CharField(max_length=50)
    expediente = models.CharField(max_length=50)
    id_dep = models.ForeignKey(departamento_tbs, to_field='id_dep', on_delete=models.CASCADE)
    institucion_id = models.ForeignKey(Institucion_tbs, to_field='idInstitucion', on_delete=models.CASCADE) 
    fecha = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Muestra #{self.numero_de_muestra}: {self.nombre}"
    
    class Meta:
        permissions = [
            ("can_view_persona", "Can view persona_tbs"),
            ("can_add_persona", "Can add persona_tbs"),
            ("can_change_persona", "Can change persona_tbs"),
            ("can_delete_persona", "Can delete persona_tbs"),
        ]

class resultado_tbs(models.Model):
    id_res = models.AutoField(primary_key=True, unique=True)
    resultado = models.CharField(max_length=50)

class resultado_per_tbs(models.Model):
    id_res_per = models.AutoField(primary_key=True, unique=True)
    numero_de_muestra = models.ForeignKey(Persona_TBS, to_field='numero_de_muestra', on_delete=models.CASCADE)
    id_res = models.ForeignKey(resultado_tbs, to_field='id_res', on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("can_change_res_per", "Can change resultado_per_tbs")
        ]





