# Generated by Django 3.2.7 on 2021-10-27 04:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0029_alter_user_phone_number'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('goal', '0022_alter_goal_paid_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='total_comment_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='goal',
            name='total_like_count',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.CharField(max_length=255, null=True)),
                ('modified_at', models.DateTimeField(null=True)),
                ('is_like', models.BooleanField(default=False)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='goal_like', to='goal.goal')),
                ('has_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='like_has_profile', to='user.profile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='goal_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Like',
                'verbose_name_plural': 'Likes',
                'db_table': 'like',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.CharField(max_length=255, null=True)),
                ('modified_at', models.DateTimeField(null=True)),
                ('text', models.TextField()),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='goal_comment', to='goal.goal')),
                ('has_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='comment_has_profile', to='user.profile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='comment_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'db_table': 'comment',
            },
        ),
    ]
