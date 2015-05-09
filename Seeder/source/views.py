import forms
import models
import tables
import field_filters
import constants

from django.views.generic import DetailView
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django_tables2 import SingleTableView

from datetime import datetime
from core.utils import LoginMixin, MultipleFormView
from class_based_comments.views import CommentViewGeneric


class AddSource(LoginMixin, MultipleFormView):
    """
    Custom view for processing source form and seed formset
    """

    template_name = 'add_source.html'
    title = _('Add source')
    view_name = 'add_source'
    form_classes = {
        'source_form': forms.SourceForm,
        'seed_formset': forms.SeedFormset,
    }

    def dispatch(self, request, *args, **kwargs):
        # dynamically set source form according to user rights
        if self.request.user.has_perm('core.manage_sources'):
            self.form_classes['source_form'] = forms.ManagementSourceForm
        return super(AddSource, self).dispatch(request, *args, **kwargs)

    def forms_valid(self, form_instances):
        source_form = form_instances['source_form']
        seed_formset = form_instances['seed_formset']
        user = self.request.user
        is_manager = self.request.user.has_perm('core.manage_sources')

        source = source_form.save(commit=False)
        source.created_by = user
        if not is_manager or not source_form.cleaned_data.get('owner', None):
            source.owner = user

        new_publisher = source_form.cleaned_data.get('new_publisher', None)
        if new_publisher:
            new_publisher = models.Publisher(name=new_publisher)
            new_publisher.save()
            source.publisher = new_publisher
        source.save()

        if source_form.cleaned_data['open_license']:
            contract = models.Contract(
                source=source,
                date_start=datetime.now(),
                contract_type=constants.CONTRACT_CREATIVE_COMMONS
            )
            contract.save()

        for form in seed_formset.forms:
            seed = form.save(commit=False)
            if seed.url:  # prevent saving empty fields
                seed.source = source
                seed.save()

        return HttpResponseRedirect(source.get_absolute_url())


class SourceDetail(LoginMixin, DetailView, CommentViewGeneric):
    template_name = 'source.html'
    view_name = 'sources'
    context_object_name = 'source'
    model = models.Source
    anonymous = False
    threaded_comments = True


class SourceList(LoginMixin, SingleTableView):
    model = models.Source
    template_name = 'source_list.html'
    title = _('Sources')
    context_object_name = 'sources'
    view_name = 'sources'
    table_class = tables.SourceTable
    filter_class = field_filters.SourceFilter
    table_pagination = {"per_page": 20}

    def get_table_data(self):
        queryset = super(SourceList, self).get_table_data()
        return self.filter_class(self.request.GET, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super(SourceList, self).get_context_data(**kwargs)
        context['filter'] = self.filter_class(data=self.request.GET)
        return context