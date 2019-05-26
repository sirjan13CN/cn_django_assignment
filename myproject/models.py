from django.db import models


class Users(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255)
    proj_user = models.ManyToManyField('Users', through='ProjectUser')

    def __str__(self):
        return self.name


class ProjectUser(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    is_mentor = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'project')
