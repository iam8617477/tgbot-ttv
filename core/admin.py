from django.contrib import admin


class DefaultAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        opts = self.model._meta
        return [field.name for field in opts.get_fields() if not field.is_relation]
