from django.db import models

class Institucion_pEmb(models.Model):
    idInstitucion = models.AutoField(primary_key=True, unique=True)
    nombreInstitucion = models.CharField(max_length=100)

class departamento_pEmb(models.Model):
    id_dep=models.AutoField(primary_key=True, unique=True)
    nombreDep=models.CharField(max_length=50)
    def __str__(self):
        return f"Departamento #{self.id_dep}: {self.nombreDep}"

class Persona_pEmb(models.Model):
    numero_de_muestra = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=50)
    edad = models.IntegerField()
    direccion = models.TextField()
    dui=models.CharField(max_length=50)
    expediente = models.CharField(max_length=50)
    id_dep = models.ForeignKey(departamento_pEmb, to_field='id_dep', on_delete=models.CASCADE)
    institucion_id = models.ForeignKey(Institucion_pEmb, to_field='idInstitucion', on_delete=models.CASCADE) 
    fecha = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Muestra #{self.numero_de_muestra}: {self.nombre}"
    
    class Meta:
        permissions = [
            ("can_view_persona", "Can view persona_p emb"),
            ("can_add_persona", "Can add persona_p emb"),
            ("can_change_persona", "Can change persona_p emb"),
            ("can_delete_persona", "Can delete persona_p emb"),
        ]

class resultado_pEmb(models.Model):
    id_res = models.AutoField(primary_key=True, unique=True)
    resultado = models.CharField(max_length=50)

class resultado_per_pEmb(models.Model):
    id_res_per = models.AutoField(primary_key=True, unique=True)
    numero_de_muestra = models.ForeignKey(Persona_pEmb, to_field='numero_de_muestra', on_delete=models.CASCADE)
    id_res = models.ForeignKey(resultado_pEmb, to_field='id_res', on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("can_change_res_per", "Can change resultado_per_p emb")
        ]






