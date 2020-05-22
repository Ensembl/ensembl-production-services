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
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from ensembl_dbcopy.models import RequestJob, Group, Host


def reset_failed_jobs(request, *args, **kwargs):
    job_id = kwargs['job_id']
    request_job = RequestJob.objects.filter(job_id=job_id)
    request_job.update(end_date=None)
    request_job.update(status=None)
    obj = request_job[0]
    url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name),
                  args=[obj.job_id])
    messages.success(request, "All the failed jobs for %s have been successfully reset" % job_id)
    return redirect(url)

def group_choice(request, *args, **kwargs):

    host_id = request.POST.get("host_id")
    host_id = Host.objects.get(auto_id=host_id)
    for each_group in request.POST.getlist('group_name'):
        grp = Group.objects.filter(group_name=[str(each_group)], host_id=request.POST.get("host_id"))
        if len(grp) > 0 :
            continue
        new_group = Group()
        new_group.group_name = each_group
        new_group.host_id = host_id #Host.objects.get(auto_id=host_id)
        new_group.save()

    url = reverse('admin:ensembl_dbcopy_group_changelist')
    return redirect(url)

