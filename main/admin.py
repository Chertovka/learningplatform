from django.contrib import admin
import datetime

from .forms import RubricForm, UserCommentForm
from .models import UserProfile, News, AdditionalImage, Rubric, Comment
from .utilities import send_activation_notification


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
        modeladmin.message_user(request, 'Письма с требованиями отправлены')


send_activation_notifications.short_description = \
    'Отправка писем с требованиями активации'


class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3 дней'),
            ('week', 'Не прошли более недели')
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('user_type', 'username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivatedFilter,)
    fields = (
        ('username', 'email', 'user_type'), ('first_name', 'last_name'), ('send_messages', 'is_active', 'is_activated'),
        ('is_staff', 'is_superuser'), ('groups', 'user_permissions'), ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)


admin.site.register(UserProfile, UserProfileAdmin)


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class NewsAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'created_at')
    fields = (('rubric',), 'title', 'content', 'image', 'is_active')


admin.site.register(News, NewsAdmin)


class RubricAdmin(admin.ModelAdmin):
    form = RubricForm


admin.site.register(Rubric, RubricAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content',)
    fields = ('title', 'content',)


admin.site.register(Comment, CommentAdmin)
