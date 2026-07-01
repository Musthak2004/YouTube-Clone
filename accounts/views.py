from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .forms import CustomUserCreationForm, CustomUserChangeForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/settings.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['profile_form'] = CustomUserChangeForm(
                self.request.POST, self.request.FILES,
                instance=self.request.user
            )
            ctx['password_form'] = PasswordChangeView.form_class(
                self.request.user, self.request.POST
            )
        else:
            ctx['profile_form'] = CustomUserChangeForm(instance=self.request.user)
            ctx['password_form'] = PasswordChangeView.form_class(self.request.user)
        return ctx

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        profile_form = context['profile_form']
        password_form = context['password_form']

        profile_ok = profile_form.is_valid()
        password_ok = password_form.is_valid()

        if profile_ok:
            profile_form.save()

        if password_ok:
            password_form.save()

        if profile_ok or password_ok:
            from django.contrib import messages
            messages.success(request, 'Settings saved successfully.')

        if password_ok:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

        if password_ok and not profile_ok:
            # Only password changed — redirect to the login-required
            # page so the user stays on settings.
            return self.render_to_response(context)

        return self.render_to_response(context)
