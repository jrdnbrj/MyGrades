from django.urls import path
from .views import *

urlpatterns = [
    path('post', post_assigment, name='post_assignment'),
    #path('post2', post_assigment_2, name = 'post_assignment_2'),
    path('', landing_page, name='landing_page'),
    path('register', register, name='register'),
    path('register_verification', register_verification, name='register_verification'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),
]