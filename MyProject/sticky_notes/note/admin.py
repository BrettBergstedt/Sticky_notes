from django.contrib import admin

# Register your models here.
from .models import Note
from .models import Author

# Customise the default admin site (the one urls.py actually serves)
admin.site.site_title = "Sticky Notes"
admin.site.site_header = "Sticky Notes Administration"
admin.site.index_title = "Dashboard"

# Note model
admin.site.register(Note)
# Author model
admin.site.register(Author)
