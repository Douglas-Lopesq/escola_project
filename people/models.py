import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
User = get_user_model()


def get_sentinel_user():
    return get_user_model().objects.get_or_create(email="deleted")[0]


class UUIDModel(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class CreationTimestampedModel(models.Model):
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
        editable=False,
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        on_delete=models.SET(get_sentinel_user),
        null=True,
        related_name="created_%(app_label)s_%(class)s_set",
    )

    class Meta:
        abstract = True


class UpdateTimestampedModel(models.Model):
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True, editable=False)
    updated_by = models.ForeignKey(
        User,
        verbose_name=_("Updated by"),
        on_delete=models.SET(get_sentinel_user),
        null=True,
        related_name="updated_%(app_label)s_%(class)s_set",
    )

    class Meta:
        abstract = True


class TimestampedModel(CreationTimestampedModel, UpdateTimestampedModel):
    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel):
    class Meta:
        abstract = True


class Curso(BaseModel):
    nome = models.CharField(_("Nome"), max_length=100)
    codigo = models.CharField(_("Código"), max_length=20, unique=True)
    coordenador = models.CharField(_("Coordenador"), max_length=100)
    descricao = models.TextField(_("Descrição"), blank=True)
    carga_horaria = models.PositiveIntegerField(_("Carga Horária"))
    ativo = models.BooleanField(_("Ativo"), default=True)

    class Meta:
        verbose_name = _("Curso")
        verbose_name_plural = _("Cursos")
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Aluno(BaseModel):
    STATUS_CHOICES = [
        ('ativo', _('Ativo')),
        ('inativo', _('Inativo')),
        ('desvinculado', _('Desvinculado')),
        ('formado', _('Formado')),
    ]
    
    SEMESTRE_CHOICES = [
        (1, _('1º Semestre')),
        (2, _('2º Semestre')),
        (3, _('3º Semestre')),
        (4, _('4º Semestre')),
        (5, _('5º Semestre')),
        (6, _('6º Semestre')),
        (7, _('7º Semestre')),
        (8, _('8º Semestre')),
        (9, _('9º Semestre')),
        (10, _('10º Semestre')),
    ]
    
    nome = models.CharField(_("Nome"), max_length=100)
    matricula = models.CharField(_("Matrícula"), max_length=20, unique=True)
    email = models.EmailField(_("Email"), unique=True)
    telefone = models.CharField(_("Telefone"), max_length=20, blank=True)
    data_nascimento = models.DateField(_("Data de Nascimento"))
    semestre = models.PositiveIntegerField(_("Semestre"), choices=SEMESTRE_CHOICES, default=1)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='ativo')
    curso = models.ForeignKey(
        Curso,
        verbose_name=_("Curso"),
        on_delete=models.CASCADE,
        related_name="alunos"
    )
    ativo = models.BooleanField(_("Ativo"), default=True)

    class Meta:
        verbose_name = _("Aluno")
        verbose_name_plural = _("Alunos")
        ordering = ['nome']

    def __str__(self):
        return self.nome