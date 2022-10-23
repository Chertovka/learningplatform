from django.urls import path

from .forms import UserPasswordResetForm
from .views import index, detail_news, other_page, UserLoginView, UserLogoutView, ChangeUserInfoView, \
    UserPasswordChangeView, RegisterUserView, RegisterDoneView, user_activate, DeleteUserView, by_rubric, profile

from django.contrib.auth import views as auth_views

app_name = 'main'
urlpatterns = [
    path('', index, name='index'),
    path('accounts/logout/', UserLogoutView.as_view(), name='logout'),
    path('accounts/password/change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/login/', UserLoginView.as_view(), name='login'),
    path('accounts/reset_password/', auth_views.PasswordResetView.as_view(template_name="main/password_reset.html", form_class=UserPasswordResetForm),
         name='reset_password'),
    path('accounts/reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="main/password_reset_done.html"),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name="main/password_reset_form.html"),
         name='password_reset_confirm'),
    path('accounts/reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="main/password_reset_complete.html"),
         name='password_reset_complete'),
    path('accounts/profile/', profile, name='profile'),
    path('<int:pk>', by_rubric, name='by_rubric'),
    path('<int:rubric_pk>/<int:pk>/', detail_news, name='detail_news'),
    path('<str:page>/', other_page, name='other'),
]
