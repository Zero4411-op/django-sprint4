from django.contrib import admin

from .models import Category, Location, Post


class PublishedAdmin(admin.ModelAdmin):
    list_editable = ('is_published',)
    list_filter = ('is_published',)


@admin.register(Category)
class CategoryAdmin(PublishedAdmin):
    list_display = ('title', 'is_published', 'created_at')
    search_fields = ('title',)


@admin.register(Location)
class LocationAdmin(PublishedAdmin):
    list_display = ('name', 'is_published', 'created_at')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(PublishedAdmin):
    list_display = ('title', 'pub_date', 'author', 'category', 'is_published')
    search_fields = ('title', 'text')
    list_filter = ('category', 'is_published', 'pub_date')
