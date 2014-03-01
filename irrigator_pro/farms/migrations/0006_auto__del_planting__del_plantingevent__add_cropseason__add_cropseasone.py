# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Probe', fields ['radio_id']
        db.delete_unique(u'farms_probe', ['radio_id'])

        # Deleting model 'Planting'
        db.delete_table(u'farms_planting')

        # Removing M2M table for field field_list on 'Planting'
        db.delete_table(db.shorten_name(u'farms_planting_field_list'))

        # Deleting model 'PlantingEvent'
        db.delete_table(u'farms_plantingevent')

        # Adding model 'CropSeason'
        db.create_table(u'farms_cropseason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('cuser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'farms_cropseason_cusers', to=orm['auth.User'])),
            ('mdate', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('muser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'farms_cropseason_musers', to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('season_start_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 3, 1, 0, 0))),
            ('crop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['farms.Crop'])),
        ))
        db.send_create_signal(u'farms', ['CropSeason'])

        # Adding M2M table for field field_list on 'CropSeason'
        m2m_table_name = db.shorten_name(u'farms_cropseason_field_list')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cropseason', models.ForeignKey(orm[u'farms.cropseason'], null=False)),
            ('field', models.ForeignKey(orm[u'farms.field'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cropseason_id', 'field_id'])

        # Adding model 'CropSeasonEvent'
        db.create_table(u'farms_cropseasonevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('cuser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'farms_cropseasonevent_cusers', to=orm['auth.User'])),
            ('mdate', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('muser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'farms_cropseasonevent_musers', to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('crop_season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['farms.CropSeason'])),
            ('crop_event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['farms.CropEvent'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 3, 1, 0, 0))),
        ))
        db.send_create_signal(u'farms', ['CropSeasonEvent'])

        # Adding unique constraint on 'CropSeasonEvent', fields ['crop_season', 'crop_event']
        db.create_unique(u'farms_cropseasonevent', ['crop_season_id', 'crop_event_id'])

        # Adding field 'Probe.crop_season'
        db.add_column(u'farms_probe', 'crop_season',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['farms.CropSeason']),
                      keep_default=False)

        # Adding unique constraint on 'Probe', fields ['crop_season', 'radio_id']
        db.create_unique(u'farms_probe', ['crop_season_id', 'radio_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Probe', fields ['crop_season', 'radio_id']
        db.delete_unique(u'farms_probe', ['crop_season_id', 'radio_id'])

        # Removing unique constraint on 'CropSeasonEvent', fields ['crop_season', 'crop_event']
        db.delete_unique(u'farms_cropseasonevent', ['crop_season_id', 'crop_event_id'])

        # Adding model 'Planting'
        db.create_table(u'farms_planting', (
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cuser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'farms_planting_cusers', to=orm['auth.User'])),
            ('crop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['farms.Crop'])),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mdate', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('muser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'farms_planting_musers', to=orm['auth.User'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('planting_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 2, 26, 0, 0))),
        ))
        db.send_create_signal(u'farms', ['Planting'])

        # Adding M2M table for field field_list on 'Planting'
        m2m_table_name = db.shorten_name(u'farms_planting_field_list')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('planting', models.ForeignKey(orm[u'farms.planting'], null=False)),
            ('field', models.ForeignKey(orm[u'farms.field'], null=False))
        ))
        db.create_unique(m2m_table_name, ['planting_id', 'field_id'])

        # Adding model 'PlantingEvent'
        db.create_table(u'farms_plantingevent', (
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('crop_event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['farms.CropEvent'])),
            ('cdate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mdate', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('cuser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'farms_plantingevent_cusers', to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 2, 26, 0, 0))),
            ('muser', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'farms_plantingevent_musers', to=orm['auth.User'])),
            ('planting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['farms.Planting'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'farms', ['PlantingEvent'])

        # Deleting model 'CropSeason'
        db.delete_table(u'farms_cropseason')

        # Removing M2M table for field field_list on 'CropSeason'
        db.delete_table(db.shorten_name(u'farms_cropseason_field_list'))

        # Deleting model 'CropSeasonEvent'
        db.delete_table(u'farms_cropseasonevent')

        # Deleting field 'Probe.crop_season'
        db.delete_column(u'farms_probe', 'crop_season_id')

        # Adding unique constraint on 'Probe', fields ['radio_id']
        db.create_unique(u'farms_probe', ['radio_id'])


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
        u'farms.cropseason': {
            'Meta': {'ordering': "['season_start_date', 'crop']", 'object_name': 'CropSeason'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'crop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.Crop']"}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_cropseason_cusers'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'field_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['farms.Field']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_cropseason_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'season_start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 3, 1, 0, 0)'})
        },
        u'farms.cropseasonevent': {
            'Meta': {'ordering': "['crop_season__season_start_date', 'crop_event']", 'unique_together': "(('crop_season', 'crop_event'),)", 'object_name': 'CropSeasonEvent'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'crop_event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.CropEvent']"}),
            'crop_season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.CropSeason']"}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_cropseasonevent_cusers'", 'to': u"orm['auth.User']"}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 3, 1, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_cropseasonevent_musers'", 'to': u"orm['auth.User']"})
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
        u'farms.probe': {
            'Meta': {'unique_together': "(('crop_season', 'radio_id'),)", 'object_name': 'Probe'},
            'cdate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'crop_season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['farms.CropSeason']"}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_probe_cusers'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'field_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['farms.Field']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'farms_probe_musers'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'radio_id': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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