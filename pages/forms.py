from django import forms
from .models import ContactMessage

TAILWIND_INPUT = 'w-full rounded-lg border-gray-300 text-sm focus:ring-brand focus:border-brand'


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'class': TAILWIND_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'message':  # message đã set class riêng ở widgets
                field.widget.attrs.update({'class': TAILWIND_INPUT})