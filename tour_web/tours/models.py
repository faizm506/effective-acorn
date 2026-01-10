from django.db import models

class Destination(models.Model):
    name = models.CharField(max_length=100)
    # e.g., "Manali", "Kerala"
    
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
    """Replaces the Booking model"""
    tour = models.ForeignKey(TourPackage, on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    travel_date = models.DateField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Status for Admin to track leads
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('booked', 'Booked (Offline)'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Inquiry from {self.customer_name} for {self.tour.title}"