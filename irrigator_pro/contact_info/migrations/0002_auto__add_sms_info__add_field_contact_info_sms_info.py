# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SMS_Info'
        db.create_table(u'contact_info_sms_info', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('cuser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'contact_info_sms_info_cusers', to=orm['auth.User'])),
            ('mdate', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('muser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'contact_info_sms_info_musers', to=orm['auth.User'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='New', max_length=20, blank=True)),
        ))
        db.send_create_signal(u'contact_info', ['SMS_Info'])

        # Adding field 'Contact_Info.sms_info'
        db.add_column(u'contact_info_contact_info', 'sms_info',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['contact_info.SMS_Info'], unique=True, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'SMS_Info'
        db.delete_table(u'contact_info_sms_info')

        # Deleting field 'Contact_Info.sms_info'
        db.delete_column(u'contact_info_contact_info', 'sms_info_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contact_info.contact_info': {
            'Meta': {'object_name': 'Contact_Info'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'United States'", 'max_length': '32', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'contact_info_contact_info_cusers'", 'to': u"orm['auth.User']"}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'contact_info_contact_info_musers'", 'to': u"orm['auth.User']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'sms_info': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['contact_info.SMS_Info']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contact_info_user'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'contact_info.sms_info': {
            'Meta': {'object_name': 'SMS_Info'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'contact_info_sms_info_cusers'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'contact_info_sms_info_musers'", 'to': u"orm['auth.User']"}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'New'", 'max_length': '20', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['contact_info']