# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import uuid

class Dbs2Exclude(models.Model):
    table_schema = models.CharField(db_column='TABLE_SCHEMA', max_length=64)  # Field name made lowercase.

    class Meta:
        db_table = 'dbs_2_exclude'


class DebugLog(models.Model):
    job_id = models.CharField(max_length=128, blank=True, null=True)
    sequence = models.IntegerField(blank=True, null=True)
    function = models.CharField(max_length=128, blank=True, null=True)
    value = models.TextField(max_length=8192, blank=True, null=True)

    class Meta:
        db_table = 'debug_log'


class RequestJob(models.Model):
    job_id = models.CharField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False)
    src_host = models.TextField(max_length=2048)
    src_incl_db = models.TextField(max_length=2048, blank=True, null=True)
    src_skip_db = models.TextField(max_length=2048, blank=True, null=True)
    src_incl_tables = models.TextField(max_length=2048, blank=True, null=True)
    src_skip_tables = models.TextField(max_length=2048, blank=True, null=True)
    tgt_host = models.TextField(max_length=2048)
    tgt_db_name = models.TextField(max_length=2048, blank=True, null=True)
    tgt_directory = models.TextField(max_length=2048, blank=True, null=True)
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

    def __str__(self):
        return str(self.job_id)

    @property
    def overall_status(self):
        if self.end_date:
            return 'complete'
        elif self.transfer_logs.count() > 0:
            return 'running'
        else:
            return 'submitted'

    @property
    def detailed_status(self):
        total_tables=self.transfer_logs.count()
        table_copied=self.table_copied
        progress=0
        if table_copied and total_tables:
            progress=(table_copied/total_tables)*100
        if progress == 100.0:
            return {'status_msg':'complete','table_copied':table_copied,'total_tables':total_tables,'progress':progress}
        elif total_tables > 0:
            return {'status_msg':'running','table_copied':table_copied,'total_tables':total_tables,'progress':progress}
        else:
            return {'status_msg':'submitted','table_copied':table_copied,'total_tables':total_tables,'progress':progress}

    @property
    def table_copied(self):
        nbr_tables=sum(map(lambda log: self.count_copied(log),self.transfer_logs.all()))
        return nbr_tables

    def count_copied(self,log):
        if log.end_date:
            return 1
        else:
            return 0


class TransferLog(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    job_id = models.ForeignKey(RequestJob, db_column='job_id', on_delete=models.CASCADE, related_name='transfer_logs')
    tgt_host = models.CharField(max_length=512, editable=False)
    table_schema = models.CharField(db_column='TABLE_SCHEMA', max_length=64, editable=False)  # Field name made lowercase.
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
            return 'complete'
        else:
            return 'running'

class Host(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64)
    port = models.IntegerField()
    mysql_user = models.CharField(max_length=64)
    virtual_machine = models.CharField(max_length=255,blank=True, null=True)
    mysqld_file_owner = models.CharField(max_length=128)

    class Meta:
        db_table = 'host'
        unique_together = (('name', 'port'),)
        app_label = 'ensembl_dbcopy'
        verbose_name = 'Host'

    def __str__(self):
        return '{}:{}'.format(self.name, self.port)
