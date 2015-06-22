import forms

from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView, View
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.utils.http import is_safe_url
from django.utils import translation

from generic_views import LoginMixin, MessageView
from dashboard_data import get_cards

from source import export
from source.models import SeedExport
from source import constants as source_constants


class DashboardView(LoginMixin, TemplateView):
    template_name = 'dashboard.html'
    title = _('Dashboard')
    view_name = 'dashboard'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data()
        context['cards'] = get_cards(self.request.user)
        return context


class ChangeLanguage(View):
    def get(self, request, code):
        print translation.get_language()

        redirect = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=redirect, host=request.get_host()):
            redirect = '/'
        if translation.check_for_language(code):
            request.session[translation.LANGUAGE_SESSION_KEY] = code
        return HttpResponseRedirect(redirect)


class UserProfileEdit(UpdateView, MessageView):
    form_class = forms.UserForm
    view_name = 'user_edit'
    template_name = 'user_edit.html'
    title = _('Change user information')
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        self.add_message(_('Profile changed.'), messages.SUCCESS)
        return HttpResponseRedirect('/')


class ApiPage(TemplateView):
    template_name = 'api.html'
    title = _('Api description')
    view_name = 'api'
    
    def get_context_data(self, **kwargs):
        context = super(ApiPage, self).get_context_data(**kwargs)
        latest_exports = []
        for freq in dict(source_constants.SOURCE_FREQUENCY_PER_YEAR):
            first = SeedExport.objects.filter(
                frequency=freq).order_by('-created').first()
            latest_exports.append(first)

        context['latest_exports'] = latest_exports
        return context

    def post(self, request):
        export.export_seeds()
        return HttpResponseRedirect('')


class PasswordChangeDone(MessageView, View):
    """
        Redirect page that adds success message
    """
    def get(self, request):
        self.add_message(_('Password changed successfully.'), messages.SUCCESS)
        return HttpResponseRedirect('/')
