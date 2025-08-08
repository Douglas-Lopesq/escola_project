from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Curso, Aluno


class BaseModelAdmin(admin.ModelAdmin):
    """Admin base para modelos que herdam de BaseModel"""
    readonly_fields = ['uuid', 'created_at', 'updated_at', 'created_by', 'updated_by']
    list_filter = ['ativo', 'created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        """Torna campos de auditoria somente leitura"""
        readonly = list(self.readonly_fields)
        if obj:  # Editando objeto existente
            readonly.extend(['created_at', 'created_by'])
        return readonly
    
    def save_model(self, request, obj, form, change):
        """Salva o modelo rastreando o usuário"""
        if not change:  # Novo objeto
            obj.created_by = request.user
        else:  # Objeto existente
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Curso)
class CursoAdmin(BaseModelAdmin):
    """Admin personalizado para Curso"""
    list_display = [
        'nome', 'codigo', 'coordenador', 'carga_horaria_display', 'total_alunos', 
        'ativo_display', 'created_at_display'
    ]
    list_filter = ['ativo', 'carga_horaria', 'coordenador', 'created_at', 'updated_at']
    search_fields = ['nome', 'codigo', 'coordenador', 'descricao', 'uuid']
    ordering = ['nome']
    list_per_page = 20
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'codigo', 'coordenador', 'descricao', 'carga_horaria', 'ativo')
        }),
        ('Informações do Sistema', {
            'fields': ('uuid', 'created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def carga_horaria_display(self, obj):
        """Exibe carga horária formatada"""
        return format_html(
            '<span class="badge" style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 4px;">'
            '{}h</span>',
            obj.carga_horaria
        )
    carga_horaria_display.short_description = 'Carga Horária'
    carga_horaria_display.admin_order_field = 'carga_horaria'
    
    def total_alunos(self, obj):
        """Exibe total de alunos matriculados"""
        count = obj.alunos.filter(ativo=True, status='ativo').count()
        if count > 0:
            url = reverse('admin:people_aluno_changelist') + f'?curso__id__exact={obj.id}&status__exact=ativo'
            return format_html(
                '<a href="{}" style="color: #28a745; font-weight: bold;">{} ativo{}</a>',
                url, count, 's' if count != 1 else ''
            )
        return format_html('<span style="color: #6c757d;">0 alunos</span>')
    
    def ativo_display(self, obj):
        """Exibe status ativo com ícone"""
        if obj.ativo:
            return format_html(
                '<span style="color: #28a745;">✓ Ativo</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Inativo</span>'
        )
    ativo_display.short_description = 'Status'
    ativo_display.admin_order_field = 'ativo'
    
    def created_at_display(self, obj):
        """Exibe data de criação formatada"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_display.short_description = 'Criado em'
    created_at_display.admin_order_field = 'created_at'
    
    actions = ['ativar_cursos', 'desativar_cursos']
    
    def ativar_cursos(self, request, queryset):
        """Ação para ativar cursos selecionados"""
        updated = queryset.update(ativo=True)
        self.message_user(
            request,
            f'{updated} curso(s) ativado(s) com sucesso.'
        )
    ativar_cursos.short_description = "Ativar cursos selecionados"
    
    def desativar_cursos(self, request, queryset):
        """Ação para desativar cursos selecionados"""
        updated = queryset.update(ativo=False)
        self.message_user(
            request,
            f'{updated} curso(s) desativado(s) com sucesso.'
        )
    desativar_cursos.short_description = "Desativar cursos selecionados"


@admin.register(Aluno)
class AlunoAdmin(BaseModelAdmin):
    """Admin personalizado para Aluno"""
    list_display = [
        'nome', 'matricula', 'email', 'curso_link', 'semestre_display', 'status_display',
        'telefone_display', 'ativo_display', 'created_at_display'
    ]
    list_filter = ['ativo', 'status', 'semestre', 'curso', 'data_nascimento', 'created_at', 'updated_at']
    search_fields = ['nome', 'matricula', 'email', 'telefone', 'uuid', 'curso__nome']
    ordering = ['nome']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'matricula', 'email', 'telefone', 'data_nascimento')
        }),
        ('Informações Acadêmicas', {
            'fields': ('curso', 'semestre', 'status', 'ativo')
        }),
        ('Informações do Sistema', {
            'fields': ('uuid', 'created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def curso_link(self, obj):
        """Link para o curso do aluno"""
        if obj.curso:
            url = reverse('admin:people_curso_change', args=[obj.curso.pk])
            return format_html(
                '<a href="{}" style="color: #007bff; text-decoration: none;">{}</a>',
                url, obj.curso.nome
            )
        return '-'
    curso_link.short_description = 'Curso'
    curso_link.admin_order_field = 'curso__nome'
    
    def semestre_display(self, obj):
        """Exibe o semestre do aluno"""
        return obj.get_semestre_display()
    semestre_display.short_description = 'Semestre'
    semestre_display.admin_order_field = 'semestre'
    
    def status_display(self, obj):
        """Exibe status com cor"""
        colors = {
            'ativo': '#28a745',
            'formado': '#007bff',
            'inativo': '#ffc107',
            'desvinculado': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def telefone_display(self, obj):
        """Exibe telefone formatado ou indica se não informado"""
        if obj.telefone:
            return format_html(
                '<a href="tel:{}" style="color: #28a745;">{}</a>',
                obj.telefone, obj.telefone
            )
        return format_html('<span style="color: #6c757d;">Não informado</span>')
    telefone_display.short_description = 'Telefone'
    
    def ativo_display(self, obj):
        """Exibe status ativo com ícone"""
        if obj.ativo:
            return format_html(
                '<span style="color: #28a745;">✓ Ativo</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Inativo</span>'
        )
    ativo_display.short_description = 'Status'
    ativo_display.admin_order_field = 'ativo'
    
    def created_at_display(self, obj):
        """Exibe data de criação formatada"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_display.short_description = 'Criado em'
    created_at_display.admin_order_field = 'created_at'
    
    actions = ['ativar_alunos', 'desativar_alunos', 'enviar_email']
    
    def ativar_alunos(self, request, queryset):
        """Ação para ativar alunos selecionados"""
        updated = queryset.update(ativo=True)
        self.message_user(
            request,
            f'{updated} aluno(s) ativado(s) com sucesso.'
        )
    ativar_alunos.short_description = "Ativar alunos selecionados"
    
    def desativar_alunos(self, request, queryset):
        """Ação para desativar alunos selecionados"""
        updated = queryset.update(ativo=False)
        self.message_user(
            request,
            f'{updated} aluno(s) desativado(s) com sucesso.'
        )
    desativar_alunos.short_description = "Desativar alunos selecionados"
    
    def enviar_email(self, request, queryset):
        """Ação para preparar envio de email para alunos selecionados"""
        emails = [aluno.email for aluno in queryset if aluno.email]
        if emails:
            emails_str = ';'.join(emails)
            self.message_user(
                request,
                mark_safe(f'Emails selecionados: <a href="mailto:{emails_str}">Clique aqui para abrir cliente de email</a>')
            )
        else:
            self.message_user(
                request,
                'Nenhum email encontrado nos alunos selecionados.',
                level='warning'
            )
    enviar_email.short_description = "Preparar envio de email"


# Customização do Admin Site
admin.site.site_header = "Sistema Escolar - Administração"
admin.site.site_title = "Sistema Escolar Admin"
admin.site.index_title = "Painel de Administração"