from django.shortcuts import render, get_object_or_404, redirect
from .models import TourPackage, Destination
from .forms import InquiryForm
from django.contrib import messages

def home(request):
    # Featured tours for the homepage
    featured_tours = TourPackage.objects.filter(is_featured=True)[:6]
    destinations = Destination.objects.all()
    return render(request, 'tours/home.html', {
        'featured_tours': featured_tours,
        'destinations': destinations
    })

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

def tour_detail(request, pk):
    tour = get_object_or_404(TourPackage, pk=pk)
    
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.tour = tour
            inquiry.save()
            messages.success(request, "Your inquiry has been sent! We will call you shortly.")
            return redirect('tour_detail', pk=pk)
    else:
        form = InquiryForm()

    return render(request, 'tours/tour_detail.html', {
        'tour': tour,
        'form': form
    })

from django.contrib.auth.decorators import user_passes_test
from .models import Inquiry

# 1. Define the check: Is the user a superuser (Admin)?
def is_admin(user):
    return user.is_superuser

# 2. Apply the security check to the view
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get all inquiries, newest first
    inquiries = Inquiry.objects.all().order_by('-created_at')
    
    # Calculate simple stats
    total_inquiries = inquiries.count()
    pending_leads = inquiries.filter(status='pending').count()
    booked_leads = inquiries.filter(status='booked').count()

    # Handle Status Updates directly from the dashboard
    if request.method == "POST":
        inquiry_id = request.POST.get('inquiry_id')
        new_status = request.POST.get('new_status')
        
        inquiry = get_object_or_404(Inquiry, pk=inquiry_id)
        inquiry.status = new_status
        inquiry.save()
        messages.success(request, f"Status updated for {inquiry.customer_name}")
        return redirect('admin_dashboard')

    return render(request, 'tours/admin_dashboard.html', {
        'inquiries': inquiries,
        'total_inquiries': total_inquiries,
        'pending_leads': pending_leads,
        'booked_leads': booked_leads
    })