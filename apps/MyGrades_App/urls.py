from django.urls import path

from .views import *


urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('customer_support', customer_support, name='customer_support'),

    path('register', register, name='register'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),
    path('about', about, name='about'),
    path('contact', contact, name='contact'),
    path('privacy_policy', privacy_policy, name='privacy_policy'),
    path('404/', handler404),

    path('post_assignment', post_assignment, name='post_assignment'),
    path('post_assignment/<int:trabajo>', post_assignment_payment, name = 'post_assignment_payment'),
    # path('post_assignment_complete/<str:trabajo>', post_assignment_complete, name = 'post_assignment_complete'),

    path('work_place', work_place, name='work_place'),
    path('wp_ajax', wp_ajax, name='wp_ajax'),
    path('work_place/<int:pk>', work_place_2, name='work_place_2'),
    path('work_place_3/<int:id>', work_place_3, name='work_place_3'),
    path('work_place_4/<int:id>', work_place_4, name='work_place_4'),

    path('media/<path>', download_file, name='media/'),

    path('profile', user_profile, name='user_profile'),
    path('profile/<status>', user_profile_2, name='user_profile_2'),
    path('post_assignment/edit/<int:id>', edit_post_assignment, name='edit_post_assignment'),
    path('assignments', user_assignments, name='user_assignments'),
    path('edit_user/', edit_user, name='edit_user'),
    path('edit_user_info/', edit_user_info, name='edit_user_info'),
    path('edit_payment_method/', edit_payment_method, name='edit_payment_method'),
    path('edit_password/', edit_password, name='edit_password'),
    
    path('send_assignment/', send_assignment, name='send_assignment'),

    path('paypal/create/<int:id>', paypal_create, name='paypal_create'),
    path('paypal/<str:order_id>/capture/<int:trabajo_id>', paypal_capture, name="paypal_capture"),



    path('<str:username>', public_profile, name='public_profile'),
]