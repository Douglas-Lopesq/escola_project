from django.contrib import messages
from django.urls import reverse_lazy


class TitleMixin:
    """Mixin para adicionar título às páginas"""
    title = None
    
    def get_title(self):
        return self.title
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context


class SuccessMessageMixin:
    """Mixin para adicionar mensagens de sucesso"""
    success_message = None
    
    def get_success_message(self):
        return self.success_message
    
    def form_valid(self, form):
        response = super().form_valid(form)
        success_message = self.get_success_message()
        if success_message:
            messages.success(self.request, success_message)
        return response


class ActiveObjectsMixin:
    """Mixin para filtrar apenas objetos ativos"""
    def get_queryset(self):
        return super().get_queryset().filter(ativo=True)


class UserTrackingMixin:
    """Mixin para rastrear usuário que criou/atualizou"""
    def form_valid(self, form):
        if not form.instance.pk:  # Novo objeto
            form.instance.created_by = self.request.user if self.request.user.is_authenticated else None
        else:  # Objeto existente
            form.instance.updated_by = self.request.user if self.request.user.is_authenticated else None
        return super().form_valid(form)


class SoftDeleteMixin:
    """Mixin para soft delete"""
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.ativo = False
        self.object.updated_by = request.user if request.user.is_authenticated else None
        self.object.save()
        return super().delete(request, *args, **kwargs)


class BreadcrumbMixin:
    """Mixin para adicionar breadcrumbs"""
    breadcrumbs = []
    
    def get_breadcrumbs(self):
        return self.breadcrumbs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context