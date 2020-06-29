from dbbackup.models import DestinationServer, JobConfig, Backup, DB_TYPES, RUN_EVERY
from django.forms import ModelForm
from django import forms


class BackupForm(ModelForm):
    """
    code BackupForm
    """
    class Meta:
        """comment of Meta class
        """
        model = Backup


class DestinationServerForm(ModelForm):
    """
    comment of class
    """
    class Meta:
        """
        comment of Meta
        """
        model = DestinationServer
        fields = '__all__'


class JobConfigForm(forms.Form):
    """
    comment of class
    """
    hostname = forms.IPAddressField(error_messages={'required': 'Please enter the hostname'},
                                    required=True, max_length=30)
    db_type = forms.ChoiceField(error_messages={'required': 'Please enter the database type'}, choices=DB_TYPES)
    db_name = forms.CharField(max_length=100, required=False)
    db_username = forms.CharField(max_length=100, required=False)
    db_password = forms.CharField(max_length=100, widget=forms.PasswordInput, required=False)
    run_every = forms.IntegerField(error_messages={'required': 'Please enter the run every period'},
                                   required=True, widget=forms.Select(choices=RUN_EVERY))
