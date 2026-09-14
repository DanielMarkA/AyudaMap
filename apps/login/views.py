from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import UserLoginForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home:home")
        else:
            return render(request, "login/login.html", {
                "form": form,
                "error": "Invalid username or password.",
            })
    else:
        form = UserLoginForm()

    return render(request, "login/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login:login")