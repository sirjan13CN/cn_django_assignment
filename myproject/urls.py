from django.urls import path

from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^users/$', user_views.as_view()),
    url(r'^users/assign-project', assign_project_to_user),
    url(r'^projects/$', ProjectViews.as_view()),
    path('projects/<int:project_id>/assign-mentor/<int:mentor_id>', assign_mentor_to_project),
    path('mentors/<int:mentor_id>/projects/', get_projects_user_is_mentoring),
    path('projects/<int:project_id>/associates/', get_project_associates),
    path('mentors/<int:mentor_id>/mentees/', get_project_mentees)
]