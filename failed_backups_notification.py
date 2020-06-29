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
from cron import FAILED, SUCCESS

from ikwen.core.log import CRONS_LOGGING
logging.config.dictConfig(CRONS_LOGGING)
logger = logging.getLogger('ikwen.crons')


def notify_staff():
    now = datetime.now()
    start = now - timedelta(days=7)
    for backup in Backup.objects.order_by('-id').filter(status=FAILED):
        sender = 'ikwen DBBACKUP <no-reply@ikwen.com>'
        subject = _("New failed backup")
        service = get_service_instance()
        recipient_list = [service.member.email, 'k.sihon@ikwen.com', 'c.fotso@ikwen.com',
                          'r.yopa@ikwen.com', 'w.futchea@ikwen.com',
                          'y.siaka@ikwen.com', 'rmbogning@gmail.com']
        job_config = backup.job_config
        extra_context = {'hostname': job_config.hostname,
                         'db_name': job_config.db_name,
                         'db_type': job_config.db_type,
                         'status': backup.status,
                         'start_time': backup.created_on,
                         'file_size_hr': backup.file_size_hr,
                         'error_messages': backup.error_messages}
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
        logger.error(u"Failed to send email of failed backups to staff", exc_info=True)
