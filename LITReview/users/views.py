from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import SigninForm, UserUpdateForm, ProfileUpdateForm, LoginForm


class SigninView(View):
    def get(self, request):
        form = SigninForm()
        context = {'form': form}
        return render(request, 'users/signin.html', context)

    def post(self, request):
        form = SigninForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        context = {'form': form}
        return render(request, 'users/signin.html', context)

class LoginView(View):
    """View for user login."""
    def get(self, request):
        """Render the login page with the login form."""
        if request.user.is_authenticated:
            return redirect("flux")
        form = LoginForm()
        context = {"form": form
                   }
        return render(request, "users/login.html", context)

    def post(self, request):
        """Handle the login form submission."""
        if request.user.is_authenticated:
            return redirect("flux")
        user = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=user, password=password)

        if user is not None:
            login(request, user)
            return redirect("flux")
        else:
            return redirect("login")
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profilemodel)
        context = {'u_form': u_form, 'p_form': p_form}
        return render(request, 'users/profiles.html', context)

    def post(self, request):
        u_form = UserUpdateForm(request.POST or None, instance=request.user)
        p_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user.profilemodel)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
        context = {'u_form': u_form, 'p_form': p_form}
        return render(request, 'users/profiles.html', context)

def logout(request):
    request.user.is_authenticated = False
    return redirect('login')

