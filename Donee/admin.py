from django.contrib import admin


class DoneeAdmin(admin.ModelAdmin):
    readonly_fields = [
        'created_by', 'modified_by', 'modified_at'
    ]