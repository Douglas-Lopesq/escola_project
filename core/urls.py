from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # URLs para Curso
    path('cursos/', views.curso_list, name='curso_list'),
    path('cursos/<int:pk>/', views.curso_detail, name='curso_detail'),
    path('cursos/criar/', views.curso_create, name='curso_create'),
    path('cursos/<int:pk>/editar/', views.curso_edit, name='curso_edit'),
    path('cursos/<int:pk>/deletar/', views.curso_delete, name='curso_delete'),
    
    # URLs para Aluno
    path('alunos/', views.aluno_list, name='aluno_list'),
    path('alunos/<int:pk>/', views.aluno_detail, name='aluno_detail'),
    path('alunos/criar/', views.aluno_create, name='aluno_create'),
    path('alunos/<int:pk>/editar/', views.aluno_edit, name='aluno_edit'),
    path('alunos/<int:pk>/deletar/', views.aluno_delete, name='aluno_delete'),
]