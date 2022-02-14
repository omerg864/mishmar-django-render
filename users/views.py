from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, AuthenticationForm
from mishmar.models import Settings as Settings
from .models import UserSettings as USettings
from requests import get
from mishmar.models import IpBan
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext as _
from django.utils import translation
from django.views.generic import UpdateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.template.defaulttags import register as register_tag
import re


def login(request):
    translation.activate('he')
    request.session[translation.LANGUAGE_SESSION_KEY] = 'he'
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('Home')
        else:
            messages.warning(request, "שם משתמש או סיסמא לא נכונים")
            return HttpResponseRedirect('/login')

    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def register(request, *args, **kwargs):
    translation.activate('he')
    request.session[translation.LANGUAGE_SESSION_KEY] = 'he'
    settings = Settings.objects.first()
    pin_code = int(settings.pin_code)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print('My public IP address is: {}'.format(ip))
    ips = IpBan.objects.all()
    ban = False
    if len(ips.filter(ipaddress=ip)) > 0:
        new_ip = ips.filter(ipaddress=ip).first()
        if new_ip.num_tries > 15:
            ban = True
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if ban:
            return render(request, "users/register.html", {"form": form, "ban": ban})
        ips = IpBan.objects.all()
        if len(ips.filter(ipaddress=ip)) == 0:
            new_ip = IpBan(ipaddress=ip, num_tries=1)
            new_ip.save()
        else:
            new_ip = ips.filter(ipaddress=ip).first()
            new_ip.num_tries += 1
            new_ip.save()
        pc = int(request.POST.get("pin_code"))
        if pc != pin_code:
            messages.warning(request, "קוד זיהוי לא נכון")
        elif User.objects.all().filter(email=request.POST.get("email")).count() > 0:
            messages.warning(request, "כתובת דואר אלקטרוני קיימת כבר")
        elif form.is_valid():
            form.save(commit=True)
            username = form.cleaned_data.get("username")
            messages.success(request, f'{username}נוצר חשבון ל ')
            return redirect("login")
        else:
            for key in form.errors:
                print(key)
                print(_(form.errors[key].as_text()))
            messages.warning(request, form.errors)
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form, "ban": ban})


@login_required
def profile(request):
    translation.activate('he')
    request.session[translation.LANGUAGE_SESSION_KEY] = 'he'
    user_settings = USettings.objects.all().filter(user=request.user).first()
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        user_settings.language = request.POST.get("languages")
        if u_form.is_valid():
            u_form.save()
            user_settings.save()
            messages.success(request, f'פרטים עודכנו')
            return redirect("profile")
        else:
            messages.warning(request, f'פרטים לא עודכנו')
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
    context = {
        "u_form": u_form,
        "night": user_settings.night,
        "sat_night": user_settings.sat_night,
        "sat_morning": user_settings.sat_morning,
        "sat_noon": user_settings.sat_noon,
        "language": user_settings.language
    }
    return render(request, "users/profile.html", context)


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    queryset = User.objects.all().exclude(username='admin').exclude(username='metagber')
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    ordering = ['id']

    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        ctx = super(UserListView, self).get_context_data(**kwargs)

        return ctx
    
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            if request.POST.get("action") == "delete":
                id = request.POST.get("delete")
                User.objects.filter(id=id).delete()
                messages.success(request, f'משתמש נמחק')
                return redirect("user-list")
            elif 'change' in request.POST:
                id = request.POST.get("change")
                user = User.objects.filter(id=id).first()
                username = request.POST.get(f"username{id}")
                if User.objects.filter(username=username).count() > 0:
                    if User.objects.filter(username=username).count() == 1:
                        messages.warning(request, f'שם משתמש קיים כבר')
                        return redirect("user-list")
                    messages.warning(request, f'שם משתמש קיים כבר')
                    return redirect("user-list")
                elif re.match(r'^[a-zA-Z0-9_.-]+$', username) == None:
                    messages.warning(request, f'שם משתמש לא תקין')
                    return redirect("user-list")
                user.username = username
                email = request.POST.get(f"email{id}")
                if User.objects.filter(email=email).count() > 0:
                    messages.warning(request, f'כתובת דואר אלקטרוני קיימת כבר')
                    return redirect("user-list")
                user.email = email
                user.first_name = request.POST.get(f"first{id}")
                user.last_name = request.POST.get(f"last{id}")
                user_settings = USettings.objects.all().filter(user=user).first()
                nickname = request.POST.get(f"nickname{id}")
                if USettings.objects.filter(nickname=nickname).count() > 0:
                    messages.warning(request, f'כינוי קיים כבר')
                    return redirect("user-list")
                user_settings.nickname = nickname
                if request.POST.get(f"staff{id}") != None:
                    user.groups.add(Group.objects.get(name='staff'))
                else:
                    user.groups.remove(Group.objects.get(name='staff'))
                if request.POST.get(f"manager{id}") != None:
                    user.groups.add(Group.objects.get(name='manager'))
                else:
                    user.groups.remove(Group.objects.get(name='manager'))
                user_settings.save()
                user.save()
                messages.success(request, f'משתמש שונה')
                return redirect("user-list")
        return redirect("user-list")

@register_tag.filter
def isStaff(user):
    return user.groups.filter(name='staff').exists()

@register_tag.filter
def isManager(user):
    return user.groups.filter(name='manager').exists()

@register_tag.filter
def get_nickname(user):
    return USettings.objects.all().filter(user=user).first().nickname