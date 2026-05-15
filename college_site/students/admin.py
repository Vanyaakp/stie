from django.contrib import admin
from .models import Student, Group, Club

admin.site.register(Group)
admin.site.register(Club)
admin.site.register(Student)