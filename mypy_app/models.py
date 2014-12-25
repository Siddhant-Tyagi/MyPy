from django.db import models

class add_server(models.Model):
    mysql_server_name = models.CharField(max_length=200, unique=True, null=False)
    mysql_host = models.CharField(max_length=200, null=False)
    mysql_port = models.CharField(max_length=10, null=False, default="3306")
    mysql_user = models.CharField(max_length=200, null=False)
    mysql_password = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return '%s %s %s %s %s' %(self.mysql_server_name, self.mysql_host, self.mysql_port, \
                self.mysql_user, self.mysql_password)
