from rest_framework import serializers
from .models import Users, Project, ProjectUser


class user_serializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id', 'name')


class project_serializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'name')

