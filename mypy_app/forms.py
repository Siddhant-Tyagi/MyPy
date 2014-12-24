from django import forms
from mypy_app.models import add_server

class Add_Server_Form(forms.ModelForm):
    mysql_server_name = forms.CharField(widget=forms.TextInput(attrs={'class' : 'input'}), \
            max_length=128, label="MySQL Server Name ")
    mysql_host = forms.CharField(widget=forms.TextInput(attrs={'class' : 'input'}), \
            max_length=128, label="MySQL Host IP ")
    mysql_port = forms.CharField(widget=forms.TextInput(attrs={'class' : 'input'}), \
            max_length=128, label="MySQL Port ")
    mysql_user = forms.CharField(widget=forms.TextInput(attrs={'class' : 'input'}), \
            max_length=128, label="MySQL Username ")
    mysql_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}), \
            label="MySQL Password ")

    class Meta:
        model = add_server
        """widget = {
                'mysql_password': forms.PasswordInput(),
                    }"""
        fields = ('mysql_server_name', 'mysql_host', 'mysql_port', 'mysql_user', 'mysql_password')
