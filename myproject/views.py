from django.db.utils import IntegrityError
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView
import json
from myproject.models import *
from .serializers import *


def invalid_request(func):

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as error:
            if 'UNIQUE' in error.args[0]:
                result_text = "Record already exists for the given user and project"
            else:
                result_text = "Database constraints violated"

            response = {
                'result': result_text,
                'status_code': 500,
                'message': 'Internal Server Error'
            }
            return HttpResponse(json.dumps(response))

        except Exception as error:
            response = {
                'result': error.args[0],
                'status_code': 500,
                'message': 'Internal Server Error'
            }
            return HttpResponse(json.dumps(response))

    return wrapper


# Create your views here.
class user_views(APIView):

    def post(self, request):
        try:
            if 'name' in request.data:
                user_name = request.data['name']
            else:
                response = {
                    'result': "Bad Request",
                    'status_code': 400,
                    'message': " 'name' field not found"
                }
                return HttpResponse(json.dumps(response), content_type="application/json")

            Users.objects.create(name=user_name)
            response = {
                'result': 'User added successfully',
                'status': True,
                'status_code': 201,
                'message': 'User added successfully.'
            }

            return HttpResponse(json.dumps(response), content_type="application/json")
        except Exception as error:
            return HttpResponse(error)

    def get(self, request):
        try:
            response = {
                'result': user_serializer(instance=Users.objects.all(), many=True).data,
                'status': True,
                'status_code': 200,
                'message': 'User List fetched successfully'
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
        except Exception as error:
            HttpResponse(error)


class ProjectViews(APIView):

    def post(self, request):
        try:

            if 'name' in request.data:
               project_name = request.data['name']
            else:
                response = {
                    'result': "Bad Request",
                    'status_code': 400,
                    'message': " 'name' field not found"
                }
                return HttpResponse(json.dumps(response), content_type="application/json")

            Project.objects.create(name=project_name)
            response = {
                'result': 'Project created successfully',
                'status': True,
                'status_code': 201,
                'message': 'Project created successfully.'
            }

            return HttpResponse(json.dumps(response), content_type="application/json")
        except Exception as error:
            return HttpResponse(error)

    def get(self, request):
        response = {
            'result': project_serializer(instance=Project.objects.all(), many=True).data,
            'status': True,
            'status_code': 200,
            'message': 'Projects List fetched successfully'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['POST'])
@invalid_request
def assign_project_to_user(request):
    data = json.loads(request.body.decode('utf-8'))
    if 'user_list' and 'project_id' in data:
        user_id_list = data.get('user_list')
        project_id = data.get('project_id')
    else:
        response = {
            'result': "Bad Request",
            'status_code': 400,
            'message': " 'user_list' and 'project_id' fields are required"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_object_list = Users.objects.filter(pk__in=user_id_list)
    project_object = Project.objects.get(pk=project_id)
    project_user_list = [ProjectUser(user=user_ob, project=project_object) for user_ob in user_object_list]
    ProjectUser.objects.bulk_create(project_user_list)

    response = {
        'result': 'Project assigned successfully',
        'status': True,
        'status_code' : 201,
        'message': 'Project assigned successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['POST'])
@invalid_request
def assign_mentor_to_project(request, project_id, mentor_id):
    ProjectUser.objects.create(user_id=mentor_id, project_id=Project.objects.get(pk=project_id), is_mentor=True)

    response = {
        'result': 'Mentor assigned to Project successfully',
        'status': True,
        'status_code': 201,
        'message': 'Mentor assigned to Project successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['GET'])
@invalid_request
def get_projects_user_is_mentoring(request, mentor_id):
    project_ids = ProjectUser.objects.filter(user_id=mentor_id, is_mentor=True).values_list('project__id', flat=True)
    projects = Project.objects.filter(pk__in=project_ids)
    response = {
        'result': project_serializer(instance=projects, many=True).data,
        'status': True,
        'status_code': 201,
        'message': 'Project List Fetched successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['GET'])
@invalid_request
def get_project_associates(request, project_id):
    project_object_list = ProjectUser.objects.filter(project=Project.objects.get(pk=project_id))

    mentee_ids = []
    mentor_ids = []
    for project_object in project_object_list:
        if project_object.is_mentor:
            mentor_ids.append(project_object.user_id)
        else:
            mentee_ids.append(project_object.user_id)
    mentor_ids = list(set(mentor_ids))
    mentee_ids = list(set(mentee_ids))
    response = {
        'result': {
            'mentee_ids' : mentee_ids,
            'mentor_ids': mentor_ids
        },
        'status': True,
        'status_code' : 201,
        'message': 'Associate List fetched successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
@require_http_methods(['GET'])
@invalid_request
def get_project_mentees(request, mentor_id):

    project_ids = ProjectUser.objects.filter(is_mentor=True, user=Users.objects.get(pk=mentor_id)).\
                                    values_list('project_id', flat = True).distinct()

    mentees_of_the_mentor = ProjectUser.objects.filter(project_id__in = list(project_ids), is_mentor=False).\
                                    values_list('user_id', flat=True).distinct()

    response = {
        'result': user_serializer(instance=Users.objects.filter(pk__in=mentees_of_the_mentor), many=True).data,
        'status': True,
        'status_code' : 201,
        'message': 'Mentees list fetched successfully.'
    }

    return HttpResponse(json.dumps(response), content_type="application/json")
