from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView
import json
from myproject.models import *
from .serializers import *


# Create your views here.
class UserViews(APIView):

    def post(self, request):
        user_name = request.data['name']

        Users.objects.create(name=user_name)
        response = {
            'result': 'User added successfully',
            'status': True,
            'status_code': 201,
            'message': 'User added successfully.'
        }

        return HttpResponse(json.dumps(response), content_type="application/json")

    def get(self, request):
        response = {
            'result': UserSerializer(instance = Users.objects.all(), many = True).data,
            'status': True,
            'status_code': 200,
            'message': 'User List fetched successfully'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")


class ProjectViews(APIView):

    def post(self, request):
        project_name = request.data['name']

        Project.objects.create(name=project_name)
        response = {
            'result': 'Project created successfully',
            'status': True,
            'status_code': 201,
            'message': 'Project created successfully.'
        }

        return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['POST'])
def assignProjectToUser(request):
    data = json.loads(request.body.decode('utf-8'))
    user_id_list = data.get('user_list')
    project_id = data.get('proj_id')
    project_ob = Project.objects.get(id = project_id)

    for user_id in user_id_list:
        user_ob = Users.objects.get(id = user_id)
        ProjectUser.objects.create(user=user_ob, project=project_ob)

    response = {
        'result': 'Project assigned successfully',
        'status': True,
        'status_code' : 201,
        'message': 'Project assigned successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['POST'])
def assignMentorToProject(request):
    data = json.loads(request.body.decode('utf-8'))
    user_id = data.get('user_id')
    project_id = data.get('proj_id')
    project_ob = Project.objects.get(id = project_id)
    user_ob = Users.objects.get(id = user_id)
    ProjectUser.objects.create(user=user_ob, project=project_ob, is_mentor=True)

    response = {
        'result': 'Mentor assigned to Project successfully',
        'status': True,
        'status_code' : 201,
        'message': 'Mentor assigned to Project successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['GET'])
def getProjectsUserIsMentoring(request, user_id):
    user_ob = Users.objects.get(id = user_id)
    project_ids_qs = ProjectUser.objects.filter(user=user_ob, is_mentor=True).values_list('project_id', flat=True)
    project_ids = []
    for proj_id in project_ids_qs:
        project_ids.append(proj_id)
    response = {
        'result': project_ids,
        'status': True,
        'status_code' : 201,
        'message': 'Mentor assigned to Project successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['GET'])
def getProjectsUserIsMentoring(request, user_id):
    user_ob = Users.objects.get(id = user_id)
    project_ids_qs = ProjectUser.objects.filter(user=user_ob, is_mentor=True).values_list('project_id', flat=True).distinct()
    project_ids = []
    for proj_id in project_ids_qs:
        project_ids.append(proj_id)
    response = {
        'result': project_ids,
        'status': True,
        'status_code' : 201,
        'message': 'Mentor List fetched successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['GET'])
def getProjectAssociates(request, project_id):
    project_ob = Project.objects.get(id = project_id)
    project_ob_qs = ProjectUser.objects.filter(project=project_ob)

    user_ids = []
    mentor_ids = []
    for proj_ob in project_ob_qs:
        if proj_ob.is_mentor:
            mentor_ids.append(proj_ob.user_id)
        else:
            user_ids.append(proj_ob.user_id)
    mentor_ids = list(set(mentor_ids))
    user_ids = list(set(user_ids))
    response = {
        'result': {
            'user_ids' : user_ids,
            'mentor_ids': mentor_ids
        },
        'status': True,
        'status_code' : 201,
        'message': 'Mentor assigned to Project successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['GET'])
def getProjectMentees(request, user_id):
    user_ob = Users.objects.get(id=user_id)

    project_ids = ProjectUser.objects.filter(is_mentor=True, user = user_ob).\
                                    values_list('project_id', flat = True).distinct()

    mentees_of_the_projects = ProjectUser.objects.filter(project_id__in = list(project_ids), is_mentor=False).\
                                values_list('user_id', flat=True).distinct()

    user_ids = [user_id for user_id in mentees_of_the_projects]

    response = {
        'result': user_ids,
        'status': True,
        'status_code' : 201,
        'message': 'Mentees list fetched successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")
