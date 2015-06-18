import models
import forms
import tables
import field_filters
import constants

from datetime import datetime, timedelta

from django.views.generic import DetailView, FormView
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from comments.views import CommentViewGeneric
from source.models import Source
from core.generic_views import (ObjectMixinFixed, LoginMixin, EditView,
                                HistoryView, FilteredListView)


class ContractView(LoginMixin):
    view_name = 'contracts'
    model = models.Contract


class Detail(ContractView, DetailView, CommentViewGeneric):
    template_name = 'contract.html'


class Create(LoginMixin, FormView, ObjectMixinFixed):
    form_class = forms.CreateForm
    template_name = 'add_form.html'
    title = _('Add contract')
    view_name = 'contracts'
    model = Source

    def form_valid(self, form):
        contract = form.save(commit=False)
        contract.source = self.object
        contract.save()
        return HttpResponseRedirect(contract.get_absolute_url())


class Edit(ContractView, EditView):
    form_class = forms.EditForm

    def form_valid(self, form):
        if (self.get_object().state == constants.CONTRACT_STATE_NEGOTIATION and
                form.cleaned_data['state'] == constants.CONTRACT_STATE_VALID):
            contract = form.save(commit=False)
            contract.contract_number = models.Contract.new_contract_number()
            contract.save()
            self.add_message(_('Contract number assigned.'), messages.SUCCESS)
            self.add_message(_('Changes saved.'), messages.SUCCESS)
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        else:
            return super(Edit, self).form_valid(form)


class History(ContractView, HistoryView):
    """
        History of changes to contracts
    """


class ListView(ContractView, FilteredListView):
    title = _('Contracts')
    table_class = tables.ContractTable
    filter_class = field_filters.ContractFilter


class Schedule(ContractView, FormView, ObjectMixinFixed):
    template_name = 'schedule.html'
    title = _('Schedule emails')

    def get_context_data(self, **kwargs):
        context = super(Schedule, self).get_context_data(**kwargs)
        context['source'] = self.object.source
        return context

    def get_form_class(self):
        queryset = self.object.emailnegotiation_set.all()
        extra = 0 if queryset else len(constants.NEGOTIATION_TEMPLATES)
        return modelformset_factory(
            models.EmailNegotiation,
            fields=('scheduled_date', 'title', 'content'),
            extra=extra, can_delete=True)

    def get_initial(self):
        initial = []
        delay = 0
        for template in constants.NEGOTIATION_TEMPLATES:
            rendered = render_to_string(template, context={
                'user': self.request.user
            })
            date = datetime.now() + timedelta(days=delay)
            delay += constants.NEGOTIATION_DELAY
            initial.append({
                'content': rendered,
                'scheduled_date': date,
            })
        return initial

    def form_valid(self, form):
        for email in form.save(commit=False):
            email.contract = self.object
            email.save()

        for obj in form.deleted_objects:
            obj.delete()

        return HttpResponseRedirect(self.object.get_absolute_url())
