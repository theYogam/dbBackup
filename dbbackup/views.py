import os
import urllib
import json
import mysql.connector
import subprocess
import paramiko

import sys
from ftplib import FTP
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError, ConfigurationError


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.settings')
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
# from django.utils.decorators import method_decorator
from django.utils.translation import get_language
# from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from djangotoolbox.fields import ListField

from ikwen.core.utils import to_dict
from ikwen.core.views import HybridListView, ChangeObjectBase

from dbbackup.models import JobConfig, DestinationServer, Backup
from dbbackup.admin import JobConfigAdmin, BackupAdmin, DestinationServerAdmin
from dbbackup.forms import JobConfigForm, DestinationServerForm




reload(sys)
sys.setdefaultencoding('utf-8')  # Allow system to decode utf-8's strings such as ',",|,?


class Home(TemplateView):
    """code"""
    template_name = 'dbbackup/home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        return context


class JobConfigList(HybridListView):
    """ code"""
    model = JobConfig
    ordering = ('-id',)
    # search_field = 'db_name'
    html_results_template_name = 'dbbackup/job_config_list_result.html'
    list_filter = (
        'hostname',
        ('db_type', _('Database type')),
        ('created_on', _('Date created'))
    )


class ChangeJobConfig(ChangeObjectBase):
    """
    code
    """
    model = JobConfig
    model_admin = JobConfigAdmin
    template_name = 'dbbackup/change_job_config.html'

    def post(self, request, *args, **kwargs):
        context = super(ChangeJobConfig, self).get_context_data(**kwargs)
        job_config_form = JobConfigForm(request.POST)
        if job_config_form.is_valid():
            hostname = job_config_form.cleaned_data.get("hostname")
            db_name = job_config_form.cleaned_data.get("db_name")
            db_type = job_config_form.cleaned_data.get("db_type")
            db_username = job_config_form.cleaned_data.get("db_username")
            db_password = job_config_form.cleaned_data.get("db_password")
            run_every = job_config_form.cleaned_data.get("run_every")
            job_config = JobConfig(
                hostname=hostname,
                db_name=db_name,
                db_type=db_type,
                db_username=db_username,
                db_password=db_password,
                run_every=run_every
            )
            job_uncleaned_data_list = [{'name': field.name, 'value': field.value()} for
                                       field in job_config_form if field not in job_config_form.cleaned_data]
            i = 1
            destination_server_list = []

            while True:
                try:

                    ip = request.POST['ip%d' % i]
                    username = request.POST['username%d' % i]
                    password = request.POST['password%d' % i]
                    port = request.POST.get('port%d' % i)
                    if not port:
                        port = 22
                    destination_server = {
                        'ip': ip,
                        'username': username,
                        'password': password,
                        'port': port
                    }
                    destination_server_form = DestinationServerForm(destination_server)

                    if destination_server_form.is_valid():
                        destination_server_form.save()
                        destination_server = DestinationServer.objects.create(ip=ip, username=username,
                                                                              password=password, port=port)

                        destination_server_list.append(destination_server)
                        job_config.destination_server_list = destination_server_list

                    else:
                        context['destination_server_form'] = destination_server_form
                        return render(request, self.template_name, context)
                except:
                    break
                i += 1

            if i == 1:
                context['destination_server_form'] = "No destination server configured"
                return render(request, self.template_name, context)
            else:
                job_config.save()
                next_url = reverse('dbbackup:change_jobconfig', args=(job_config.id,))
                return HttpResponseRedirect(next_url)

        else:
            context['form'] = job_config_form
            return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        context = super(ChangeJobConfig, self).get_context_data(**kwargs)
        if kwargs.__len__() > 0:
            job_config_id = kwargs['object_id']
            most_recent_backup = Backup.objects.filter(job_config_id=job_config_id).order_by('created_on')[:4]
            context['job_config_id'] = job_config_id
            context['destination_server_list'] = JobConfig.objects.get(id=job_config_id).destination_server_list
            context['most_recent_backup'] = most_recent_backup
        else:
            context['no_backup_history'] = 'No backups yet exist for this Job'

        return context


class DBListFilter(object):
    title = _('Database')
    parameter_name = 'database'

    def lookups(self):
        choices = [(job_config.id, job_config.db_type) for job_config in JobConfig.objects.all()]
        return choices

    def queryset(self, request, queryset):
        value = request.GET.get(self.parameter_name)
        if value:
            job_config_list = JobConfig.objects.filter(db_type=value)
            return queryset.filter(job_config__in=job_config_list)
        return queryset


class BackupList(HybridListView):
    """
    comment
    """
    model = Backup
    ordering = ('-id',)
    list_filter = (DBListFilter, 'status', 'created_on')
    html_results_template_name = 'dbbackup/backup_list_result.html'

    def get_context_data(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        context = super(BackupList, self).get_context_data(**kwargs)
        if kwargs.__len__() > 0:
            backup_id = kwargs['object_id']
            matched_backup = Backup.objects.get(id=backup_id)
            backup_list = Backup.objects.filter(job_config_id=matched_backup.job_config_id).order_by('created_on')
            context['backup_list'] = backup_list
            context['backup_id'] = backup_id
        else:
            backup_list = Backup.objects.all().order_by('created_on')
            context['backup_list'] = backup_list

        return context


def test_db_connection(request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    hostname = request.GET.get('hostname')
    db_username = request.GET.get('db_username')
    db_password = request.GET.get('db_password')
    db_type = request.GET.get('db_type')

    if not hostname:
        return HttpResponse(json.dumps({'success': False}), 'content-type: text/json')

    if db_type == 'MongoDB':
        uri = 'mongodb://'
        username = urllib.quote_plus(db_username)
        password = urllib.quote_plus(db_password)

        if username and password:
            uri += username + ':' + password + '@'
        elif username:
            uri += username + '@'

        uri += hostname + ':27017/?authSource=admin&authMechanism=MONGODB-CR'

        try:
            client = MongoClient(uri)
            return HttpResponse(json.dumps({'success': True}), 'content-type: text/json')

        except PyMongoError as e:
            return HttpResponse(json.dumps({'success': False}), 'content-type: text/json')
    elif db_type == 'MySQL':
        config = {}
        if db_username:
            config['user'] = db_username
        if db_password:
            config['password'] = db_password
        try:
            cnx = mysql.connector.connect(**config)
            cnx.close()
            return HttpResponse(json.dumps({'success': True}), 'content-type: text/json')

        except:
            return HttpResponse(json.dumps({'success': False}), 'content-type: text/json')

    else:
        return HttpResponse('Errors...')


def test_destination_server_connection(request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    server_ip = request.GET.get('ip')
    server_username = request.GET.get('username')
    server_password = request.GET.get('password')
    server_port = request.GET.get('port')

    try:
        if not server_port:
            server_port = 22
        ssh_transport = paramiko.Transport(server_ip, server_port)
        ssh_transport.connect(username=server_username, password=server_password)
    except (paramiko.SSHException, paramiko.AuthenticationException, paramiko.BadAuthenticationType,
            paramiko.AUTH_FAILED, paramiko.ssh_exception) as e:
        message = e.message
        try:
            if not server_port:
                server_port = 21
            ftp = FTP(server_ip, server_username, server_password, (server_ip, server_port))
            return HttpResponse(json.dumps({'success': True}), 'content-type: text/json')
        except Exception as e:
            return HttpResponse(json.dumps({'success': False, 'error': message + '\n' + e.message}), 'content-type: text/json')

    return HttpResponse(json.dumps({'success': True}), 'content-type: text/json')


