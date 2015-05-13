# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationsRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cdate', models.DateTimeField(auto_now_add=True, verbose_name=b'creation date')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name=b'last modification date')),
                ('comment', models.TextField(blank=True)),
                ('level', models.CharField(max_length=15)),
                ('notification_type', models.CharField(max_length=15)),
                ('label', models.CharField(max_length=50)),
                ('delivery_time', models.CharField(max_length=10)),
                ('time_zone', models.CharField(max_length=50)),
                ('cuser', models.ForeignKey(related_name='notifications_notificationsrule_cusers', verbose_name=b'creator', to=settings.AUTH_USER_MODEL)),
                ('field_list', models.ManyToManyField(to='farms.Field')),
                ('muser', models.ForeignKey(related_name='notifications_notificationsrule_musers', verbose_name=b'last modifcation user', to=settings.AUTH_USER_MODEL)),
                ('recipients', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification Rule',
            },
            bases=(models.Model,),
        ),
    ]
