# Forked and reviewed by Silatchom SIAKA on June 10, Wed 2020
import os
import sys
import logging
import socket
import subprocess
import paramiko
from datetime import datetime, timedelta
from ftplib import FTP

sys.path.append("/home/libran/virtualenv/lib/python2.7/site-packages")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.settings')

# from typing import Dict, List, Any, Union
from django.core import mail
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

from ikwen.accesscontrol.backends import UMBRELLA
from ikwen.accesscontrol.models import Member
from ikwen.core.utils import get_mail_content, get_service_instance, send_push

# from django.core.management import setup_environ
from django.utils.importlib import import_module
from djangotoolbox import fields
from django.utils.translation import ugettext as _, activate

from importlib import import_module

from ikwen.core.log import CRONS_LOGGING

from dbbackup.models import JobConfig, DestinationServer, Backup

logging.config.dictConfig(CRONS_LOGGING)
logger = logging.getLogger('ikwen.crons')

STARTED = 'Started'
RUNNING = 'Running'
PENDING = 'Pending'
FAILED = 'Failed'
SUCCESS = 'Success'


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
    print "%s \n" % dumper
    dump_error_file = open("dump_error.txt", "a")
    dump_error_code = subprocess.call(dumper, stderr=dump_error_file)
    dump_error_file.close()

    return dump_error_code, dump_output_path, os.getcwd() + '/' + dump_error_file.name


def send_file_thru_sftp(db_hostname, backup, destination_server_list, source_file_path):
    """
    :param backup:
    :type source_file_path: string
    :param destination_server_list:
    :param source_file_path:
    :return:
    """
    error_message = []  # type: # List[Dict[str, Union[str, Any]]]
    return_code = 0
    remote_file_size = 0
    remote_dir = 'IKWEN_DB_BACKUPS/' + db_hostname + backup.created_on.strftime('_%Y-%m-%d_%H-%M-%S') + '/'
    i = 0

    for destination_server in destination_server_list:
        host_ip = destination_server.ip
        username = destination_server.username
        password = destination_server.password
        port = destination_server.port

        try:  # Try connection using the SSH v2 protocol
            ssh_transport = paramiko.Transport(host_ip, port)
            ssh_transport.connect(username=username, password=password)
            sftp_session = paramiko.SFTPClient.from_transport(ssh_transport)
            print "Connection to %s established \n" % host_ip

            if not os.path.exists('IKWEN_DB_BACKUPS'):
                sftp_session.mkdir('IKWEN_DB_BACKUPS')
                print "Create directory IKWEN_DB_BACKUPS"
            if not os.path.exists(remote_dir):
                sftp_session.mkdir(remote_dir)
                print "Create directory %s\n" % remote_dir

            remote_dir += source_file_path.split('/')[-1]
            print "Remote directory now is %d\n" % remote_dir
            sftp_session.put(source_file_path, remote_dir, confirm=True)
            remote_file_size = os.path.getsize('/' + os.getcwd().split('/')[1] + '/' + os.getcwd().split('/')[2] + '/'
                                               + remote_dir)
            print "File sent successfully ...\n"
            sftp_session.close()

        except paramiko.AuthenticationException:
            message = "Failing to authenticate on the destination server '%s' with username '%s' and password '%s'\n" % \
                      (host_ip, destination_server.username, destination_server.password)
            logger.debug(message, exc_info=True)
            error_message.append(
                {'hostname': host_ip, 'encountered_error': message}
            )
            print message
            return_code = 1

        except paramiko.SSHException:
            message = "Failing to connect thru SSH v2\n"
            logger.debug(message, exc_info=True)
            error_message.append(
                {'hostname': host_ip, 'encountered_error': message}
            )
            return_code = 1
            print message

        except:
            message = 'Unknown error\n'
            logger.debug(message, exc_info=True)
            error_message.append(
                {'hostname': host_ip, 'encountered_error': message}
            )
            return_code = 1
        if return_code == 1:
            error_message = []
            try:  # Try connection with FTP protocol
                ftp = FTP(host_ip, username, password, (host_ip, port))
                try:
                    ftp.mkd('IKWEN_DB_BACKUPS')
                    print "Create directory IKWEN_DB_BACKUPS"
                except:
                    pass
                ftp.cwd('IKWEN_DB_BACKUPS/')
                print "Change directory to IKWEN_DB_BACKUPS"
                try:
                    ftp.mkd(db_hostname + backup.created_on.strftime('_%Y-%m-%d_%H-%M-%S') + '/')
                    print "Create directory %s" % db_hostname + backup.created_on.strftime('_%Y-%m-%d_%H-%M-%S') + '/'
                except:
                    pass
                ftp.cwd(db_hostname + backup.created_on.strftime('_%Y-%m-%d_%H-%M-%S') + '/')

                source_file = open(source_file_path, 'rb')
                ftp.storbinary('STOR ' + source_file_path.split('/')[-1], source_file)
                remote_file_size = ftp.size(source_file_path.split('/')[-1])
                remote_dir += source_file_path.split('/')[-1]
                return_code = 0
                ftp.close()
                if i == len(destination_server_list):
                    print "Try to quit the tunnel\n"
                    ftp.quit()
                    print "Quit the tunnel\n"

            except Exception as e:
                message = e.message + '\n'
                logger.debug(message, exc_info=True)
                error_message.append(
                    {'hostname': host_ip, 'encountered_error': message}
                )
                return_code = 1
                print message

        i += 1

    return remote_dir, remote_file_size, error_message, return_code


def find_file_size(file_size):

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

    return s, unit


def do_backup(job_config):
    """
    :param job_config:
    :return:
    """

    backup = Backup.objects.create(job_config=job_config, status=RUNNING)
    t0 = datetime.now()
    dump_output_path = "IKWEN_DUMP/" + 'all'
    if job_config.db_name:
        dump_output_path = "IKWEN_DUMP/" + job_config.db_name
    dump_return_code, dump_output_path, dump_log_file_path = dump_database(job_config.hostname, job_config.db_name, job_config.db_type,
                                                       job_config.db_username, job_config.db_password,
                                                       dump_output_path)

    if dump_return_code != 0:
        backup.status = FAILED
        message = 'Failed to dump the database: check log file ' + dump_log_file_path
        backup.error_messages = message + '\n'
        backup.save()
        print message
        return 0

    dump_archive_file = dump_output_path + '.7z'
    zip_log_file = open("zip_error.txt", "a")
    zip_return_code = subprocess.call(["7z", "a", dump_archive_file, dump_output_path + '/*'], stderr=zip_log_file)
    zip_log_file.close()

    if zip_return_code != 0:
        message = 'Failed to build the dump archive: check log file ' + os.getcwd() + zip_log_file.name
        backup.status = FAILED
        backup.error_messages = message + '\n'
        backup.save()
        print message
        return 0

    file_path, size, error, code = send_file_thru_sftp(job_config.hostname, backup,
                                                              job_config.destination_server_list, dump_archive_file)
    if code != 0:
        i = 0
        message = ''
        while i < len(error):
            message += '\n' + str(i+1) + '. ' + error[i].get('encountered_error') + '\n'
            i += 1
        backup.status = FAILED
        backup.error_messages = message + '\n'
        logger.error(message, exc_info=True)
        backup.save()
        print message
        return 0

    eraser_return_code = subprocess.call(['rm', '-f', '-R', 'IKWEN_DUMP'])
    if eraser_return_code != 0:
        message = 'Failed to erase the temporarily folder\n'
        backup.status = FAILED
        logger.error(message, exc_info=True)
        backup.save()
        print message
        return 0

    backup.relative_file_path = file_path
    file_size = size

    print "%d\n" % file_size

    s, unit = find_file_size(file_size)

    backup.file_size_hr = str(file_size / s) + unit
    backup.file_size = file_size

    print "%s\n" % backup.file_size

    backup.status = SUCCESS
    tf = datetime.now()
    backup.run_time = (tf - t0).total_seconds()
    backup.save()

    return 1


if __name__ == '__main__':
    now = datetime.now()
    for job_config in JobConfig.objects.order_by('-id').all():
        if now.hour % job_config.run_every == 0:
            do_backup(job_config)




