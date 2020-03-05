"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, ListView
from ensembl_dbcopy.forms import SubmitForm
from ensembl_dbcopy.models import RequestJob
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import F


class SubmitView(CreateView):
    template_name = "submit.html"
    form_class = SubmitForm

    def get_success_url(self):
        return reverse('ensembl_dbcopy:detail', kwargs={'job_id': self.object.job_id})

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


class JobView(DetailView):
    model = RequestJob
    template_name = 'detail.html'
    pk_url_kwarg = 'job_id'
    queryset = RequestJob.objects.all().prefetch_related('transfer_logs')

    def get_context_data(self, **kwargs):
        context = super(JobView, self).get_context_data(**kwargs)
        paginator = Paginator(context['requestjob'].transfer_logs.order_by(F('end_date').desc(nulls_first=True)), 30)
        page_number = self.request.GET.get('page', 1)
        page = paginator.page(page_number)
        context['transfer_logs'] = page
        return context


class JobListView(ListView):
    model = RequestJob
    paginate_by = 10
    template_name = 'list.html'
    def get_queryset(self):
        return RequestJob.objects.order_by(F('start_date').desc(nulls_first=True))
