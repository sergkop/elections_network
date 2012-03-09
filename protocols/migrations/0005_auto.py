# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Protocol', fields ['verified']
        db.create_index('protocols_protocol', ['verified'])

        # Adding index on 'Protocol', fields ['object_id']
        db.create_index('protocols_protocol', ['object_id'])


    def backwards(self, orm):
        
        # Removing index on 'Protocol', fields ['object_id']
        db.delete_index('protocols_protocol', ['object_id'])

        # Removing index on 'Protocol', fields ['verified']
        db.delete_index('protocols_protocol', ['verified'])


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
            'x_coord': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'y_coord': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'protocols.attachedfile': {
            'Meta': {'object_name': 'AttachedFile'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'protocols.protocol': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'protocol_id'),)", 'object_name': 'Protocol'},
            'assistant': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'chairman': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'complaints': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['locations.Location']"}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'p1': ('django.db.models.fields.IntegerField', [], {}),
            'p10': ('django.db.models.fields.IntegerField', [], {}),
            'p11': ('django.db.models.fields.IntegerField', [], {}),
            'p12': ('django.db.models.fields.IntegerField', [], {}),
            'p13': ('django.db.models.fields.IntegerField', [], {}),
            'p14': ('django.db.models.fields.IntegerField', [], {}),
            'p15': ('django.db.models.fields.IntegerField', [], {}),
            'p16': ('django.db.models.fields.IntegerField', [], {}),
            'p17': ('django.db.models.fields.IntegerField', [], {}),
            'p18': ('django.db.models.fields.IntegerField', [], {}),
            'p19': ('django.db.models.fields.IntegerField', [], {}),
            'p2': ('django.db.models.fields.IntegerField', [], {}),
            'p20': ('django.db.models.fields.IntegerField', [], {}),
            'p21': ('django.db.models.fields.IntegerField', [], {}),
            'p22': ('django.db.models.fields.IntegerField', [], {}),
            'p23': ('django.db.models.fields.IntegerField', [], {}),
            'p3': ('django.db.models.fields.IntegerField', [], {}),
            'p4': ('django.db.models.fields.IntegerField', [], {}),
            'p5': ('django.db.models.fields.IntegerField', [], {}),
            'p6': ('django.db.models.fields.IntegerField', [], {}),
            'p7': ('django.db.models.fields.IntegerField', [], {}),
            'p8': ('django.db.models.fields.IntegerField', [], {}),
            'p9': ('django.db.models.fields.IntegerField', [], {}),
            'protocol_id': ('django.db.models.fields.IntegerField', [], {}),
            'recieve_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'secretary': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'sign_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        }
    }

    complete_apps = ['protocols']
