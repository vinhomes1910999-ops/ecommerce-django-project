from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .models import StaticPage


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất.')
            return redirect('pages:contact')
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {'form': form})


def static_page_view(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    return render(request, 'pages/static_page.html', {'page': page})