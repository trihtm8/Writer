from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'id':'login-username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'id':'login-password'}))

class RegisterForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username' , 'id':'register-username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'id':'register-password'}))
    repass = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat Password', 'id':'register-repass'}))

class MoreInfoRegisterForm1(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Your Email', 'id':'register-email'}))
    first_name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your First name' , 'id':'register-firstname'}))
    last_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Your Last name', 'id':'register-lastname'}))
    company = forms.CharField(required=False ,max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Your Company', 'id':'register-company'}))

class MoreInfoRegisterForm2(forms.Form):
    profile_name = forms.CharField(required=True ,widget=forms.TextInput(attrs={'class':'form-control', 'id':'register-profilename', 'placeholder': 'Set how to other see your name'}))
    pen_name = forms.CharField(required=False ,widget=forms.TextInput(attrs={'class':'form-control', 'id':'register-penname', 'placeholder':'Your name on writing'}))