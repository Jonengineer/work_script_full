from django import forms
from .models import ObjectAnalog

class ObjectAnalogForm(forms.ModelForm):
    class Meta:
        model = ObjectAnalog
        fields = ['is_check', 'description']