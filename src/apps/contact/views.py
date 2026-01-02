#src\apps\contact\views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage, ProfessionalRequest


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        message_text = request.POST.get('message')
        subject = request.POST.get('subject', 'general')

        if name and email and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message_text
            )
            messages.success(request, 'Votre message a été envoyé avec succès.')
            return redirect('contact:contact')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')

    return render(request, 'pages/contact/index.html')


def professional_request_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        professional_type = request.POST.get('professional_type')
        description = request.POST.get('description')

        if name and email and professional_type and description:
            ProfessionalRequest.objects.create(
                name=name,
                email=email,
                phone=phone,
                professional_type=professional_type,
                description=description
            )
            messages.success(request, 'Votre demande a été enregistrée.')
            return redirect('core:public_service')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return redirect('core:public_service')

    return redirect('core:public_service')