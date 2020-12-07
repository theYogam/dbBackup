from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from ikwen.core.models import Model

LANGUAGES = (
        ('en', 'English'),
        ('fr', 'French'),
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
    """
    code
    """
    ip = models.IPAddressField(_("Server IP"), max_length=32)
    username = models.CharField(_("Server username"), max_length=100)
    password = models.CharField(_("Server password"), max_length=100)
    port = models.IntegerField(_("Server port"), default=22, blank=True)

    def __unicode__(self):
        return self.ip


class JobConfig(Model):
    """
    code
    """
    hostname = models.IPAddressField(_("Hostname"), max_length=16)
    db_type = models.CharField(_("Database type"), max_length=100, choices=DB_TYPES)
    db_name = models.CharField(_("Database name"), max_length=100, null=True, blank=True)
    db_username = models.CharField(_("Database username"), max_length=100, null=True, blank=True)
    db_password = models.CharField(_("Database password"), max_length=100, null=True, blank=True)
    run_every = models.IntegerField(_("Run every"), choices=RUN_EVERY, )
    destination_server_list = ListField(EmbeddedModelField('DestinationServer'))

    def __unicode__(self):
        return "Job %s" % self.created_on.ctime()


class Backup(Model):
    """
    code
    """
    job_config = models.ForeignKey(JobConfig)
    status = models.CharField(_("Status"), max_length=12)
    run_time = models.IntegerField(_("Run time"), blank=True, null=True, default=0, help_text=_("Running time of the backup in seconds"))
    relative_file_path = models.CharField(_("Backup relative file path"), max_length=100)
    file_size = models.IntegerField(_("Backup file size"), blank=True, null=True)
    file_size_hr = models.CharField(_("Backup file size in human-readable format"), max_length=100)
    error_messages = models.TextField(_("Error messages"))

    def __unicode__(self):
        return self.id


