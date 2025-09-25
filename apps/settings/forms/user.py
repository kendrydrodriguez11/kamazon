from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(), required=True, label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="Confirm New Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar', 'email', 'phone', 'direction']
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'avatar': 'Avatar',
            'email': 'Email',
            'phone': 'Phone',
            'direction': 'Direction',
        }

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if not self.instance.check_password(current_password):
            raise ValidationError("The current password is incorrect.")

        if new_password and new_password != confirm_password:
            raise ValidationError("The new passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user