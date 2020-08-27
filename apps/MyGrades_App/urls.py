from django.urls import path

from .views import *


urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('register', register, name='register'),
    # path('register_verification', register_verification, name='register_verification'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),

    path('post_assignment', post_assignment, name='post_assignment'),
    path('post_assignment_3', post_assignment_3, name = 'post_assignment_3'),
    path('post_assignment_4', post_assignment_4, name = 'post_assignment_4'),

    path('work_place/', work_place, name='work_place'),
    path('wp_ajax', wp_ajax, name='wp_ajax'),
    path('work_place_2/<int:pk>', work_place_2, name='work_place_2'),
    path('work_place_3/<int:id>', work_place_3, name='work_place_3'),
    path('work_place_4/<int:id>', work_place_4, name='work_place_4'),

    path('media/<path>', download_file, name='media/'),

    path('profile/', user_profile, name='user_profile'),
    path('edit_profile/', user_profile_2, name='user_profile_2'),
    path('edit_post_assignment/<int:id>', edit_post_assignment, name='edit_post_assignment'),
    path('assignments/', user_assignments, name='user_assignments'),
    path('edit_user/', edit_user, name='edit_user'),
    path('edit_user_info/', edit_user_info, name='edit_user_info'),
    path('edit_payment_method/', edit_payment_method, name='edit_payment_method'),
    path('edit_password/', edit_password, name='edit_password'),
    
    path('send_assignment/', send_assignment, name="send_assignment"),

]