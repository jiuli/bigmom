from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import render

from .forms import MyLoginForm


# Create your views here.
@login_required
def dashboard(request):
    return render(request, 'mylogin/dashboard.html',{'section':'dashboard'})

def user_login(request):
    if request.method == 'POST':
        form = MyLoginForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data
            user = authenticate(username=account['username'],
                                password=account['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('登录成功。')
                else:
                    return HttpResponse('账号不对。')
            else:
                return HttpResponse('账号不对。')
    else:
        form = MyLoginForm()
    return render(request, 'mylogin/login.html', {'form': form})
                