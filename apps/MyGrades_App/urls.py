from django.urls import path
from .views import *

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('register', register, name='register'),
    path('register_verification', register_verification, name='register_verification'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),
    path('post', post_assigment, name='post_assignment'),
    path('post3', post_assignment_3, name = 'post_assignment_3'),
    path('work_place/', work_place, name='work_place'),
    path('wp_ajax', wp_ajax, name='wp_ajax'),
    path('work_place_2/<int:pk>', work_place_2, name='work_place_2'),
]