from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.views import View
from urllib.parse import urlencode
from .forms import SigninForm




def signin(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('litreview_app:home')
    else:
        form = SigninForm()
    return render(request, "users/signin.html", {"form":form})
def logout_user(request):
    return redirect('home')


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
    elif request.user.is_authenticated:
        return redirect("flux")
    else:
        return render(request, "users/login.html")


def logout(request):
    return redirect("users:login")


"""
_MESSAGES = {
    'not_same_password': "Vous avez entré deux mots de passe différents.",
    'username_already_used': "Le nom d'utilisateur '{username}' est déjà utilisé.",
    'incorrect_credentials': "Vos identifiants sont incorrects. Merci de réessayer."
}
 User = get_user_model()
 class LoginView(View):
    def get(self, request):
        form = SigninForm()
        error_message = request.GET.get('error_message')
        username = request.GET.get('username')

        if error_message is not None:
            error_message = _MESSAGES.get(error_message).format(username=username)
            context = {'form': form, 'error_message': error_message}
        return render(request, 'users/login.html', context)

    def post(self, request):
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            error_message = 'username_already_used'
            query = {'error_message': error_message, 'username': username}
            query_string = urlencode(query)
            return redirect(f'login?{query_string}')
        else:
            form = SigninForm(request.POST)
            if form.is_valid():
                user = form.save()
                # Uncomment the following line for production
                # return redirect('/auth/')

                # For debugging only
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                if user is not None and user.is_active:
                    login(request, user)
                    return redirect('/flux/')
                # TODO: Uncomment the line above and comment the line below for production

            else:
                error_message = 'not_same_password'
                query = {'error_message': error_message}
                query_string = urlencode(query)
                return redirect(f'login?{query_string}')
"""