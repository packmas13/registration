from django.contrib import admin

from .models import Attendance, Diet, Participant, Troop

from payment.admin import DiscountInline, PaymentInline


class AttendanceInline(admin.TabularInline):
    model = Participant.attendance.through
    readonly_fields = ('participant', )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class AttendanceAdmin(admin.ModelAdmin):
    inlines = [AttendanceInline, ]


class DietInline(admin.TabularInline):
    model = Participant.diet.through
    readonly_fields = ('participant', )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class DietAdmin(admin.ModelAdmin):
    inlines = [DietInline, ]


class ParticipantAdmin(admin.ModelAdmin):
    inlines = [DiscountInline, ]
    list_display = ('troop', 'firstname', 'lastname', 'birthday', 'age_section', 'is_leader', )
    list_display_links = ('firstname', 'lastname', 'birthday', )


class ParticipantInline(admin.TabularInline):
    model = Participant
    fields = ('firstname', 'lastname', 'birthday', )
    readonly_fields = ('firstname', 'lastname', 'birthday', )
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class TroopAdmin(admin.ModelAdmin):
    inlines = [ParticipantInline, PaymentInline, ]
    list_display = ('number', 'name', )
    list_display_links = ('name', )


admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Diet, DietAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Troop, TroopAdmin)
