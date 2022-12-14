# Generated by Django 4.1.2 on 2022-10-22 13:32

from django.db import migrations, models
import django.db.models.deletion
import main.utilities


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_role_remove_userprofile_role_userprofile_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=40, verbose_name='Новость')),
                ('content', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(blank=True, upload_to=main.utilities.get_timestamp_path, verbose_name='Изображение')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Выводить в списке?')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')),
            ],
            options={
                'verbose_name': 'Новость',
                'verbose_name_plural': 'Новости',
                'ordering': ['-created_at'],
            },
        ),
        migrations.DeleteModel(
            name='SuperRubric',
        ),
        migrations.RemoveField(
            model_name='rubric',
            name='super_rubric',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='roles',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'student'), (2, 'teacher'), (3, 'employee')], default=False, verbose_name='Роль'),
        ),
        migrations.AlterField(
            model_name='rubric',
            name='name',
            field=models.CharField(db_index=True, max_length=100, unique=True, verbose_name='Название'),
        ),
        migrations.DeleteModel(
            name='Role',
        ),
        migrations.AddField(
            model_name='news',
            name='rubric',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.rubric', verbose_name='Рубрика'),
        ),
    ]
