from django import forms
from mypy_app.models import add_server

class Add_Server_Form(forms.ModelForm):
    mysql_server_name = forms.CharField(max_length=128, label="MySQL Server Name ")
    mysql_host = forms.CharField(max_length=128, label="MySQL Host IP ")
    mysql_port = forms.CharField(max_length=128, label="MySQL Port ")
    mysql_username = forms.CharField(max_length=128, label="MySQL Username ")
    mysql_password = forms.CharField(widget=forms.PasswordInput(), label="MySQL Password ")

    class Meta:
        model = add_server
        """widget = {
                'mysql_password': forms.PasswordInput(),
                    }"""
        fields = ('mysql_server_name', 'mysql_host', 'mysql_port', 'mysql_username', 'mysql_password')
