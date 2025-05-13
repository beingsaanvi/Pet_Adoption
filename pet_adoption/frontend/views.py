import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

API_BASE_URL = "http://localhost:5000"
ADMIN_API_KEY = "your-secret-key"  # Replace with the same key as in Flask app.py

def index(request):
    type_filter = request.GET.get('type', '')
    adopted_filter = request.GET.get('adopted', '')
    url = f"{API_BASE_URL}/pets"
    params = {}
    if type_filter:
        params['type'] = type_filter
    if adopted_filter:
        params['adopted'] = adopted_filter
    response = requests.get(url, params=params)
    pets = response.json() if response.status_code == 200 else []
    
    # Convert relative image URLs to absolute URLs
    for pet in pets:
        if pet.get('image_url') and not pet['image_url'].startswith(('http://', 'https://')):
            pet['image_url'] = f"{API_BASE_URL}{pet['image_url']}"
            
    return render(request, 'index.html', {'pets': pets, 'type_filter': type_filter, 'adopted_filter': adopted_filter})

def pet_detail(request, id):
    response = requests.get(f"{API_BASE_URL}/pets/{id}")
    pet = response.json() if response.status_code == 200 else None
    
    # If pet exists and has an image_url that's just a path, make it a full URL
    if pet and pet.get('image_url'):
        if not pet['image_url'].startswith(('http://', 'https://')):
            pet['image_url'] = f"{API_BASE_URL}{pet['image_url']}"
    
    return render(request, 'pet_detail.html', {'pet': pet})

@login_required
def adoption_request(request, id):
    if request.method == 'POST':
        data = {
            'user_name': request.POST['user_name'],
            'email': request.POST['email'],
            'phone': request.POST.get('phone', ''),
            'message': request.POST.get('message', ''),
            'pet_id': id
        }
        response = requests.post(f"{API_BASE_URL}/adoption-requests", json=data)
        if response.status_code == 201:
            messages.success(request, 'Adoption request submitted successfully!')
            return redirect('index')
        else:
            messages.error(request, 'Failed to submit adoption request.')
    
    response = requests.get(f"{API_BASE_URL}/pets/{id}")
    pet = response.json() if response.status_code == 200 else None
    
    # Convert relative image URL to absolute URL
    if pet and pet.get('image_url') and not pet['image_url'].startswith(('http://', 'https://')):
        pet['image_url'] = f"{API_BASE_URL}{pet['image_url']}"
    
    return render(request, 'adoption_request.html', {'pet': pet})

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def admin_pets(request):
    # Login to Flask backend
    login_response = requests.post(f"{API_BASE_URL}/login", json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        messages.error(request, 'Failed to authenticate with backend service')
        return render(request, 'admin_pets.html', {'pets': []})
    
    # Get pets with session cookie
    response = requests.get(
        f"{API_BASE_URL}/pets",
        cookies=login_response.cookies
    )
    
    pets = response.json() if response.status_code == 200 else []
    
    # Convert relative image URLs to absolute URLs
    for pet in pets:
        if pet.get('image_url') and not pet['image_url'].startswith(('http://', 'https://')):
            pet['image_url'] = f"{API_BASE_URL}{pet['image_url']}"
    
    if request.method == 'POST':
        data = {
            'name': request.POST['name'],
            'type': request.POST['type'],
            'breed': request.POST.get('breed', ''),
            'gender': request.POST.get('gender', ''),
            'age': request.POST.get('age', ''),
            'description': request.POST.get('description', '')
        }

        # Handle image upload
        if request.FILES.get('image'):
            files = {'image': request.FILES['image']}
            response = requests.post(
                f"{API_BASE_URL}/pets",
                data=data,
                files=files,
                cookies=login_response.cookies
            )
        else:
            response = requests.post(
                f"{API_BASE_URL}/pets",
                json=data,
                cookies=login_response.cookies
            )

        if response.status_code == 201:
            messages.success(request, 'Pet added successfully!')
            return redirect('admin_pets')
        else:
            messages.error(request, 'Failed to add pet.')
    
    return render(request, 'admin_pets.html', {'pets': pets})

@login_required
def admin_requests(request):
    # First ensure we're logged in to the Flask backend
    login_response = requests.post(f"{API_BASE_URL}/login", json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        messages.error(request, 'Failed to authenticate with backend service')
        return render(request, 'admin_requests.html', {'requests': []})
    
    # Get adoption requests with session cookie from login
    response = requests.get(
        f"{API_BASE_URL}/adoption-requests",
        cookies=login_response.cookies  # Use the session cookie from login
    )
    
    requests_list = response.json() if response.status_code == 200 else []
    if response.status_code != 200:
        messages.error(request, f"Failed to fetch adoption requests: {response.status_code}")
    return render(request, 'admin_requests.html', {'requests': requests_list})

@login_required
def mark_adopted(request, id):
    if request.method == 'POST':
        # Login to Flask backend
        login_response = requests.post(f"{API_BASE_URL}/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code != 200:
            messages.error(request, 'Failed to authenticate with backend service')
            return redirect('admin_pets')
        
        response = requests.patch(
            f"{API_BASE_URL}/pets/{id}/adopted",
            cookies=login_response.cookies
        )
        if response.status_code == 200:
            messages.success(request, 'Pet marked as adopted!')
        else:
            messages.error(request, 'Failed to mark pet as adopted.')
        return redirect('admin_pets')
    return HttpResponse(status=405)

@login_required
def delete_pet(request, id):
    if request.method == 'POST':
        # Login to Flask backend
        login_response = requests.post(f"{API_BASE_URL}/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code != 200:
            messages.error(request, 'Failed to authenticate with backend service')
            return redirect('admin_pets')
        
        response = requests.delete(
            f"{API_BASE_URL}/pets/{id}",
            cookies=login_response.cookies
        )
        if response.status_code == 200:
            messages.success(request, 'Pet deleted successfully!')
        else:
            messages.error(request, 'Failed to delete pet.')
        return redirect('admin_pets')
    return HttpResponse(status=405)

@login_required
def approve_request(request, id):
    if request.method == 'POST':
        # Login to Flask backend
        login_response = requests.post(f"{API_BASE_URL}/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code != 200:
            messages.error(request, 'Failed to authenticate with backend service')
            return redirect('admin_requests')
        
        # Approve request using session cookie
        response = requests.patch(
            f"{API_BASE_URL}/adoption-requests/{id}/approve",
            cookies=login_response.cookies
        )
        
        if response.status_code == 200:
            messages.success(request, 'Adoption request approved and pet marked as adopted!')
        else:
            messages.error(request, 'Failed to approve adoption request.')
        return redirect('admin_requests')
    return HttpResponse(status=405)

@login_required
def delete_request(request, id):
    if request.method == 'POST':
        # Login to Flask backend
        login_response = requests.post(f"{API_BASE_URL}/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code != 200:
            messages.error(request, 'Failed to authenticate with backend service')
            return redirect('admin_requests')
        
        # Delete request using session cookie
        response = requests.delete(
            f"{API_BASE_URL}/adoption-requests/{id}",
            cookies=login_response.cookies
        )
        
        if response.status_code == 200:
            messages.success(request, 'Adoption request deleted successfully!')
        else:
            messages.error(request, 'Failed to delete adoption request.')
        return redirect('admin_requests')
    return HttpResponse(status=405)

@login_required
def reject_request(request, id):
    if request.method == 'POST':
        # Login to Flask backend
        login_response = requests.post(f"{API_BASE_URL}/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code != 200:
            messages.error(request, 'Failed to authenticate with backend service')
            return redirect('admin_requests')
        
        # Reject request using session cookie
        response = requests.patch(
            f"{API_BASE_URL}/adoption-requests/{id}/reject",
            cookies=login_response.cookies
        )
        
        if response.status_code == 200:
            messages.success(request, 'Adoption request rejected successfully.')
        else:
            messages.error(request, 'Failed to reject adoption request.')
        return redirect('admin_requests')
    return HttpResponse(status=405)

@login_required
def my_adoption_requests(request):
    # Login to Flask backend
    login_response = requests.post(f"{API_BASE_URL}/login", json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        messages.error(request, 'Failed to authenticate with backend service')
        return render(request, 'my_adoption_requests.html', {'requests': []})
    
    # Get adoption requests for the current user
    response = requests.get(
        f"{API_BASE_URL}/adoption-requests",
        cookies=login_response.cookies,
        params={'user_name': request.user.username}  # Filter by current user
    )
    
    requests_list = response.json() if response.status_code == 200 else []
    return render(request, 'my_adoption_requests.html', {'requests': requests_list})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('index')
    return render(request, 'signup.html')