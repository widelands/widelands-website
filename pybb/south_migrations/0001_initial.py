# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Category'
        db.create_table('pybb_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('position', self.gf('django.db.models.fields.IntegerField')(
                default=0, blank=True)),
        ))
        db.send_create_signal('pybb', ['Category'])

        # Adding model 'Forum'
        db.create_table('pybb_forum', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(
                related_name='forums', to=orm['pybb.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('position', self.gf('django.db.models.fields.IntegerField')(
                default=0, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(
                default='', blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('pybb', ['Forum'])

        # Adding M2M table for field moderators on 'Forum'
        db.create_table('pybb_forum_moderators', (
            ('id', models.AutoField(verbose_name='ID',
                                    primary_key=True, auto_created=True)),
            ('forum', models.ForeignKey(orm['pybb.forum'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('pybb_forum_moderators', ['forum_id', 'user_id'])

        # Adding model 'Topic'
        db.create_table('pybb_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('forum', self.gf('django.db.models.fields.related.ForeignKey')(
                related_name='topics', to=orm['pybb.Forum'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['auth.User'])),
            ('views', self.gf('django.db.models.fields.IntegerField')(
                default=0, blank=True)),
            ('sticky', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('post_count', self.gf('django.db.models.fields.IntegerField')(
                default=0, blank=True)),
        ))
        db.send_create_signal('pybb', ['Topic'])

        # Adding M2M table for field subscribers on 'Topic'
        db.create_table('pybb_topic_subscribers', (
            ('id', models.AutoField(verbose_name='ID',
                                    primary_key=True, auto_created=True)),
            ('topic', models.ForeignKey(orm['pybb.topic'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('pybb_topic_subscribers', ['topic_id', 'user_id'])

        # Adding model 'Post'
        db.create_table('pybb_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(
                related_name='posts', to=orm['pybb.Topic'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(
                related_name='posts', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(
                null=True, blank=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(
                default='markdown', max_length=15)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('body_html', self.gf('django.db.models.fields.TextField')()),
            ('body_text', self.gf('django.db.models.fields.TextField')()),
            ('user_ip', self.gf('django.db.models.fields.IPAddressField')(
                default='', max_length=15, blank=True)),
        ))
        db.send_create_signal('pybb', ['Post'])

        # Adding model 'Read'
        db.create_table('pybb_read', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['auth.User'])),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['pybb.Topic'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
        ))
        db.send_create_signal('pybb', ['Read'])

        # Adding unique constraint on 'Read', fields ['user', 'topic']
        db.create_unique('pybb_read', ['user_id', 'topic_id'])

        # Adding model 'PrivateMessage'
        db.create_table('pybb_privatemessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dst_user', self.gf('django.db.models.fields.related.ForeignKey')(
                related_name='dst_users', to=orm['auth.User'])),
            ('src_user', self.gf('django.db.models.fields.related.ForeignKey')(
                related_name='src_users', to=orm['auth.User'])),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(
                default='markdown', max_length=15)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('body_html', self.gf('django.db.models.fields.TextField')()),
            ('body_text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('pybb', ['PrivateMessage'])

        # Adding model 'Attachment'
        db.create_table('pybb_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(
                related_name='attachments', to=orm['pybb.Post'])),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('hash', self.gf('django.db.models.fields.CharField')
             (default='', max_length=40, db_index=True, blank=True)),
        ))
        db.send_create_signal('pybb', ['Attachment'])

    def backwards(self, orm):

        # Removing unique constraint on 'Read', fields ['user', 'topic']
        db.delete_unique('pybb_read', ['user_id', 'topic_id'])

        # Deleting model 'Category'
        db.delete_table('pybb_category')

        # Deleting model 'Forum'
        db.delete_table('pybb_forum')

        # Removing M2M table for field moderators on 'Forum'
        db.delete_table('pybb_forum_moderators')

        # Deleting model 'Topic'
        db.delete_table('pybb_topic')

        # Removing M2M table for field subscribers on 'Topic'
        db.delete_table('pybb_topic_subscribers')

        # Deleting model 'Post'
        db.delete_table('pybb_post')

        # Deleting model 'Read'
        db.delete_table('pybb_read')

        # Deleting model 'PrivateMessage'
        db.delete_table('pybb_privatemessage')

        # Deleting model 'Attachment'
        db.delete_table('pybb_attachment')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pybb.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'hash': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['pybb.Post']"}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        'pybb.category': {
            'Meta': {'ordering': "['position']", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        'pybb.forum': {
            'Meta': {'ordering': "['position']", 'object_name': 'Forum'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forums'", 'to': "orm['pybb.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderators': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'pybb.post': {
            'Meta': {'ordering': "['created']", 'object_name': 'Post'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'body_html': ('django.db.models.fields.TextField', [], {}),
            'body_text': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'markdown'", 'max_length': '15'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': "orm['pybb.Topic']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': "orm['auth.User']"}),
            'user_ip': ('django.db.models.fields.IPAddressField', [], {'default': "''", 'max_length': '15', 'blank': 'True'})
        },
        'pybb.privatemessage': {
            'Meta': {'ordering': "['-created']", 'object_name': 'PrivateMessage'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'body_html': ('django.db.models.fields.TextField', [], {}),
            'body_text': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'dst_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dst_users'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'markdown'", 'max_length': '15'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'src_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'src_users'", 'to': "orm['auth.User']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'pybb.read': {
            'Meta': {'unique_together': "(['user', 'topic'],)", 'object_name': 'Read'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pybb.Topic']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pybb.topic': {
            'Meta': {'ordering': "['-updated']", 'object_name': 'Topic'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'forum': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topics'", 'to': "orm['pybb.Forum']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'post_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'sticky': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'subscriptions'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        }
    }

    complete_apps = ['pybb']
