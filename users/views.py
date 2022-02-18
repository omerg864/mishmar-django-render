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
import base64


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
        try:
            image =  request.FILES['imagefile']
            b64 = base64.b64encode(image.file.read())
            bytesv = b'data:image/png;base64,' + b64
            user_settings.image = bytesv.decode("utf-8")
        except:
            print("no image")
        if u_form.is_valid():
            email = u_form.cleaned_data.get("email")
            if User.objects.filter(email=email).count() > 0:
                    if request.user != User.objects.filter(email=email).first():
                        messages.warning(request, f'כתובת דואר אלקטרוני קיימת כבר')
                        return redirect("profile")
            u_form.save()
            user_settings.save()
            messages.success(request, f'פרטים עודכנו')
            return redirect("profile")
        else:
            messages.warning(request, f'פרטים לא עודכנו')
            messages.warning(request, u_form.errors)
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
    context = {
        "u_form": u_form,
        "user_settings": user_settings,
    }
    return render(request, "users/profile.html", context)


class UserPasswordUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = ['password']
    template_name = 'users/password_change.html'
    success_url = '/'

    def test_func(self):
        return isStaff(self.request.user) or self.request.user == self.get_object()
    
    def get_context_data(self, **kwargs):
        ctx = super(UserPasswordUpdateView, self).get_context_data(**kwargs)
        ctx['user1'] = self.get_object()
        ctx['user1s'] = USettings.objects.all().filter(user=self.get_object()).first()
        return ctx
    
    def post(self, request, *args, **kwargs):
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1):
                user = self.get_object()
                user.set_password(password1)
                user.save()
                messages.success(request, f'סיסמא עודכנה')
                return redirect('/')
            else:
                messages.warning(request, "סיסמא חייבת להכיל לפחות שמונה תווים מתוכן לפחות אחד מהאותיות האנגליות ומספרים")
                return HttpResponseRedirect(request.path_info)
        else:
            messages.warning(request, 'סיסמאות לא תואמות')
            return HttpResponseRedirect(request.path_info)

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    queryset = User.objects.all().exclude(username='admin')
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    ordering = ['id']

    def test_func(self):
        return isStaff(self.request.user)
    
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
            elif 'password' in request.POST:
                id = request.POST.get("password")
                return redirect("password-change", id)
            elif 'change' in request.POST:
                id = request.POST.get("change")
                user = User.objects.filter(id=id).first()
                username = request.POST.get(f"username{id}")
                if User.objects.filter(username=username).count() > 0:
                    if user != User.objects.filter(username=username).first():
                        messages.warning(request, f'שם משתמש קיים כבר')
                        return redirect("user-list")
                elif re.match(r'^[a-zA-Z0-9_.-]+$', username) == None:
                    messages.warning(request, f'שם משתמש לא תקין')
                    return redirect("user-list")
                user.username = username
                email = request.POST.get(f"email{id}")
                if User.objects.filter(email=email).count() > 0:
                    if user != User.objects.filter(email=email).first():
                        messages.warning(request, f'כתובת דואר אלקטרוני קיימת כבר')
                        return redirect("user-list")
                user.email = email
                user.first_name = request.POST.get(f"first{id}")
                user.last_name = request.POST.get(f"last{id}")
                user_settings = USettings.objects.all().filter(user=user).first()
                nickname = request.POST.get(f"nickname{id}")
                if USettings.objects.filter(nickname=nickname).count() > 0:
                    if user_settings != USettings.objects.filter(nickname=nickname).first():
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


class QualityUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = USettings
    queryset = USettings.objects.all().exclude(user__username='admin').exclude(user__username='metagber')
    template_name = 'users/quality_user_list.html'
    context_object_name = 'users'
    ordering = ['id']

    def test_func(self):
        return isStaff(self.request.user)
    
    def post(self, request, *args, **kwargs):
        if 'reset' in request.POST:
            users = USettings.objects.all().exclude(user__username='admin').exclude(user__username='metagber')
            for user in users:
                id = user.id
                user.night = 0
                user.sat_night = 0
                user.sat_morning = 0
                user.fri_noon = 0
                user.save()
            messages.success(request, f'איכויות אופסו')
            return redirect("quality-list")
        else:
            users = USettings.objects.all().exclude(user__username='admin').exclude(user__username='metagber')
            for user in users:
                id = user.id
                user.night = request.POST.get(f"night{id}")
                print(request.POST.get(f"night{id}"))
                print(user)
                user.sat_night = request.POST.get(f"sat_night{id}")
                user.sat_morning = request.POST.get(f"sat_morning{id}")
                user.fri_noon = request.POST.get(f"fri_noon{id}")
                if request.POST.get(f"sat{id}") == 'on':
                    user.sat = True
                else:
                    user.sat = False
                user.save()
            messages.success(request, f'נתונים עודכנו')
            return redirect("quality-list")


@register_tag.filter
def isStaff(user):
    return user.groups.filter(name='staff').exists()

@register_tag.filter
def isManager(user):
    return user.groups.filter(name='manager').exists()

@register_tag.filter
def get_nickname(user):
    return USettings.objects.all().filter(user=user).first().nickname