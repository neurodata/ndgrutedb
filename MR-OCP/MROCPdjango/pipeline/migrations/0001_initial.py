# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildGraphModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_name', models.CharField(max_length=255)),
                ('site', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('session', models.CharField(max_length=255)),
                ('scanId', models.CharField(max_length=255)),
                ('location', models.TextField()),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field=b'username', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GraphDownloadModel',
            fields=[
                ('filepath', models.CharField(max_length=255, unique=True, serialize=False, primary_key=True)),
                ('genus', models.CharField(max_length=128)),
                ('region', models.CharField(max_length=128)),
                ('project', models.CharField(max_length=255)),
                ('numvertex', models.BigIntegerField(verbose_name=b'# Nodes')),
                ('numedge', models.BigIntegerField(verbose_name=b'# Edges')),
                ('graphattr', models.TextField(verbose_name=b'Graph Attrs')),
                ('vertexattr', models.TextField(verbose_name=b'Node Attrs')),
                ('edgeattr', models.TextField(verbose_name=b'Edge Attrs')),
                ('sensor', models.CharField(max_length=128)),
                ('source', models.CharField(max_length=256, verbose_name=b'Source host url')),
                ('mtime', models.FloatField()),
                ('url', models.URLField(max_length=2048, verbose_name=b'Download url')),
            ],
        ),
        migrations.CreateModel(
            name='OwnedProjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_name', models.CharField(max_length=255)),
                ('is_private', models.BooleanField()),
                ('owner_group', models.CharField(max_length=255, null=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RawUploadModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dtipath', models.CharField(max_length=255)),
                ('mpragepath', models.CharField(max_length=255)),
                ('bvectorpath', models.CharField(max_length=255)),
                ('bvaluepath', models.CharField(max_length=255)),
                ('atlaspath', models.CharField(max_length=255)),
                ('maskpath', models.CharField(max_length=255)),
                ('labelspath', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='SharingTokens',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=64)),
                ('issue_date', models.DateTimeField(auto_now_add=True)),
                ('expire_date', models.DateField(null=True)),
                ('issued_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field=b'username')),
                ('project_name', models.ManyToManyField(related_name='st_project_name', to='pipeline.BuildGraphModel')),
            ],
        ),
    ]
