from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ensembl_dbcopy.models import Host, RequestJob, Group
from ensembl_production.admin import SuperUserAdmin
from django.contrib.auth.models import Group as UsersGroup

@receiver(post_save, sender=UsersGroup)
def sync_groups(sender, instance, **kwargs):
    user_groups = [ obj.name for obj in UsersGroup.objects.all() ]
    host_groups = [ obj.group_name for obj in Group.objects.all() ]
    new_usergroup = list(set(user_groups) - set(host_groups))
    for each_group in new_usergroup:
        g1 = Group(group_name=each_group)
        g1.save()

@receiver(post_delete, sender=UsersGroup)
def delete_group(sender, instance, **kwargs):
    user_groups = [ obj.name for obj in UsersGroup.objects.all() ]
    host_groups = [ obj.group_name for obj in Group.objects.all() ]
    new_usergroup = list( set(host_groups) - set(user_groups) )
    for each_group in new_usergroup:
        Group.objects.filter(group_name=each_group).delete()
