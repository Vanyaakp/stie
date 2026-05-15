from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('students/', views.student_list, name='student_list_alias'),
    path('hello/', views.hello, name='hello'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='students/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Профиль
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('change-password/', views.change_password, name='change_password'),
    # Админ-панель
    path('admin/students/', views.admin_panel, name='admin_panel'),
    path('admin/students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('admin/students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    # Управление пользователями
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]
