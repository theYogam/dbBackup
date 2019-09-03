import os


import subprocess
from datetime import datetime

import paramiko
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.settings')
from dbbackup.models import JobConfig, DestinationServer, Backup
# from django.core.management import setup_environ
from django.utils.importlib import  import_module
from importlib import import_module
from djangotoolbox import fields


# django.setup()
# setup_environ(settings)

STARTED = 'Started'
RUNNING = 'Running'
PENDING = 'Pending'
FAILED = 'Failed'
SUCCESS = 'Success'


# sys.path.append('/home/roddy/Dropbox/PycharmProjects/dbBackup/dbbackup/')
# os.chdir('/home/roddy/Dropbox/PycharmProjects/dbBackup/dbbackup/')
# # os.environ['DJANGO_SETTINGS_MODULE'] = '/home/roddy/Dropbox/PycharmProjects/dbBackup/conf/settings.py'
# '/home/roddy/Dropbox/PycharmProjects/dbBackup/conf/settings.py'

# subprocess.call(['export PYTHONPATH=/usr/bin/python:$PYTHONPATH'])


def dump_database(hostname, db_name, db_type, db_username, db_password, dump_output_path):
    dumper = ""
    dump_output_path += datetime.now().strftime('_%Y-%m-%d_%H-%M')
    if db_type == 'MongoDB':
        dumper = ["mongodump", "--host", hostname, "--db", db_name]
        if hostname != '127.0.0.1':
            if db_username:
                dumper += ["--username", db_username, "--authenticationDatabase admin"]
            if db_password:
                dumper += ["--password", db_password, "--authenticationDatabase admin"]
        dumper += ["--out", dump_output_path]
    elif db_type == 'MySQL':
        dumper += "ls"
    elif db_type == 'PostgreSQL':
        dumper += "ls"

    return subprocess.call(dumper), dump_output_path


def send_file_thru_sftp(destination_server_list, source_file_path):

    for destination_server in destination_server_list:
        try:
            ssh_transport = paramiko.Transport(destination_server.ip, 22)
            ssh_transport.connect(username=destination_server.username,
                                  password=destination_server.password)
            sftp_session = paramiko.SFTPClient.from_transport(ssh_transport)

            try:
                sftp_session.mkdir('IKWEN_DB_BACKUPS', mode=0777)
            except IOError as exception:
                return exception.message

            sftp_session.put(source_file_path, 'IKWEN_DB_BACKUPS/' + source_file_path.split('/')[-1], confirm=True)
            sftp_session.close()

        except (paramiko.SSHException, paramiko.AuthenticationException, paramiko.BadAuthenticationType,
                paramiko.AUTH_FAILED, paramiko.ssh_exception) as exception:
            return exception.message

    return 1


def do_backup(job_config):
    # current_time = datetime.now()
    # delta_time = current_time - job_config.created_on
    # seconds = delta_time.total_seconds()
    # # if (seconds/3600) % job_config.run_every == 0:
    backup = Backup.objects.create(job_config=job_config, status=STARTED)
    backup.status = RUNNING
    dump_output_path = "IKWEN_DUMP/" + job_config.db_name
    dump_return_code, dump_output_path = dump_database(job_config.hostname, job_config.db_name, job_config.db_type,
                                                       job_config.db_username, job_config.db_password,
                                                       dump_output_path)
    dump_archive_file = dump_output_path + '.7z'
    zip_return_code = subprocess.call(["7z", "a", dump_archive_file, dump_output_path + '/*'])
    destination_server_list = job_config.destination_server_list

    if dump_return_code == 0:
        if zip_return_code == 0:
            sftp_return_code = send_file_thru_sftp(destination_server_list, dump_archive_file)
            eraser_return_code = subprocess.call(['rm', 'IKWEN_DUMP', '-R', '-f'])
            if sftp_return_code == 1:
                backup.file_log_name = dump_archive_file
                backup.file_log_size = zip_return_code.__sizeof__()
                backup.status = SUCCESS
                # job_config.save()
                if eraser_return_code != 0:
                    print 'Failed to erase temporary folder'
            else:
                backup.status = FAILED
        else:
            backup.status = FAILED
    else:
        backup.status = FAILED

    # backup.save()


if __name__ == '__main__':
    now = datetime.now()
    for job_config in JobConfig.objects.order_by('-id').all():
        # if now.hour % job_config.run_every == 0:
        do_backup(job_config)


