# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Violation'
        db.create_table('violations_violation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('violation_id', self.gf('django.db.models.fields.IntegerField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Location'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('violations', ['Violation'])

        # Adding unique constraint on 'Violation', fields ['content_type', 'type', 'violation_id']
        db.create_unique('violations_violation', ['content_type_id', 'type', 'violation_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Violation', fields ['content_type', 'type', 'violation_id']
        db.delete_unique('violations_violation', ['content_type_id', 'type', 'violation_id'])

        # Deleting model 'Violation'
        db.delete_table('violations_violation')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'locations.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'postcode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'in_region'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'region_code': ('django.db.models.fields.IntegerField', [], {}),
            'region_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'root': ('django.db.models.fields.IntegerField', [], {}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'tik': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'in_tik'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'tvd': ('django.db.models.fields.BigIntegerField', [], {}),
            'vrnkomis': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'vrnorg': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'x_coord': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_coord': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'violations.violation': {
            'Meta': {'unique_together': "(('content_type', 'type', 'violation_id'),)", 'object_name': 'Violation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Location']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'violation_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['violations']
