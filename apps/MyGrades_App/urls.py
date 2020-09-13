from django.urls import path

from .views import *


urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('customer_support', customer_support, name='customer_support'),
    path('about', about, name='about'),
    path('contact', contact, name='contact'),
    path('privacy_policy', privacy_policy, name='privacy_policy'),

    path('register', register, name='register'),
    path('signin', signin, name='signin'),
    path('signout', signout, name='signout'),

    #just for test
    path('404/', handler404), 
    path('500/', handler500),

    path('assignments', user_assignments, name='user_assignments'),
    path('post_assignment', post_assignment, name='post_assignment'),
    path('post_assignment/<int:trabajo>', post_assignment_payment, name = 'post_assignment_payment'),
    path('post_assignment/<int:id>/edit', edit_post_assignment, name='edit_post_assignment'),
    path('delete_assignment/<int:id>', delete_assignment, name='delete_assignment'),
    path('assignment/<int:id>/accept_reject', accept_reject, name='accept_reject'),
    path('assignment/<int:id>/open_close', open_close, name='open_close'),
    path('assignment/send', send_assignment, name='send_assignment'),

    path('work_place', work_place, name='work_place'),
    path('wp_ajax', wp_ajax, name='wp_ajax'),
    path('work_place/<int:pk>', work_place_2, name='work_place_2'),
    path('work_place/<int:id>/conditions', work_place_3, name='work_place_3'),
    path('work_place/<int:id>/complete', work_place_4, name='work_place_4'),

    path('media/<path>', download_file, name='media/'),

    path('profile', user_profile, name='user_profile'),
    path('profile/<status>', user_profile_2, name='user_profile_2'),
    
    path('user/edit', edit_user, name='edit_user'),
    path('user/edit/info/', edit_user_info, name='edit_user_info'),
    path('user/edit/payment_method/', edit_payment_method, name='edit_payment_method'),
    path('user/edit/password/', edit_password, name='edit_password'),

    path('paypal/create/<int:id>', paypal_create, name='paypal_create'),
    path('paypal/<str:order_id>/capture/<int:trabajo_id>', paypal_capture, name="paypal_capture"),



    path('@<str:username>', public_profile, name='public_profile'),
]