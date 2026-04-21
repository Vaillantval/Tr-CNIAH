# src/apps/contact/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm, ProfessionalRequestForm


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre message a été envoyé avec succès.')
            return redirect('contact:contact')
    else:
        form = ContactForm()

    return render(request, 'pages/contact/index.html', {'form': form})


def professional_request_view(request):
    if request.method == 'POST':
        form = ProfessionalRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre demande a été enregistrée.')
            return redirect('core:public_service')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())

    return redirect('core:public_service')