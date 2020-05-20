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
import uuid

from django.db import models

from ensembl_production.models import NullTextField

NAME_CHOICES_GROUP = (('Vertebrates', 'Vertebrates'),
                      ('Microbes', 'Microbes'),
                      ('Metazoa', 'Metazoa'),
                      ('VectorBase', 'VectorBase'),
                      ('Plants', 'Plants'),
                      ('WormBase', 'WormBase'),
                      ('Compara', 'Compara'),
                      ('Production', 'Production'))


class Dbs2Exclude(models.Model):
    table_schema = models.CharField(db_column='TABLE_SCHEMA', max_length=64)  # Field name made lowercase.

    class Meta:
        db_table = 'dbs_2_exclude'
        app_label = 'ensembl_dbcopy'


class DebugLog(models.Model):
    job_id = models.CharField(max_length=128, blank=True, null=True)
    sequence = models.IntegerField(blank=True, null=True)
    function = models.CharField(max_length=128, blank=True, null=True)
    value = models.TextField(max_length=8192, blank=True, null=True)

    class Meta:
        db_table = 'debug_log'
        app_label = 'ensembl_dbcopy'


class RequestJob(models.Model):
    job_id = models.CharField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False)
    src_host = models.TextField(max_length=2048)
    src_incl_db = NullTextField(max_length=2048, blank=True, null=True)
    src_skip_db = NullTextField(max_length=2048, blank=True, null=True)
    src_incl_tables = NullTextField(max_length=2048, blank=True, null=True)
    src_skip_tables = NullTextField(max_length=2048, blank=True, null=True)
    tgt_host = models.TextField(max_length=2048)
    tgt_db_name = NullTextField(max_length=2048, blank=True, null=True)
    tgt_directory = NullTextField(max_length=2048, blank=True, null=True)
    skip_optimize = models.BooleanField(default=False)
    wipe_target = models.BooleanField(default=False)
    convert_innodb = models.BooleanField(default=False)
    email_list = models.TextField(max_length=2048, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True, editable=False)
    end_date = models.DateTimeField(blank=True, null=True, editable=False)
    user = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True, editable=False)

    class Meta:
        db_table = 'request_job'
        app_label = 'ensembl_dbcopy'
        verbose_name = "Copy job"
        verbose_name_plural = "Copy jobs"

    def __str__(self):
        return str(self.job_id)

    @property
    def overall_status(self):
        if self.end_date and self.status:
            if self.transfer_logs.filter(end_date__isnull=True).count() > 0:
                return 'Failed'
            else:
                return 'Complete'
        elif self.transfer_logs.count() > 0:
            return 'Running'
        else:
            return 'Submitted'

    @property
    def detailed_status(self):
        total_tables = self.transfer_logs.count()
        table_copied = self.table_copied
        progress = 0
        if table_copied and total_tables:
            progress = (table_copied / total_tables) * 100
        if progress == 100.0:
            return {'status_msg': 'Complete', 'table_copied': table_copied, 'total_tables': total_tables,
                    'progress': progress}
        elif total_tables > 0:
            if self.end_date and self.status:
                return {'status_msg': 'Failed', 'table_copied': table_copied, 'total_tables': total_tables,
                        'progress': progress}
            else:
                return {'status_msg': 'Running', 'table_copied': table_copied, 'total_tables': total_tables,
                        'progress': progress}
        else:
            return {'status_msg': 'Submitted', 'table_copied': table_copied, 'total_tables': total_tables,
                    'progress': progress}

    @property
    def table_copied(self):
        nbr_tables = sum(map(lambda log: self.count_copied(log), self.transfer_logs.all()))
        return nbr_tables

    def count_copied(self, log):
        if log.end_date:
            return 1
        else:
            return 0


class TransferLog(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    job_id = models.ForeignKey(RequestJob, db_column='job_id', on_delete=models.CASCADE, related_name='transfer_logs')
    tgt_host = models.CharField(max_length=512, editable=False)
    table_schema = models.CharField(db_column='TABLE_SCHEMA', max_length=64,
                                    editable=False)  # Field name made lowercase.
    table_name = models.CharField(db_column='TABLE_NAME', max_length=64, editable=False)  # Field name made lowercase.
    renamed_table_schema = models.CharField(max_length=64, editable=False)
    target_directory = models.TextField(max_length=2048, blank=True, null=True, editable=False)
    start_date = models.DateTimeField(blank=True, null=True, editable=False)
    end_date = models.DateTimeField(blank=True, null=True, editable=False)
    size = models.BigIntegerField(blank=True, null=True, editable=False)
    retries = models.IntegerField(blank=True, null=True, editable=False)
    message = models.CharField(max_length=255, blank=True, null=True, editable=False)

    class Meta:
        db_table = 'transfer_log'
        unique_together = (('job_id', 'tgt_host', 'table_schema', 'table_name'),)
        app_label = 'ensembl_dbcopy'
        verbose_name = 'TransferLog'

    @property
    def table_status(self):
        if self.end_date:
            return 'Complete'
        elif self.job_id.end_date and self.job_id.status:
            return 'Failed'
        else:
            return 'Running'


class Host(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64)
    port = models.IntegerField()
    mysql_user = models.CharField(max_length=64)
    virtual_machine = models.CharField(max_length=255, blank=True, null=True)
    mysqld_file_owner = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        db_table = 'host'
        unique_together = (('name', 'port'),)
        app_label = 'ensembl_dbcopy'
        verbose_name = 'Host'

    def __str__(self):
        return '{}:{}'.format(self.name, self.port)


class Group(models.Model):
    group_id = models.BigAutoField(primary_key=True)
    host_id = models.ForeignKey(Host, db_column='auto_id', on_delete=models.CASCADE)
    group_name = models.CharField(choices=NAME_CHOICES_GROUP, max_length=80, default='Vertebrates')

    class Meta:
        db_table = 'group'
        app_label = 'ensembl_dbcopy'
        verbose_name = 'Group'
