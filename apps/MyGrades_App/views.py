from django.shortcuts import render, redirect
from .forms import *
# Create your views here.
def post_assigment(request):
    if request.method == 'POST':
        print(request.POST)
        print(request.FILES)
        form = TrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            trabajo = form.save()
            print(trabajo.archivos)
            return render(request, 'post/post_assignment_2.html', {'trabajo': trabajo})
        else:
            print(form.errors)
    return render(request, 'post/post_assignment.html', {})

def post_assigment_2(request):
    return render(request, 'post/post_assignment_2.html', {})

def landing_page(request):
    return render(request, 'landing_page/landing_page.html', {})