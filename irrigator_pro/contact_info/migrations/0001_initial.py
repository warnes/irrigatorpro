# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact_Info',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address_1', models.CharField(max_length=50, verbose_name=b'address line 1')),
                ('address_2', models.CharField(max_length=50, verbose_name=b'address line 2', blank=True)),
                ('city', models.CharField(max_length=32)),
                ('county', models.CharField(max_length=32)),
                ('state', models.CharField(max_length=2)),
                ('zipcode', models.CharField(max_length=10, verbose_name=b'zip/postal code')),
                ('country', models.CharField(default=b'United States', max_length=32, blank=True)),
                ('cdate', models.DateTimeField(auto_now_add=True, verbose_name=b'creation date')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name=b'last modification date')),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('fax', models.CharField(max_length=20, blank=True)),
                ('cuser', models.ForeignKey(related_name='contact_info_contact_info_cusers', verbose_name=b'creator', to=settings.AUTH_USER_MODEL)),
                ('muser', models.ForeignKey(related_name='contact_info_contact_info_musers', verbose_name=b'last modifcation user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contact Information',
                'verbose_name_plural': 'Contact Information',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SMS_Info',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cdate', models.DateTimeField(auto_now_add=True, verbose_name=b'creation date')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name=b'last modification date')),
                ('number', models.CharField(unique=True, max_length=20, blank=True)),
                ('status', models.CharField(default=b'New', max_length=20, blank=True)),
                ('cuser', models.ForeignKey(related_name='contact_info_sms_info_cusers', verbose_name=b'creator', to=settings.AUTH_USER_MODEL)),
                ('muser', models.ForeignKey(related_name='contact_info_sms_info_musers', verbose_name=b'last modifcation user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='contact_info',
            name='sms_info',
            field=models.ForeignKey(blank=True, to='contact_info.SMS_Info', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact_info',
            name='user',
            field=models.OneToOneField(related_name='contact_info_user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
