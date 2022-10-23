from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .apps import user_registered

from .models import Comment, UserProfile, News, AdditionalImage, Rubric


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='')


class RegisterUserForm(forms.ModelForm):
    user_type = forms.ChoiceField(choices=UserProfile.USER_PROFILE_TYPE_CHOICES, widget=forms.RadioSelect, label='Роль',
                                  required=True)
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput,
                                help_text='Введите тот же самый пароль еще раз для проверки')

    def check_role(self):
        user_type = self.cleaned_data['role']
        if user_type != True:
            errors = {'role': ValidationError(
                'Выберите роль'
            )}
            raise ValidationError(errors)
        return user_type

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError(
                'Введенные пароли не совпадают', code='password_mismatch'
            )}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = UserProfile
        fields = (
            'username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages', 'user_type')


class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}


AIFormSet = inlineformset_factory(News, AdditionalImage, fields='__all__')


class UserCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        exclude = ('user',)


class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={
        'class': 'your class',
        'placeholder': 'your placeholder',
        'type': 'email',
        'name': 'email'
    }))


class RubricForm(forms.ModelForm):
    class Meta:
        model = Rubric
        fields = '__all__'
