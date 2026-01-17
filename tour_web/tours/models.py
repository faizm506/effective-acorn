from django.db import models

from django.db import models

class Destination(models.Model):
    name = models.CharField(max_length=100)
    # Add this line below:
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)

    def __str__(self):
        return self.name

class TourPackage(models.Model):
    title = models.CharField(max_length=200) # e.g., "Manali Adventure"
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    days = models.IntegerField()
    nights = models.IntegerField()
    description = models.TextField()
    main_image = models.ImageField(upload_to='tours/main/')
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    

class TourDate(models.Model):
    """Specific dates when this tour is available"""
    tour = models.ForeignKey(TourPackage, related_name='available_dates', on_delete=models.CASCADE)
    start_date = models.DateField()
    
    def __str__(self):
        return self.start_date.strftime("%d %B, %Y") # e.g., "15 January, 2026"
    
    
class TourImage(models.Model):
    """Allows multiple images for a single tour"""
    tour = models.ForeignKey(TourPackage, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tours/gallery/')

class Itinerary(models.Model):
    """Day-wise breakdown"""
    tour = models.ForeignKey(TourPackage, related_name='itineraries', on_delete=models.CASCADE)
    day_number = models.IntegerField()
    title = models.CharField(max_length=200) # e.g., "Day 1: Arrival and Sightseeing"
    activity_description = models.TextField()

    class Meta:
        ordering = ['day_number']

class Inquiry(models.Model):
    tour = models.ForeignKey(TourPackage, on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # We keep this as DateField, but on the frontend, it will be a Dropdown selection
    travel_date = models.DateField() 
    
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('booked', 'Booked (Offline)'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Inquiry from {self.customer_name}"
    

class GalleryImage(models.Model):
    """
    Independent images for the public Gallery Page.
    These are NOT tied to a specific Tour Package.
    """
    caption = models.CharField(max_length=100, blank=True, help_text="Short title like 'Sunset in Bali'")
    image = models.ImageField(upload_to='gallery/public/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Public Gallery Image"
        verbose_name_plural = "Public Gallery Images"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.caption or f"Gallery Image {self.id}"
    

class Review(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_title = models.CharField(max_length=100, blank=True, help_text="e.g. Traveler from USA")
    photo = models.ImageField(upload_to='reviews/', blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    is_active = models.BooleanField(default=True) # Admin can hide reviews without deleting
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} ({self.rating} Stars)"