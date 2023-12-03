from django.contrib import admin

from movie_app.models import Collection, Movie

# Register your models here.


admin.site.register(Movie)
admin.site.register(Collection)