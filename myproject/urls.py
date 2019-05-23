from django.urls import path

from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^users/create', UserViews.as_view()),
    url(r'^projects/create', ProjectViews.as_view()),
    url(r'^users/assignproject', assignProjectToUser),
    url(r'^projects/assignmentor', assignMentorToProject),
    path('projects/mentorprojlist/<int:user_id>/', getProjectsUserIsMentoring),
    path('projects/associates/<int:project_id>/', getProjectAssociates),
    path('projects/getmentees/<int:user_id>/', getProjectMentees)
]