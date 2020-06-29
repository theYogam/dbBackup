import os
import logging
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.settings')

from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _, activate


from ikwen.accesscontrol.backends import UMBRELLA
from ikwen.accesscontrol.models import Member
from ikwen.core.utils import get_service_instance, send_push, get_mail_content


from dbbackup.models import JobConfig, Backup
from cron import FAILED, SUCCESS, find_file_size

from ikwen.core.log import CRONS_LOGGING
logging.config.dictConfig(CRONS_LOGGING)
logger = logging.getLogger('ikwen.crons')


def notify_staff():
    now = datetime.now()
    start = now - timedelta(days=7)
    sender = 'ikwen DBBACKUP <no-reply@ikwen.com>'
    subject = _("Succeeded backups recap")
    service = get_service_instance()
    recipient_list = [service.member.email, 'k.sihon@ikwen.com', 'c.fotso@ikwen.com',
                      'r.yopa@ikwen.com', 'w.futchea@ikwen.com',
                      'y.siaka@ikwen.com', 'rmbogning@gmail.com']
    backup_list = [backup for backup in Backup.objects.order_by('-id').filter(status=SUCCESS)]
    database_list = [backup.job_config.db_name for backup in backup_list]
    hostname_list = [backup.job_config.hostname for backup in backup_list]
    total_size = sum([backup.file_size for backup in backup_list])
    type_list = [backup.job_config.db_type for backup in backup_list]
    s, unit = find_file_size(total_size)  # s is a constant that equals to 2 power the

    extra_context = {'database_list': list(set(database_list)),
                     'hostname_list': list(set(hostname_list)),
                     'type_list': list(set(type_list)),
                     'total_size': str(total_size % s) + unit,
                     'location': 'IKWEN_DB_BACKUPS',
                     'period': "Backups from  %s  to  %s" % (start, now)}
    activate('en')
    try:
        html_content = get_mail_content(subject,
                                        template_name='dbbackup/mails/failed_backup_notification.html',
                                        extra_context=extra_context)
    except:
        logger.error("Could not generate HTML content from template", exc_info=True)
        return
    msg = EmailMessage(subject, html_content, sender, recipient_list)
    msg.content_subtype = "html"
    msg.send()


if __name__ == '__main__':
    try:
        notify_staff()
    except:
        logger.error(u"Failed to send email of succeeded backups to staffs", exc_info=True)
