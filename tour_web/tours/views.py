from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from httpx import request
from .models import GalleryImage, TourPackage, Destination
from .forms import InquiryForm
from django.contrib import messages
from django.utils import timezone
from .models import Review



def home(request):
    # 1. Fetch ALL destinations for the Search Bar dropdown
    all_destinations = Destination.objects.all()

    # 2. Create the "Top 5" list for the Inspiration section
    top_destinations = all_destinations[:5]

    # 3. Fetch Featured Tours
    # Note: Use 'Tour' or 'TourPackage' depending on what your model is actually named in models.py
    featured_tours = TourPackage.objects.filter(is_featured=True)[:3] 

    reviews = Review.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    # 4. Pass everything to the template
    return render(request, 'tours/home.html', {
        'destinations': all_destinations,      # Used in the Search Bar
        'top_destinations': top_destinations,  # Used in "Explore by Destination"
        'featured_tours': featured_tours, 
        'reviews': reviews,  # Used in "Featured Packages"
    })

def gallery(request):
    # FETCH ALL FROM NEW GALLERY MODEL
    all_images = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'tours/gallery.html', {'images': all_images})
def destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'tours/destination_list.html', {'destinations': destinations})


def tour_list(request):
    tours = TourPackage.objects.all()
    
    # Filter Logic
    destination_id = request.GET.get('destination')
    max_price = request.GET.get('max_price')
    
    if destination_id:
        tours = tours.filter(destination_id=destination_id)
    if max_price:
        tours = tours.filter(price__lte=max_price)
        
    destinations = Destination.objects.all()
    
    return render(request, 'tours/tour_list.html', {
        'tours': tours,
        'destinations': destinations
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone # Import timezone to handle dates
from .models import TourPackage, TourDate
from .forms import InquiryForm

def tour_detail(request, pk):
    tour = get_object_or_404(TourPackage, pk=pk)
    
    # FIX: Get available dates for this tour that are >= Today
    # We order them by date so the dropdown looks organized
    available_dates = TourDate.objects.filter(
        tour=tour, 
        start_date__gte=timezone.now().date()
    ).order_by('start_date')
    
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.tour = tour
            inquiry.save()
            messages.success(request, "Your inquiry has been sent! We will call you shortly.")
            return redirect('tour_detail', pk=pk)
        else:
            # If form is invalid, print errors to console for debugging
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = InquiryForm()

    return render(request, 'tours/tour_detail.html', {
        'tour': tour,
        'form': form,
        'available_dates': available_dates, # Passing the filtered dates here
    })


# 1. Define the "Bouncer" function
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages # Import messages for feedback
from .models import Inquiry

def is_superuser_check(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser_check, login_url='/admin/login/')
def admin_dashboard(request):
    # Security check (Preserved)
    if not request.user.is_superuser:
        return redirect('home') 

    # 1. SPLIT QUERIES (Updated)
    # We separate Bookings (Tour attached) from General Messages (No tour)
    booking_list = Inquiry.objects.filter(tour__isnull=False).order_by('-created_at')
    message_list = Inquiry.objects.filter(tour__isnull=True).order_by('-created_at')

    unread_general_count = message_list.filter(status='pending').count()
    
    # 2. STATUS COUNTS (Preserved logic, calculated on ALL inquiries)
    all_inquiries = Inquiry.objects.all()
    total_inquiries = all_inquiries.count()
    pending_leads = all_inquiries.filter(status='pending').count()
    booked_leads = all_inquiries.filter(status='booked').count()

    # 3. ROWS PER PAGE (Preserved)
    per_page = request.GET.get('per_page', 50) 
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 50 

    # 4. PAGINATION (Applied to Booking List)
    # We paginate the main booking list as it grows fastest
    paginator = Paginator(booking_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 5. HANDLE STATUS UPDATE (Preserved Functionality)
    if request.method == "POST":
        inquiry_id = request.POST.get('inquiry_id')
        new_status = request.POST.get('new_status')
        
        inquiry = get_object_or_404(Inquiry, pk=inquiry_id)
        inquiry.status = new_status
        inquiry.save()
        
        # Add success message for better UX
        messages.success(request, f"Status updated for {inquiry.customer_name}")
        
        # Stay on the same page after update
        return redirect(f"{request.path}?page={page_obj.number}&per_page={per_page}")

    # 6. RENDER
    return render(request, 'tours/admin_dashboard.html', {
        'page_obj': page_obj,           # For the 'Tour Bookings' tab
        'general_messages': message_list, # For the 'General Inbox' tab
        'unread_general_count': unread_general_count,
        'total_inquiries': total_inquiries,
        'pending_leads': pending_leads,
        'booked_leads': booked_leads,
        'per_page': per_page, 
    })

def about(request):
    reviews = Review.objects.filter(is_active=True).order_by('-created_at')[:4]

    if request.method == 'POST':
        # --- Form Processing Logic ---
        name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone') 
        subject = request.POST.get('subject')
        raw_message = request.POST.get('message')

        # Format message
        full_message = f"Subject: {subject}\n\n{raw_message}"

        # Save to Database
        Inquiry.objects.create(
            customer_name=name,
            email=email,
            phone=phone,
            message=full_message,
            travel_date=timezone.now().date(),
            tour=None, 
            status='pending'
        )

        # Success feedback
        messages.success(request, "Message sent successfully! We will contact you shortly.")
        return redirect('about')

    # 2. Render Template with Data
    # IMPORTANT: We pass {'reviews': reviews} so the HTML can display them
    return render(request, 'tours/about_contact.html', {'reviews': reviews})

import openpyxl
from datetime import datetime
from django.http import HttpResponse
from .models import Inquiry # Ensure this matches your Model name

def download_monthly_report(request):
    # 1. Create the HttpResponse with Excel header
    current_date = datetime.now()
    filename = f"Inquiry_Report_{current_date.strftime('%B_%Y')}.xlsx"
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'

    # 2. Create the Workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Monthly Inquiries"

    # 3. Define the Header Row
    headers = ['Date Received', 'Customer Name', 'Phone', 'Email', 'Tour Package', 'Travel Date', 'Status']
    ws.append(headers)

    # 4. Make Headers Bold
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    # 5. Query Data (Filter for Current Month & Year)
    # Note: Adjust 'created_at' to match your actual date field name in models
    inquiries = Inquiry.objects.filter(
        created_at__month=current_date.month, 
        created_at__year=current_date.year
    ).order_by('-created_at')

    # 6. Write Data Rows
    for item in inquiries:
        # Handle cases where tour might be None (General Inquiry)
        tour_name = item.tour.title if item.tour else "General Inquiry"
        
        # Format dates as strings to prevent Excel errors
        created_date = item.created_at.strftime('%Y-%m-%d')
        travel_date = item.travel_date.strftime('%Y-%m-%d') if item.travel_date else "N/A"

        ws.append([
            created_date,
            item.customer_name,
            item.phone,
            item.email,
            tour_name,
            travel_date,
            item.get_status_display() # Gets the readable label (e.g., "Pending")
        ])

    # 7. Save to response
    wb.save(response)
    return response


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .forms import (
    DestinationForm, TourPackageForm, TourDateForm, 
    TourImageForm, ItineraryForm, GalleryImageForm, ReviewForm
)

@user_passes_test(lambda u: u.is_superuser, login_url='/admin/login/')
def data_management_dashboard(request):
    # Initialize all forms
    forms = {
        'dest_form': DestinationForm(),
        'tour_form': TourPackageForm(),
        'date_form': TourDateForm(),
        'img_form': TourImageForm(),
        'itinerary_form': ItineraryForm(),
        'gallery_form': GalleryImageForm(),
        'review_form': ReviewForm(),
    }

    if request.method == 'POST':
        # Determine which form was submitted using a hidden input 'form_type'
        form_type = request.POST.get('form_type')
        
        if form_type == 'destination':
            form = DestinationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Destination Added Successfully! 🌍")
                return redirect('data_dashboard')
        
        elif form_type == 'tour':
            form = TourPackageForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Tour Package Created! ✈️")
                return redirect('data_dashboard')

        elif form_type == 'date':
            form = TourDateForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Tour Date Added! 📅")
                return redirect('data_dashboard')

        elif form_type == 'image':
            form = TourImageForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Tour Image Uploaded! 📸")
                return redirect('data_dashboard')

        elif form_type == 'itinerary':
            form = ItineraryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Itinerary Day Added! 📝")
                return redirect('data_dashboard')

        elif form_type == 'gallery':
            form = GalleryImageForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Public Gallery Image Added! 🎨")
                return redirect('data_dashboard')

        elif form_type == 'review':
            form = ReviewForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Review Added! ⭐")
                return redirect('data_dashboard')
        
        # If we fall through, something failed validation
        messages.error(request, "Error adding data. Please check the form.")

    return render(request, 'tours/data_dashboard.html', forms)