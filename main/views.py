from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.http import Http404, HttpResponse, BadHeaderError
from django.shortcuts import render, get_object_or_404, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template, render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView
from django.contrib import messages

from .forms import ChangeUserInfoForm, RegisterUserForm, SearchForm, UserCommentForm
from .models import UserProfile, News, Rubric, Comment
from .utilities import signer


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = UserProfile
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, "Пользователь удален")
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(UserProfile, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


class RegisterUserView(CreateView):
    model = UserProfile
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class UserPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:login')
    success_message = 'Пароль пользователя изменен'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class UserLoginView(LoginView):
    template_name = 'main/login.html'


class UserLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


def by_rubric(request, pk):
    rubric = get_object_or_404(Rubric, pk=pk)
    newses = News.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        newses = newses.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(newses, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'newses': page.object_list, 'form': form}
    return render(request, 'main/by_rubric.html', context)


def detail_news(request, rubric_pk, pk):
    news = News.objects.get(pk=pk)
    ais = news.additionalimage_set.all()
    context = {'news': news, 'ais': ais}
    return render(request, 'main/detail_news.html', context)


def index(request):
    newses = News.objects.filter(is_active=True)[:10]
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UserCommentForm(request.POST)
            if form.is_valid():
                subject = "Пробное сообщение"
                body = {
                    'username': request.user.username,
                    'email': request.user.email,
                    'message': form.cleaned_data['content'],
                }
                message = "\n".join(body.values())
                try:
                    send_mail(subject, message,
                              'admin@example.com',
                              ['admin@example.com'])
                except BadHeaderError:
                    return HttpResponse('Найден некорректный заголовок')
                return redirect("main:index")
        form = UserCommentForm()
    else:
        form = False
    context = {'newses': newses, 'form': form}
    return render(request, 'main/index.html', context)


@login_required
def profile(request):
    users = UserProfile.objects.filter(pk=request.user.pk)
    context = {'users': users}
    return render(request, 'main/profile.html', context)


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))
