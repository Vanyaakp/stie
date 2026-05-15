from django import forms
from django.contrib.auth.models import User

from .models import Student, Club, Group, UserProfile


class StudentForm(forms.ModelForm):
    new_group = forms.CharField(
        required=False,
        label='Новая группа',
        widget=forms.TextInput(attrs={'placeholder': 'Новая группа (если нет в списке)'}),
    )

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'age', 'group', 'new_group', 'clubs', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Возраст', 'min': 1}),
            'group': forms.Select(),
            'clubs': forms.CheckboxSelectMultiple(),
        }

    def save(self, commit=True):
        new_group_name = self.cleaned_data.get('new_group')
        if new_group_name:
            group, _ = Group.objects.get_or_create(name=new_group_name, defaults={'curator': 'Неизвестно'})
            self.instance.group = group
        return super().save(commit=commit)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают!')
        return cleaned_data


class CreateUserForm(forms.ModelForm):
    """Форма для создания пользователя администратором"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
        label='Пароль'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение пароля'}),
        label='Подтверждение пароля'
    )
    is_staff = forms.BooleanField(
        required=False,
        label='Является администратором?',
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Имя пользователя'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя (опционально)'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия (опционально)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Проверка уникальности логина
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует!')

        # Проверка совпадения паролей
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают!')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = self.cleaned_data.get('is_staff', False)
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Имя',
                'class': 'profile-input'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Фамилия',
                'class': 'profile-input'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'profile-input'
            }),
        }


class UserProfileAvatarForm(forms.ModelForm):
    """Форма для загрузки аватара профиля"""
    class Meta:
        model = UserProfile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'avatar-upload',
                'accept': 'image/*'
            })
        }


class ChangePasswordForm(forms.Form):
    """Форма для изменения пароля"""
    old_password = forms.CharField(
        label='Старый пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите старый пароль',
            'class': 'profile-input'
        })
    )
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите новый пароль',
            'class': 'profile-input'
        })
    )
    confirm_password = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Подтвердите новый пароль',
            'class': 'profile-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and new_password != confirm_password:
            raise forms.ValidationError('Новые пароли не совпадают!')
        return cleaned_data