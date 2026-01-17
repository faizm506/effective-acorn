from django.contrib import admin
from .models import Destination, GalleryImage, TourPackage, TourImage, Itinerary, Inquiry, TourDate 
from .models import Review

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1

class ItineraryInline(admin.TabularInline):
    model = Itinerary
    extra = 1
    
# Add this new Inline
class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1


@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    inlines = [TourImageInline, ItineraryInline, TourDateInline]
    list_display = ('title', 'destination', 'price', 'days', 'nights', 'is_featured')
    list_filter = ('destination', 'days', 'price')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'tour', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',) # Allows quick status updates

admin.site.register(Destination)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'uploaded_at', 'image_preview')
    
    # Optional: Shows a small preview in the admin list
    def image_preview(self, obj):
        from django.utils.html import mark_safe
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="height: 50px; border-radius: 5px;" />')
        return "-"
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'rating', 'is_active', 'created_at')
    list_filter = ('is_active', 'rating')
    list_editable = ('is_active', 'rating') # Edit directly in the list view