from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, UserUpdateForm
from django.contrib.auth.models import User
from .models import Profile

def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile_form = ProfileForm(request.POST, instance=profile)
            profile_form.save()

            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("home")

    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()

    return render(request, "users/register.html", {
        "user_form": user_form,
        "profile_form": profile_form
    })

    
def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            next_url = request.GET.get("next")
            return redirect(next_url or "home")

        else:
            messages.error(request, "Invalid username or password")

    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')

@login_required
def profile(request):
    profile = request.user.profile
    return render(request, 'users/profile.html', {'profile': profile})



@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("home")  # ✅ redirects to home
        else:
            messages.error(request, "Please fix the errors below.")

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(request, "users/edit_profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "profile": profile
    })