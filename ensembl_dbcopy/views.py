from django.views.generic.edit import CreateView
from django.views.generic import DetailView,ListView
from ensembl_dbcopy.forms import SubmitForm
from ensembl_dbcopy.models import RequestJob
from django.urls import reverse

class SubmitView(CreateView):
    template_name = "submit.html"
    form_class = SubmitForm
    def get_success_url(self):
      return reverse('detail',kwargs={'job_id': self.object.job_id})
    def get_form_kwargs(self, *args, **kwargs):
      kwargs = super().get_form_kwargs(*args, **kwargs)
      kwargs['user'] = self.request.user
      return kwargs

class JobView(DetailView):
    model = RequestJob
    template_name = 'detail.html'
    queryset = RequestJob.objects.all()
    pk_url_kwarg = 'job_id'

class JobListView(ListView):
    model = RequestJob
    paginate_by = 10
    template_name = 'list.html'