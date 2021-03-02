import os
import logging
import sys
from datetime import datetime, timedelta

sys.path.append("/home/libran/virtualenv/lib/python2.7/site-packages")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.settings')

from django.core import mail
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _, activate


from ikwen.accesscontrol.backends import UMBRELLA
from ikwen.accesscontrol.models import Member
from ikwen.core.utils import get_service_instance, send_push, get_mail_content


from dbbackup.models import JobConfig, Backup
from cron import FAILED, SUCCESS, find_file_size

# from ikwen.core.log import CRONS_LOGGING
# logging.config.dictConfig(CRONS_LOGGING)
logger = logging.getLogger('ikwen.crons')


def notify_staff():
    now = datetime.now()
    start = now - timedelta(days=7)
    sender = 'ikwen DBBACKUP <no-reply@ikwen.com>'
    subject = _("Succeeded Backups Report")
    recipient_list = [get_service_instance().member.email]
    staff_list = [staff.email for staff in Member.objects.filter(is_staff=True)]
    backup_list = [backup for backup in Backup.objects.order_by('-id').filter(status=SUCCESS)]
    job_config_list = [backup.job_config for backup in backup_list]
    total_size = sum([backup.file_size for backup in backup_list])
    s, unit = find_file_size(total_size)  # s is a constant that equals to 2 power the

    extra_context = {'job_config_list': list(set(job_config_list)),
                     'total_size': str(total_size / s) + unit,
                     'location': 'IKWEN_DB_BACKUPS',
                     'period': "From  %s  to  %s" %
                               (start.strftime('%Y/%m/%d %H:%M'), now.strftime('%Y/%m/%d %H:%M'))}
    activate('en')
    try:
        html_content = get_mail_content(subject,
                                        template_name='dbbackup/mails/succeeded_backup_notification.html',
                                        extra_context=extra_context)
    except:
        logger.error("Could not generate HTML content from template", exc_info=True)
        return
    msg = EmailMessage(subject, html_content, sender, recipient_list)
    msg.content_subtype = "html"
    msg.bcc = staff_list
    msg.send()


if __name__ == '__main__':
    try:
        notify_staff()
    except:
        logger.error(u"Failed to send email of succeeded backups to staffs", exc_info=True)
