from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AppRoleAssignment


class AppRoleAssignmentInline(admin.TabularInline):
    model = AppRoleAssignment
    extra = 1
    fields = ("app", "role", "team", "granted_at")
    readonly_fields = ("granted_at",)
    fk_name = "user"


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "display_name", "is_active", "is_staff", "must_change_password", "date_joined")
    list_filter = ("is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("last_name", "first_name")
    inlines = [AppRoleAssignmentInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Persönliche Daten",
            {"fields": ("first_name", "last_name", "microsoft_oid")},
        ),
        (
            "Berechtigungen",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "must_change_password",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datum", {"fields": ("date_joined", "last_login")}),
    )
    readonly_fields = ("date_joined", "last_login")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "must_change_password",
                ),
            },
        ),
    )

    @admin.display(description="Name")
    def display_name(self, obj):
        return obj.display_name


@admin.register(AppRoleAssignment)
class AppRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "app", "role", "granted_at")
    list_filter = ("app", "role")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    autocomplete_fields = ("user",)
    readonly_fields = ("granted_at",)
