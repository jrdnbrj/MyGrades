from django.urls import path
from .views import *

urlpatterns = [
    path('post', post_assigment, name = 'post_assignment'),
    path('post2', post_assigment2, name = 'post_assignment_2'),
]