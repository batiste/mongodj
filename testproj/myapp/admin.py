from testproj.myapp.models import Entry
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'afile', 'has_file_content')

admin.site.register(Entry, EntryAdmin)