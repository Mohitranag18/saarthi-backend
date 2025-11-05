from django.contrib import admin
from django.contrib.gis import forms
from .models import EmergencyRequests, VolunteerLocations

# Disable map widget for both models
class NoMapEmergencyForm(forms.ModelForm):
    class Meta:
        model = EmergencyRequests
        fields = "__all__"
        widgets = {
            "location": forms.TextInput(),  # simple text field
        }

class NoMapVolunteerForm(forms.ModelForm):
    class Meta:
        model = VolunteerLocations
        fields = "__all__"
        widgets = {
            "location": forms.TextInput(),
        }

@admin.register(EmergencyRequests)
class EmergencyRequestsAdmin(admin.ModelAdmin):
    form = NoMapEmergencyForm
    def save_model(self, request, obj, form, change):
        if not change or not obj.user_id:
            obj.user = request.user  # attach admin user automatically
        super().save_model(request, obj, form, change)


@admin.register(VolunteerLocations)
class VolunteerLocationsAdmin(admin.ModelAdmin):
    form = NoMapVolunteerForm
