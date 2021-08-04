from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from .models import Comment, Follow, Group, Post

ModelAdmin.empty_value_display = '-пусто-'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('description',)
    list_filter = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'author', 'text', 'created')
    search_fields = ('text',)
    list_filter = ('created',)


@admin.register(Follow)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
