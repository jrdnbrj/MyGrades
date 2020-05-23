from django.shortcuts import render, redirect

# Create your views here.
def post_assigment(request):
    return render(request, 'post/post_assignment.html', {})

def post_assigment_2(request):
    return render(request, 'post/post_assignment_2.html', {})

def landing_page(request):
    return render(request, 'landing_page/landing_page.html', {})