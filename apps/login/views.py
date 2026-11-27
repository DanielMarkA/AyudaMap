from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UserLoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home:dashboard")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("home:dashboard")
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
    messages.info(request, "You have been safely signed out.")
    return redirect("login:login")
