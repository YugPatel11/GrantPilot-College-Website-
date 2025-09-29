from django.contrib import admin
from .models import Profile, Project, ProjectApplication, IPRApplication, PersonDetails

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(ProjectApplication)
admin.site.register(IPRApplication)
admin.site.register(PersonDetails)
