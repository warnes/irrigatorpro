from django.forms import ModelForm

from notifications.models import NotificationsRule


class NotificationsForm(ModelForm):
    class Meta:
        model=NotificationsRule
        fields = [label, farm, field_list, recipients, notification_type, level, delivery_time, time_zone, recipients]


