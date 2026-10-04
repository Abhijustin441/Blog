from django.contrib import admin
from .models import Author,Post,Comment



# Register your models here.
class commentInline(admin.TabularInline):
    model=Comment
    extra=0
    readonly_fields=('author','description','created_at')

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'bio')
    search_fields = ('first_name', 'last_name')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('author', 'created_at')
    inlines=[commentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'description', 'created_at')
    search_fields = ('description',)
    list_filter = ('author', 'created_at')
