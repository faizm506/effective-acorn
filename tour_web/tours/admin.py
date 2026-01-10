from django.contrib import admin
from .models import Destination, TourPackage, TourImage, Itinerary, Inquiry

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1

class ItineraryInline(admin.TabularInline):
    model = Itinerary
    extra = 1

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    inlines = [TourImageInline, ItineraryInline]
    list_display = ('title', 'destination', 'price', 'days', 'nights', 'is_featured')
    list_filter = ('destination', 'days', 'price')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'tour', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',) # Allows quick status updates

admin.site.register(Destination)