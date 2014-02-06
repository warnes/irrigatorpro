#! /usr/bin/env python2.7
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)

def auth_view(request, onsuccess='/registration/logged_in/', onfail='/registration/login/'):
    email    = request.POST.get('email',   '')
    password = request.POST.get('password','')
    user     = auth.authenticate(email=email, password=password)
    if user is not None:
        auth.login(request, user)
        return redirect(onsuccess)
    else:
        return redirect(onfail)  

def create_user(email, email, password):
    user = User(email=email, email=email)
    user.set_password(password)
    user.save()
    return user

def user_exists(email):
    user_count = User.objects.filter(email=email).count()
    if user_count == 0:
        return False
    return True

def sign_up_in(request):
    post = request.POST
    if not user_exists(post['email']): 
        user = create_user(email=post['email'], email=post['email'], password=post['password'])
    	return auth_and_login(request)
    else:
    	return redirect("/login/")

@login_required(login_url='/login/')
def secured(request):
    return render_to_response("secure.html")
