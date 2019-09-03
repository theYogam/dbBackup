from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField
from django.utils.translation import gettext_lazy as _

from ikwen.core.models import Model

LANGUAGES = (
        ('EN', 'English'),
        ('FR', 'French'),
)

DB_TYPES = (
    ('MySQL', 'MySQL'),
    ('MongoDB', 'MongoDB'),
    ('PostgreSQL', 'PostgreSQL'),
    ('Firebase', 'Firebase'),
)

RUN_EVERY = (
    ('3', '3'),
    ('6', '6'),
    ('12', '12'),
    ('24', '24'),
)


class DestinationServer(Model):
    ip = models.IPAddressField(_("Server IP"), max_length=16)
    # , placeholder="192.168.0.25"
    username = models.CharField(_("Server username"), max_length=100)
    # , placeholder='admin'
    password = models.CharField(_("Server password"), max_length=100)

    def __unicode__(self):
        return self.ip


class JobConfig(Model):
    hostname = models.IPAddressField(_("Hostname"), max_length=16)
    # , placeholder="192.168.0.25"
    db_type = models.CharField(_("Database type"), null=False, max_length=100, choices=DB_TYPES,)
    db_name = models.CharField(_("Database name"), max_length=100, null=True)
    db_username = models.CharField(_("Database username"), max_length=100)
    # , placeholder='admin'
    db_password = models.CharField(_("Database password"), max_length=100)
    run_every = models.IntegerField(_("Run every"), choices=RUN_EVERY, )
    # , placeholder='6'
    destination_server_list = ListField(EmbeddedModelField('DestinationServer'))

    def __unicode__(self):
        return "Job %s" % unicode(self.id)


class Backup(Model):
    job_config = models.ForeignKey(JobConfig)
    status = models.CharField(_("Status"), max_length=12, editable=False)
    start_time = models.DateTimeField(_("Start time"), auto_now_add=True, null=True)
    file_log_name = models.CharField(_("File log name"), max_length=100)
    file_log_size = models.CharField(_("File log size"), max_length=100)

    def __unicode__(self):
        return self.id


