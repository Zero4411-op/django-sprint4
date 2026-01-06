from django.contrib import admin

from .models import Category, Location, Post


class PublishedAdmin(admin.ModelAdmin):
    list_editable = ('is_published',)
    list_filter = ('is_published',)


class CategoryAdmin(PublishedAdmin):
    list_display = ('title', 'is_published', 'created_at')
    search_fields = ('title',)


class LocationAdmin(PublishedAdmin):
    list_display = ('name', 'is_published', 'created_at')
    search_fields = ('name',)


class PostAdmin(PublishedAdmin):
    list_display = ('title', 'pub_date', 'author', 'category', 'is_published')
    search_fields = ('title', 'text')
    list_filter = ('category', 'is_published', 'pub_date')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
