from django.urls import path
from .views import *

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('register', register, name='register'),
    path('register_verification', register_verification, name='register_verification'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),
    path('post_assignment', post_assigment, name='post_assignment'),
    path('post_assignment_3', post_assignment_3, name = 'post_assignment_3'),
    path('work_place/', work_place, name='work_place'),
    path('wp_ajax', wp_ajax, name='wp_ajax'),
    path('work_place_2/<int:pk>', work_place_2, name='work_place_2'),
    path('work_place_3/<int:id>', work_place_3, name='work_place_3'),
    path('media/<path>', download_file, name='media/'),
    path('work_place_4/<int:id>', work_place_4, name='work_place_4'),
    path('user_interface/', user_interface, name='user_interface'),
    path('edit_post_assignment/<int:id>', edit_post_assignment, name='edit_post_assignment')
]