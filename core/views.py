from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.db.models import Q
from people.models import Curso, Aluno
from .mixins import (
    TitleMixin, SuccessMessageMixin, ActiveObjectsMixin, 
    UserTrackingMixin, SoftDeleteMixin, BreadcrumbMixin
)


class HomeView(TitleMixin, BreadcrumbMixin, TemplateView):
    """View da página inicial"""
    template_name = 'core/home.html'
    title = 'Início - Sistema Escolar'
    breadcrumbs = [
        {'name': 'Início', 'url': 'home', 'active': True}
    ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_cursos'] = Curso.objects.filter(ativo=True).count()
        context['total_alunos'] = Aluno.objects.filter(ativo=True).count()
        return context


# Views para Curso
class CursoListView(TitleMixin, BreadcrumbMixin, ActiveObjectsMixin, ListView):
    """Lista todos os cursos"""
    model = Curso
    template_name = 'core/curso_list.html'
    context_object_name = 'cursos'
    title = 'Cursos - Sistema Escolar'
    breadcrumbs = [
        {'name': 'Início', 'url': 'home', 'active': False},
        {'name': 'Cursos', 'url': 'curso_list', 'active': True}
    ]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | Q(descricao__icontains=search)
            )
        
        return queryset.order_by('nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class CursoDetailView(TitleMixin, BreadcrumbMixin, ActiveObjectsMixin, DetailView):
    """Detalhes de um curso"""
    model = Curso
    template_name = 'core/curso_detail.html'
    context_object_name = 'curso'
    
    def get_title(self):
        return f'{self.object.nome} - Sistema Escolar'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Início', 'url': 'home', 'active': False},
            {'name': 'Cursos', 'url': 'curso_list', 'active': False},
            {'name': self.object.nome, 'url': None, 'active': True}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alunos'] = self.object.alunos.filter(ativo=True)
        return context


class CursoCreateView(TitleMixin, BreadcrumbMixin, SuccessMessageMixin, UserTrackingMixin, CreateView):
    """Criar novo curso"""
    model = Curso
    template_name = 'core/curso_form.html'
    fields = ['nome', 'codigo', 'coordenador', 'descricao', 'carga_horaria']
    title = 'Criar Curso - Sistema Escolar'
    success_message = 'Curso criado com sucesso!'
    breadcrumbs = [
        {'name': 'Início', 'url': 'home', 'active': False},
        {'name': 'Cursos', 'url': 'curso_list', 'active': False},
        {'name': 'Criar Curso', 'url': None, 'active': True}
    ]
    
    def get_success_url(self):
        return reverse_lazy('curso_detail', kwargs={'pk': self.object.pk})


class CursoUpdateView(TitleMixin, BreadcrumbMixin, SuccessMessageMixin, UserTrackingMixin, ActiveObjectsMixin, UpdateView):
    """Editar curso"""
    model = Curso
    template_name = 'core/curso_form.html'
    fields = ['nome', 'codigo', 'coordenador', 'descricao', 'carga_horaria']
    success_message = 'Curso atualizado com sucesso!'
    
    def get_title(self):
        return f'Editar {self.object.nome} - Sistema Escolar'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Início', 'url': 'home', 'active': False},
            {'name': 'Cursos', 'url': 'curso_list', 'active': False},
            {'name': self.object.nome, 'url': 'curso_detail', 'url_kwargs': {'pk': self.object.pk}, 'active': False},
            {'name': 'Editar', 'url': None, 'active': True}
        ]
    
    def get_success_url(self):
        return reverse_lazy('curso_detail', kwargs={'pk': self.object.pk})


class CursoDeleteView(TitleMixin, BreadcrumbMixin, SuccessMessageMixin, SoftDeleteMixin, ActiveObjectsMixin, DeleteView):
    """Deletar curso (soft delete)"""
    model = Curso
    template_name = 'core/curso_confirm_delete.html'
    context_object_name = 'curso'
    success_url = reverse_lazy('curso_list')
    success_message = 'Curso removido com sucesso!'
    
    def get_title(self):
        return f'Excluir {self.object.nome} - Sistema Escolar'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Início', 'url': 'home', 'active': False},
            {'name': 'Cursos', 'url': 'curso_list', 'active': False},
            {'name': self.object.nome, 'url': 'curso_detail', 'url_kwargs': {'pk': self.object.pk}, 'active': False},
            {'name': 'Excluir', 'url': None, 'active': True}
        ]


# Views para Aluno
class AlunoListView(TitleMixin, BreadcrumbMixin, ActiveObjectsMixin, ListView):
    """Lista todos os alunos"""
    model = Aluno
    template_name = 'core/aluno_list.html'
    context_object_name = 'alunos'
    title = 'Alunos - Sistema Escolar'
    breadcrumbs = [
        {'name': 'Início', 'url': 'home', 'active': False},
        {'name': 'Alunos', 'url': 'aluno_list', 'active': True}
    ]
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('curso')
        search = self.request.GET.get('search', '')
        curso_id = self.request.GET.get('curso', '')
        status = self.request.GET.get('status', '')
        
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | Q(email__icontains=search) | Q(matricula__icontains=search)
            )
        
        if curso_id:
            queryset = queryset.filter(curso_id=curso_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos'] = Curso.objects.filter(ativo=True).order_by('nome')
        context['search'] = self.request.GET.get('search', '')
        context['selected_curso'] = self.request.GET.get('curso', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['status_choices'] = Aluno.STATUS_CHOICES
        return context


class AlunoDetailView(TitleMixin, BreadcrumbMixin, ActiveObjectsMixin, DetailView):
    """Detalhes de um aluno"""
    model = Aluno
    template_name = 'core/aluno_detail.html'
    context_object_name = 'aluno'
    
    def get_title(self):
        return f'{self.object.nome} - Sistema Escolar'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Início', 'url': 'home', 'active': False},
            {'name': 'Alunos', 'url': 'aluno_list', 'active': False},
            {'name': self.object.nome, 'url': None, 'active': True}
        ]


class AlunoCreateView(TitleMixin, BreadcrumbMixin, SuccessMessageMixin, UserTrackingMixin, CreateView):
    """Criar novo aluno"""
    model = Aluno
    template_name = 'core/aluno_form.html'
    fields = ['nome', 'matricula', 'email', 'telefone', 'data_nascimento', 'semestre', 'status', 'curso']
    title = 'Criar Aluno - Sistema Escolar'
    success_message = 'Aluno criado com sucesso!'
    breadcrumbs = [
        {'name': 'Início', 'url': 'home', 'active': False},
        {'name': 'Alunos', 'url': 'aluno_list', 'active': False},
        {'name': 'Criar Aluno', 'url': None, 'active': True}
    ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos'] = Curso.objects.filter(ativo=True).order_by('nome')
        # Adicionar as choices para o template
        context['semestre_choices'] = Aluno.SEMESTRE_CHOICES
        context['status_choices'] = Aluno.STATUS_CHOICES
        return context
    
    def get_success_url(self):
        return reverse_lazy('aluno_detail', kwargs={'pk': self.object.pk})


class AlunoUpdateView(TitleMixin, BreadcrumbMixin, SuccessMessageMixin, UserTrackingMixin, ActiveObjectsMixin, UpdateView):
    """Editar aluno"""
    model = Aluno
    template_name = 'core/aluno_form.html'
    fields = ['nome', 'matricula', 'email', 'telefone', 'data_nascimento', 'semestre', 'status', 'curso']
    success_message = 'Aluno atualizado com sucesso!'
    
    def get_title(self):
        return f'Editar {self.object.nome} - Sistema Escolar'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Início', 'url': 'home', 'active': False},
            {'name': 'Alunos', 'url': 'aluno_list', 'active': False},
            {'name': self.object.nome, 'url': 'aluno_detail', 'url_kwargs': {'pk': self.object.pk}, 'active': False},
            {'name': 'Editar', 'url': None, 'active': True}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos'] = Curso.objects.filter(ativo=True).order_by('nome')
        # Adicionar as choices para o template
        context['semestre_choices'] = Aluno.SEMESTRE_CHOICES
        context['status_choices'] = Aluno.STATUS_CHOICES
        return context
    
    def get_success_url(self):
        return reverse_lazy('aluno_detail', kwargs={'pk': self.object.pk})


class AlunoDeleteView(TitleMixin, BreadcrumbMixin, SuccessMessageMixin, SoftDeleteMixin, ActiveObjectsMixin, DeleteView):
    """Deletar aluno (soft delete)"""
    model = Aluno
    template_name = 'core/aluno_confirm_delete.html'
    context_object_name = 'aluno'
    success_url = reverse_lazy('aluno_list')
    success_message = 'Aluno removido com sucesso!'
    
    def get_title(self):
        return f'Excluir {self.object.nome} - Sistema Escolar'
    
    def get_breadcrumbs(self):
        return [
            {'name': 'Início', 'url': 'home', 'active': False},
            {'name': 'Alunos', 'url': 'aluno_list', 'active': False},
            {'name': self.object.nome, 'url': 'aluno_detail', 'url_kwargs': {'pk': self.object.pk}, 'active': False},
            {'name': 'Excluir', 'url': None, 'active': True}
        ]


# Mapeamento das views antigas para as novas (para compatibilidade)
home = HomeView.as_view()
curso_list = CursoListView.as_view()
curso_detail = CursoDetailView.as_view()
curso_create = CursoCreateView.as_view()
curso_edit = CursoUpdateView.as_view()
curso_delete = CursoDeleteView.as_view()
aluno_list = AlunoListView.as_view()
aluno_detail = AlunoDetailView.as_view()
aluno_create = AlunoCreateView.as_view()
aluno_edit = AlunoUpdateView.as_view()
aluno_delete = AlunoDeleteView.as_view()