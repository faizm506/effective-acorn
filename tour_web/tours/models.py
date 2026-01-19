from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

# --- HELPER FUNCTION TO AUTO-RESIZE IMAGES ---
def resize_and_compress_image(image_field, target_width, target_height):
    """
    Resizes an image to fit within target dimensions while maintaining aspect ratio,
    and compresses it to JPEG to save space.
    """
    if not image_field:
        return None

    # 1. Open the image
    img = Image.open(image_field)
    
    # 2. Convert to RGB (Required for JPEG saving if original is PNG/RGBA)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # 3. Resize Logic (Thumbnail keeps aspect ratio, doesn't stretch)
    # This ensures the image fits within the box but doesn't distort
    img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

    # 4. Save to memory buffer
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85) # Quality 85 is the sweet spot
    
    # 5. Return the new file
    new_image = ContentFile(buffer.getvalue())
    return new_image

# ---------------- MODELS ----------------

class Destination(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Resize Destination images to max 800x600
        if self.image:
            self.image.save(self.image.name, resize_and_compress_image(self.image, 800, 600), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class TourPackage(models.Model):
    title = models.CharField(max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    days = models.IntegerField()
    nights = models.IntegerField()
    description = models.TextField()
    main_image = models.ImageField(upload_to='tours/main/')
    is_featured = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Resize Main Tour Banner to max 1200x800 (High Quality)
        if self.main_image:
            self.main_image.save(self.main_image.name, resize_and_compress_image(self.main_image, 1200, 800), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class TourDate(models.Model):
    """Specific dates when this tour is available"""
    tour = models.ForeignKey(TourPackage, related_name='available_dates', on_delete=models.CASCADE)
    start_date = models.DateField()
    
    def __str__(self):
        return self.start_date.strftime("%d %B, %Y")
    
    
class TourImage(models.Model):
    """Allows multiple images for a single tour"""
    tour = models.ForeignKey(TourPackage, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tours/gallery/')

    def save(self, *args, **kwargs):
        # Resize Gallery images to max 1024x768
        if self.image:
            self.image.save(self.image.name, resize_and_compress_image(self.image, 1024, 768), save=False)
        super().save(*args, **kwargs)

class Itinerary(models.Model):
    """Day-wise breakdown"""
    tour = models.ForeignKey(TourPackage, related_name='itineraries', on_delete=models.CASCADE)
    day_number = models.IntegerField()
    title = models.CharField(max_length=200)
    activity_description = models.TextField()

    class Meta:
        ordering = ['day_number']

class Inquiry(models.Model):
    tour = models.ForeignKey(TourPackage, on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
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
    """
    caption = models.CharField(max_length=100, blank=True, help_text="Short title like 'Sunset in Bali'")
    image = models.ImageField(upload_to='gallery/public/', blank=True, null=True, help_text="Upload an image file")
    video = models.FileField(upload_to='gallery/videos/', blank=True, null=True, help_text="Upload MP4, WebM, or OGG video files")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Public Gallery Image"
        verbose_name_plural = "Public Gallery Images"
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        # Resize Public Gallery images to max 1024x768
        if self.image:
            self.image.save(self.image.name, resize_and_compress_image(self.image, 1024, 768), save=False)
        super().save(*args, **kwargs)

    @property
    def is_video(self):
        """Helper to check if this item is a video in templates"""
        return bool(self.video)

    def __str__(self):
        return self.caption or f"Gallery Image {self.id}"
    

class Review(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_title = models.CharField(max_length=100, blank=True, help_text="e.g. Traveler from USA")
    photo = models.ImageField(upload_to='reviews/', blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Resize Review User Photos to max 300x300 (Small/Avatar size)
        if self.photo:
            self.photo.save(self.photo.name, resize_and_compress_image(self.photo, 300, 300), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_name} ({self.rating} Stars)"