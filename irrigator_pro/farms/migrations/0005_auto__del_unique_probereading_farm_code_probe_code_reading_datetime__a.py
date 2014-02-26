# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'ProbeReading', fields ['farm_code', 'probe_code', 'reading_datetime']
        db.delete_unique(u'farms_probereading', ['farm_code', 'probe_code', 'reading_datetime'])

        # Adding unique constraint on 'ProbeReading', fields ['radio_id', 'reading_datetime']
        db.create_unique(u'farms_probereading', ['radio_id', 'reading_datetime'])

        # Adding field 'Probe.radio_id'
        db.add_column(u'farms_probe', 'radio_id',
                      self.gf('django.db.models.fields.CharField')(default=0, unique=True, max_length=10),
                      keep_default=False)

        if not db.dry_run:        
            for probe in orm.Probe.objects.all():
                probe.radio_id = probe.farm_code + ":" + probe.probe_code

        # Deleting field 'Probe.farm_code'
        db.delete_column(u'farms_probe', 'farm_code')

        # Deleting field 'Probe.probe_code'
        db.delete_column(u'farms_probe', 'probe_code')


    def backwards(self, orm):
        # Removing unique constraint on 'ProbeReading', fields ['radio_id', 'reading_datetime']
        db.delete_unique(u'farms_probereading', ['radio_id', 'reading_datetime'])

        # Adding unique constraint on 'ProbeReading', fields ['farm_code', 'probe_code', 'reading_datetime']
        db.create_unique(u'farms_probereading', ['farm_code', 'probe_code', 'reading_datetime'])

        # Adding field 'Probe.farm_code'
        db.add_column(u'farms_probe', 'farm_code',
                      self.gf('django.db.models.fields.CharField')(default=2, max_length=10),
                      keep_default=False)

        # Adding field 'Probe.probe_code'
        db.add_column(u'farms_probe', 'probe_code',
                      self.gf('django.db.models.fields.CharField')(default=1, max_length=10),
                      keep_default=False)

        # Deleting field 'Probe.radio_id'
        db.delete_column(u'farms_probe', 'radio_id')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'farms.crop': {
            'Meta': {'ordering': "['name']", 'object_name': 'Crop'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_crop_cusers'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_crop_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'variety': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        u'farms.cropevent': {
            'Meta': {'ordering': "['crop__name', 'days_after_emergence']", 'object_name': 'CropEvent'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'crop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.Crop']"}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_cropevent_cusers'", 'to': u"orm['auth.User']"}),
            'daily_water_use': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'days_after_emergence': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_cropevent_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'farms.farm': {
            'Meta': {'ordering': "['farmer']", 'object_name': 'Farm'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'United States'", 'max_length': '32', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_farm_cusers'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'farmer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'farmers'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_farm_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'farms.field': {
            'Meta': {'ordering': "['farm__farmer__username', 'farm__name', 'name']", 'object_name': 'Field'},
            'acres': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_field_cusers'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'farm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.Farm']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irr_capacity': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_field_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'soil_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.SoilType']"})
        },
        u'farms.planting': {
            'Meta': {'ordering': "['planting_date', 'crop']", 'object_name': 'Planting'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'crop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.Crop']"}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_planting_cusers'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'field_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['farms.Field']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_planting_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'planting_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 2, 26, 0, 0)'})
        },
        u'farms.plantingevent': {
            'Meta': {'object_name': 'PlantingEvent'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'crop_event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.CropEvent']"}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_plantingevent_cusers'", 'to': u"orm['auth.User']"}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 2, 26, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_plantingevent_musers'", 'to': u"orm['auth.User']"}),
            'planting': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.Planting']"})
        },
        u'farms.probe': {
            'Meta': {'object_name': 'Probe'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_probe_cusers'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'field_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['farms.Field']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_probe_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'radio_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        u'farms.probereading': {
            'Meta': {'unique_together': "(('radio_id', 'reading_datetime'),)", 'object_name': 'ProbeReading'},
            'battery_percent': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'battery_voltage': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'circuit_board_temp': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_probereading_cusers'", 'to': u"orm['auth.User']"}),
            'farm_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'file_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'minutes_awake': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_probereading_musers'", 'to': u"orm['auth.User']"}),
            'probe_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'radio_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'reading_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'soil_potential_16': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'soil_potential_24': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'soil_potential_8': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'thermocouple_1_temp': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'thermocouple_2_temp': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'})
        },
        u'farms.probesync': {
            'Meta': {'object_name': 'ProbeSync'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_probesync_cusers'", 'to': u"orm['auth.User']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'filenames': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_probesync_musers'", 'to': u"orm['auth.User']"}),
            'nfiles': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'nrecords': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'farms.soiltype': {
            'Meta': {'ordering': "['name']", 'object_name': 'SoilType'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_soiltype_cusers'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_available_water': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '2', 'blank': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_soiltype_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'farms.soiltypeparameter': {
            'Meta': {'ordering': "['soil_type__name', 'depth']", 'object_name': 'SoilTypeParameter'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_soiltypeparameter_cusers'", 'to': u"orm['auth.User']"}),
            'depth': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intercept': ('django.db.models.fields.FloatField', [], {}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_soiltypeparameter_musers'", 'to': u"orm['auth.User']"}),
            'slope': ('django.db.models.fields.FloatField', [], {}),
            'soil_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.SoilType']"})
        },
        u'farms.waterhistory': {
            'Meta': {'object_name': 'WaterHistory'},
            'available_water_content': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_waterhistory_cusers'", 'to': u"orm['auth.User']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'field_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['farms.Field']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irrigation': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '4', 'decimal_places': '2'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_waterhistory_musers'", 'to': u"orm['auth.User']"}),
            'rain': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '4', 'decimal_places': '2'})
        }
    }

    complete_apps = ['farms']
