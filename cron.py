import os
import logging
import subprocess
from datetime import datetime

import paramiko
import sys

# from typing import Dict, List, Any, Union

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.settings')
from dbbackup.models import JobConfig, DestinationServer, Backup
# from django.core.management import setup_environ
from django.utils.importlib import import_module
from importlib import import_module
from djangotoolbox import fields

from ikwen.core.log import CRONS_LOGGING

logging.config.dictConfig(CRONS_LOGGING)
logger = logging.getLogger('ikwen.crons')

STARTED = 'Started'
RUNNING = 'Running'
PENDING = 'Pending'
FAILED = 'Failed'
SUCCESS = 'Success'


# sys.path.append('/home/roddy/Dropbox/PycharmProjects/dbbackup/dbbackup/')
# os.chdir('/home/roddy/Dropbox/PycharmProjects/dbbackup/dbbackup/')
# # os.environ['DJANGO_SETTINGS_MODULE'] = '/home/roddy/Dropbox/PycharmProjects/dbbackup/conf/settings.py'
# '/home/roddy/Dropbox/PycharmProjects/dbbackup/conf/settings.py'

# subprocess.call(['export PYTHONPATH=/usr/bin/python:$PYTHONPATH'])


def dump_database(hostname, db_name, db_type, db_username, db_password, dump_output_path):
    """

    :param hostname:
    :param db_name:
    :param db_type:
    :param db_username:
    :param db_password:
    :param dump_output_path:
    :return:
    """
    dumper = ""
    dump_output_path += datetime.now().strftime('_%Y-%m-%d_%H-%M')
    if db_type == 'MongoDB':
        dumper = ["mongodump", "--host", hostname]
        if db_name:
            dumper += ["--db", db_name]
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


def send_file_thru_sftp(backup, destination_server_list, source_file_path):
    """
    :param backup:
    :type source_file_path: string
    :param destination_server_list:
    :param source_file_path:
    :return:
    """
    error_message = []  # type: # List[Dict[str, Union[str, Any]]]
    sftp_return_code = 0
    size_remote_file = 0
    remote_file_path = ''
    for destination_server in destination_server_list:

        try:
            ssh_transport = paramiko.Transport(destination_server.ip, 22)
            ssh_transport.connect(username=destination_server.username, password=destination_server.password)
            sftp_session = paramiko.SFTPClient.from_transport(ssh_transport)

            remote_file_path = 'IKWEN_DB_BACKUPS/BACKUP' + backup.created_on.strftime('_%Y-%m-%d_%H-%M-%S') \
                               + '/' + source_file_path.split('/')[-1]
            if not os.path.exists('IKWEN_DB_BACKUPS'):
                sftp_session.mkdir('IKWEN_DB_BACKUPS')
            sftp_session.mkdir('IKWEN_DB_BACKUPS/BACKUP' + backup.created_on.strftime('_%Y-%m-%d_%H-%M-%S'))

            sftp_session.put(source_file_path, remote_file_path, confirm=True)
            size_remote_file = os.path.getsize('/' + os.getcwd().split('/')[1] + '/' + os.getcwd().split('/')[2] + '/'
                                               + remote_file_path)
            sftp_session.close()

        except paramiko.AuthenticationException:
            message = "Failing to authenticate on the destination server '%s' with username '%s' and password '%s'\n" % \
                      (destination_server.ip, destination_server.username, destination_server.password)
            logger.debug(message, exc_info=True)
            error_message.append(
                {'hostname': destination_server.ip, 'encountered_error': message}
            )
            sftp_return_code = 1

        except paramiko.SSHException:
            message = "Failing to connect thru SSH v2\n"
            logger.debug(message, exc_info=True)
            error_message.append(
                {'hostname': destination_server.ip, 'encountered_error': message}
            )
            sftp_return_code = 1

        except:
            message = 'Unknown error\n'
            logger.debug(message, exc_info=True)
            error_message.append(
                {'hostname': destination_server.ip, 'encountered_error': message}
            )
            sftp_return_code = 1

    return remote_file_path, size_remote_file, error_message, sftp_return_code


def do_backup(job_config):
    """
    :param job_config:
    :return:
    """

    backup = Backup.objects.create(job_config=job_config, status=STARTED)
    backup.status = RUNNING
    backup.save()
    dump_output_path = "IKWEN_DUMP/" + 'all'
    if job_config.db_name:
        dump_output_path = "IKWEN_DUMP/" + job_config.db_name
    dump_return_code, dump_output_path = dump_database(job_config.hostname, job_config.db_name, job_config.db_type,
                                                       job_config.db_username, job_config.db_password,
                                                       dump_output_path)
    dump_archive_file = dump_output_path + '.7z'
    zip_return_code = subprocess.call(["7z", "a", dump_archive_file, dump_output_path + '/*'])
    destination_server_list = job_config.destination_server_list

    if dump_return_code != 0:
        backup.status = FAILED
        message = 'Failed to dump the database server hosting at ' + job_config.hostname
        logger.error(message, exc_info=True)
        backup.error_messages = message + '\n'
        backup.save()
        return 0

    if zip_return_code != 0:
        message = 'Failed to build the dump archive ' + str(zip_return_code)
        backup.status = FAILED
        backup.error_messages = message + '\n'
        logger.error(message, exc_info=True)
        backup.save()
        return 0

    # output_folder = final_output_folder + backup.created_on.strftime('_%Y-%m-%d_%H-%M-%s')
    # if not os.path.exists(output_folder):
    #     os.mkdir(output_folder)

    backup_relative_file_path, size_backup_file, error_message, sftp_return_code = send_file_thru_sftp\
        (backup, destination_server_list, dump_archive_file)
    if sftp_return_code != 0:
        message = "Failed to send the file thru sftp" + " because of: \n"
        i = 0
        while i < len(error_message):
            message += str(i+1) + '. ' + error_message[i].get('encountered_error') + '\n'
            i += 1
        backup.status = FAILED
        backup.error_messages = message + '\n'
        logger.error(message, exc_info=True)
        backup.save()
        return 0

    eraser_return_code = subprocess.call(['rm', '-f', '-R', 'IKWEN_DUMP'])
    if eraser_return_code != 0:
        message = 'Failed to erase the temporarily folder\n'
        backup.status = FAILED
        logger.error(message, exc_info=True)
        backup.save()
        return 0

    backup.relative_file_path = backup_relative_file_path
    file_size = size_backup_file

    if file_size > 2 ** 40:
        unit = ' TB'
        s = 2 ** 40
    elif file_size > 2 ** 30:
        unit = ' GB'
        s = 2 ** 30
    elif file_size > 2 ** 20:
        unit = ' MB'
        s = 2 ** 20
    elif file_size > 2 ** 10:
        unit = ' KB'
        s = 2 ** 10
    else:
        unit = ' B'
        s = 2 ** 0
    backup.file_size = str(file_size % s) + unit

    backup.status = SUCCESS

    backup.save()

    return 1


if __name__ == '__main__':
    now = datetime.now()
    for job_config in JobConfig.objects.order_by('-id').all():
        if now.hour % job_config.run_every == 0:
            do_backup(job_config)
