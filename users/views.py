from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
import django.contrib.messages

from users.models import Person
from .forms import CustomUserCreationForm
from .forms import *


class LoginView(TemplateView, View):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                messages.success(request, "You are now logged in!")
            else:
                messages.warning(request, "The password is valid, but the account has been disabled!")
        else:
            # the authentication system was unable to verify the username and password
            messages.warning(request, "The username and password were incorrect.")

        return redirect(request.POST.get('next', 'home'))

class LogoutView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')

        logout(request)
        messages.success(request, "You are now logged out!")
        return redirect('home')

class RegisterView(TemplateView):
    template_name = 'users/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, "You are already logged in!")
            return redirect('home')
        return self.render_to_response({'form': CustomUserCreationForm()})

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You can now login!")
            return redirect('home')
        else:
            return self.render_to_response({'form': form})


class MembersView(LoginRequiredMixin, TemplateView, View):
    template_name = 'users/members_only.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})


class ProfileView(TemplateView, View):
    template_name = 'users/profile.html'
    data = LoadCreditsForm

    def get(self, request, *args, **kwargs):
        form = LoadCreditsForm()
        return self.render_to_response({'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            form = self.data(data=request.POST)
            user = request.user
            if form.is_valid():
                if form.cleaned_data['insert_credit']:
                    amount = form.cleaned_data['insert_credit']
                    user.insert_credits(amount)
                    messages.info(request, 'Credits Inserted successfully')

                elif form.cleaned_data['withdraw_credit']:
                    amount = form.cleaned_data['withdraw_credit']
                    user.withdraw_credits(amount)

                    messages.info(request, 'Credits withdrawed successfully')
                return self.render_to_response({'amount': amount})
        messages.info(request, 'Need to be Logged in')
        return redirect('games')

