from django.contrib import admin
from .models import Categories, Genres, Titles, Review, Comments


class CategoriesAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-empty-'


class GenresAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-empty-'


class TitlesAdmin(admin.ModelAdmin):

    list_display = ('name', 'year', 'category', 'description', 'rating')
    search_fields = ('name',)
    list_filter = ('year',)
    empty_value_display = '-пусто-'


class ReviewAdmin(admin.ModelAdmin):

    list_display = ('title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('title',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentsAdmin(admin.ModelAdmin):

    list_display = ('review', 'text', 'author', 'pub_date')
    search_fields = ('review',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Genres, GenresAdmin)
admin.site.register(Titles, TitlesAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comments, CommentsAdmin)
