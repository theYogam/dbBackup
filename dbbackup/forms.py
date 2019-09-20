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
        exclude = ('start_time',),


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
    # widget=forms.TextInput(
    # attrs={'class': 'form-control', 'placeholder': '192.168.0.25'}))
    db_type = forms.ChoiceField(error_messages={'required': 'Please enter the database type'}, choices=DB_TYPES)
    # , attrs={'class': 'form-control'}))
    # , 'placeholder': 'MySQL'
    db_name = forms.CharField(max_length=100, required=False)
    # widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': 'umbrella'}))
    db_username = forms.CharField(max_length=100, required=False)
    # , widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': 'theYogam'}))
    # db_password = forms.PasswordInput(attrs={'type': 'hidden'})
    db_password = forms.CharField(max_length=100, widget=forms.PasswordInput, required=False)
    # attrs={'type': 'hidden'}
    #     attrs={'class': 'form-control', 'placeholder': '$!@#ka3'}))
    run_every = forms.IntegerField(error_messages={'required': 'Please enter the run every period'},
                                   required=True, widget=forms.Select(choices=RUN_EVERY))

    # widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': '06 hours'}))
    # class Meta:
    #     model = JobConfig
    #     exclude = ['start_time, destination_server_list']
