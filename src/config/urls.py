# src/config/urls.py
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('apps.core.urls')),
    path('actualites/', include('apps.news.urls')),
    path('contact/', include('apps.contact.urls')),
    path('membres/', include('apps.members.urls')),

    # Réinitialisation de mot de passe (vues Django built-in)
    path('membres/password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='members/password_reset.html',
             email_template_name='members/emails/password_reset_email.txt',
             subject_template_name='members/emails/password_reset_subject.txt',
         ),
         name='password_reset'),
    path('membres/password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='members/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('membres/password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='members/password_reset_confirm.html',
         ),
         name='password_reset_confirm'),
    path('membres/password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='members/password_reset_complete.html',
         ),
         name='password_reset_complete'),
]

# Toujours servir les médias (runserver sans Nginx dédié).
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

admin.site.site_header = "Administration CNIAH"
admin.site.site_title = "CNIAH Admin"
admin.site.index_title = "Gestion du contenu"