from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, StudentForm, CreateUserForm, UserProfileForm, ChangePasswordForm, UserProfileAvatarForm
from .models import Student, UserProfile


def is_admin(user):
    """Проверка, является ли пользователь админом"""
    return user.is_staff or user.is_superuser


def hello(request):
    return HttpResponse("Добро пожаловать на сайт колледжа!")


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            # Автоматически создаём профиль для нового пользователя
            UserProfile.objects.create(user=user)
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'students/register.html', {'form': form})


@login_required
def student_list(request):
    """Просмотр списка студентов для обычных пользователей"""
    students = Student.objects.all()
    return render(request, 'students/index.html', {
        'students': students,
        'is_admin': is_admin(request.user),
    })


@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    """Админ-панель для добавления и редактирования студентов"""
    edit_student = None
    form = None
    
    if request.method == 'POST':
        # Обработка формы студента
        student_id = request.POST.get('student_id')
        if student_id:
            edit_student = get_object_or_404(Student, id=student_id)
            form = StudentForm(request.POST, request.FILES, instance=edit_student)
        else:
            form = StudentForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('admin_panel')
    else:
        edit_id = request.GET.get('edit')
        if edit_id:
            edit_student = get_object_or_404(Student, id=edit_id)
            form = StudentForm(instance=edit_student)
        else:
            form = StudentForm()

    if not form:
        form = StudentForm(instance=edit_student)

    students = Student.objects.all()
    
    return render(request, 'students/admin_panel.html', {
        'students': students,
        'form': form,
        'edit_student': edit_student,
    })


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """Управление пользователями в админ-панели"""
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически создаём профиль для нового пользователя
            UserProfile.objects.create(user=user)
            return redirect('admin_users')
    else:
        form = CreateUserForm()

    users = User.objects.all().order_by('-date_joined')
    return render(request, 'students/admin_users.html', {
        'users': users,
        'form': form,
    })


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    """Удаление пользователя (только для админов)"""
    user = get_object_or_404(User, id=user_id)
    
    # Защита: нельзя удалить себя
    if user.id == request.user.id:
        return redirect('admin_users')
    
    if request.method == 'POST':
        user.delete()
        return redirect('admin_users')
    
    return render(request, 'students/confirm_delete_user.html', {'user': user})


@login_required
@user_passes_test(is_admin)
def edit_student(request, student_id):
    """Редактирование студента (только для админов)"""
    return redirect(f"/admin/students/?edit={student_id}")


@login_required
@user_passes_test(is_admin)
def delete_student(request, student_id):
    """Удаление студента (только для админов)"""
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
    return redirect('admin_panel')


@login_required
def profile(request):
    """Профиль текущего пользователя"""
    user = request.user
    # Получаем или создаём профиль пользователя
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    
    profile_form = None
    avatar_form = None
    message = None
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                message = ('success', 'Профиль успешно обновлён!')
                user.refresh_from_db()
            else:
                message = ('error', 'Ошибка при обновлении профиля')
        
        elif 'update_avatar' in request.POST:
            avatar_form = UserProfileAvatarForm(request.POST, request.FILES, instance=user_profile)
            if avatar_form.is_valid():
                avatar_form.save()
                message = ('success', 'Аватар успешно обновлён!')
            else:
                message = ('error', 'Ошибка при обновлении аватара')
    
    if not profile_form:
        profile_form = UserProfileForm(instance=user)
    
    if not avatar_form:
        avatar_form = UserProfileAvatarForm(instance=user_profile)
    
    return render(request, 'students/profile.html', {
        'user': user,
        'user_profile': user_profile,
        'profile_form': profile_form,
        'avatar_form': avatar_form,
        'message': message,
        'is_admin': is_admin(user),
    })


@login_required
def user_profile(request, username):
    """Просмотр профиля другого пользователя"""
    profile_user = get_object_or_404(User, username=username)
    user_profile = UserProfile.objects.get_or_create(user=profile_user)[0]
    
    return render(request, 'students/user_profile.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'is_admin': is_admin(request.user),
    })


@login_required
def change_password(request):
    """Изменение пароля пользователя"""
    user = request.user
    message = None
    form = None
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            
            # Проверяем старый пароль
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                message = ('success', 'Пароль успешно изменён! Пожалуйста, войдите заново.')
                # Нужно переавторизоваться
                user_new = authenticate(username=user.username, password=new_password)
                if user_new:
                    from django.contrib.auth import login as auth_login
                    auth_login(request, user_new)
                    return redirect('profile')
            else:
                message = ('error', 'Старый пароль введён неправильно')
    else:
        form = ChangePasswordForm()
    
    # Получаем профиль пользователя для аватара
    user_profile = UserProfile.objects.get_or_create(user=user)[0]
    
    return render(request, 'students/change_password.html', {
        'user': user,
        'user_profile': user_profile,
        'form': form,
        'message': message,
        'is_admin': is_admin(user),
    })
