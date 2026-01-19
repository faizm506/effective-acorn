from django import forms
from .models import Inquiry
import datetime

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['customer_name', 'email', 'phone', 'travel_date', 'message']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special requests?'}),
        }





from django import forms
from .models import Destination, TourPackage, TourDate, TourImage, Itinerary, Inquiry, GalleryImage, Review

# Base styling for all inputs
class BaseStyleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-lg bg-light border-0'
            field.widget.attrs['placeholder'] = field.label

class DestinationForm(BaseStyleForm):
    class Meta:
        model = Destination
        fields = '__all__'

class TourPackageForm(BaseStyleForm):
    class Meta:
        model = TourPackage
        fields = '__all__'

class TourDateForm(BaseStyleForm):
    class Meta:
        model = TourDate
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TourImageForm(BaseStyleForm):
    class Meta:
        model = TourImage
        fields = '__all__'

class ItineraryForm(BaseStyleForm):
    class Meta:
        model = Itinerary
        fields = '__all__'
        widgets = {
            'activity_description': forms.Textarea(attrs={'rows': 3}),
        }
class GalleryImageForm(BaseStyleForm):
    class Meta:
        model = GalleryImage
        fields = '__all__'
        # This helps the browser filter files when selecting
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
            'video': forms.FileInput(attrs={'accept': 'video/*'}), 
        }


class ReviewForm(BaseStyleForm):
    class Meta:
        model = Review
        fields = '__all__'
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }