from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import UserProfile, FamilyRelationship
from django.db import models
import json
import base64
import random
from django.core.mail import send_mail
from .models import PendingSignup
from django.contrib.auth.hashers import make_password


#page views
def home_page_view(request):
    return render(request, 'index.html')

def signup_page_view(request):
    return render(request, 'signup.html')

def signup_verify_page_view(request):
    return render(request, 'signup-verify.html')

def profile_setup(request):
    return render(request, 'profile-setup.html')

def authentication_page_view(request):
    return render(request, 'authentication.html')

def notification(request):
    return render(request, 'notification.html')

@login_required
def search(request):
    return render(request, 'search.html')

def profile_tree_view(request, user_id: int):
    return render(request, 'profile-tree.html', { 'view_user_id': user_id })



# #function views
# @login_required
# def home(request):
#     try:
#         profile = request.user.profile
#         if not profile.is_profile_complete:
#             return redirect('profile-setup')
#     except UserProfile.DoesNotExist:
#         return redirect('profile-setup')
    
#     profile_image_url = None
#     if request.user.profile.profile_image:
#         try:
#             profile_image_url = request.user.profile.profile_image.url
#         except Exception as e:
#             print(f"Error getting profile image URL: {e}")
    
#     context = {
#         'user': request.user,
#         'profile': request.user.profile,
#         'profile_image_url': profile_image_url,
#         'user_name': request.user.first_name or request.user.username,
#         'user_location': f"{request.user.profile.country}, {request.user.profile.state}" if request.user.profile.country and request.user.profile.state else "Location not set"
#     }
    
#     return render(request, 'Home.html', context)
@login_required
def home(request):
    try:
        profile = request.user.profile
        if not profile.is_profile_complete:
            return redirect('profile-setup')
    except UserProfile.DoesNotExist:
        return redirect('profile-setup')
    
    profile_image_url = None
    if request.user.profile.profile_image:
        try:
            profile_image_url = request.user.profile.profile_image.url
        except Exception as e:
            print(f"Error getting profile image URL: {e}")
    
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'profile_image_url': profile_image_url,
        'user_name': request.user.first_name or request.user.username,
        'user_location': f"{request.user.profile.district}, {request.user.profile.state}".strip(', ') if request.user.profile.district or request.user.profile.state else "Location not set",
        'current_user_id': request.user.id,  # Add this line
    }
    
    return render(request, 'Home.html', context)

# @csrf_exempt
# def signup(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         username = data['user_name']
#         email = data['email']

#         if User.objects.filter(username=username).exists() or PendingSignup.objects.filter(username=username).exists():
#             return JsonResponse({'success': False, 'message': 'Username already exists'})
#         if User.objects.filter(email=email).exists() or PendingSignup.objects.filter(email=email).exists():
#             return JsonResponse({'success': False, 'message': 'Email already exists'})

#         # Generate OTP
#         otp = f"{random.randint(1000, 9999)}"

#         # Save pending signup
#         pending_user = PendingSignup.objects.create(
#             full_name=data['full_name'],
#             username=username,
#             password=make_password(data['password']),  # hash password
#             email=email,
#             phone_number=data.get('phone_number', ''),
#             otp=otp
#         )

#         # Send email with OTP
#         send_mail(
#             subject='Verify your email',
#             message=f'Your verification code is {otp}',
#             from_email='lifecraft.dev@gmail.com',
#             recipient_list=[email],
#         )

#         return JsonResponse({'success': True, 'message': 'OTP sent to your email', 'token': str(pending_user.token)})
#     return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['user_name']
        email = data['email']

        if User.objects.filter(username=username).exists() or PendingSignup.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Username already exists'})
        if User.objects.filter(email=email).exists() or PendingSignup.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already exists'})

        otp = f"{random.randint(1000, 9999)}"

        pending_user = PendingSignup.objects.create(
            full_name=data['full_name'],
            username=username,
            password=make_password(data['password']),
            email=email,
            phone_number=data.get('phone_number', ''),
            otp=otp
        )

        print(f"[DEBUG] OTP for {email} is {otp}")

        return JsonResponse({'success': True, 'message': 'OTP generated', 'token': str(pending_user.token)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def verify_signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        otp = data.get('otp')

        try:
            pending_user = PendingSignup.objects.get(token=token)
        except PendingSignup.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid token'})

        if pending_user.otp != otp:
            return JsonResponse({'success': False, 'message': 'Invalid OTP'})

        user = User.objects.create(
            username=pending_user.username,
            email=pending_user.email,
            first_name=pending_user.full_name,
            password=pending_user.password,
        )
        UserProfile.objects.create(
            user=user,
            phone_number=pending_user.phone_number
        )

        pending_user.delete()

        return JsonResponse({'success': True, 'message': 'Signup verified. You can now login.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True, 
                'message': 'Login successful',
                'redirect_url': '/home/'
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid username or password'
            }, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def logout_view(request):
    logout(request)
    return redirect('index')

@csrf_exempt
def profile_setup_api(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})
        
        data = json.loads(request.body)
        print(f"Received data: {data}")
        try:
            try:
                profile = UserProfile.objects.get(user=request.user)
                print(f"Found existing profile for user: {request.user.username}")
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=request.user)
                print(f"Created new profile for user: {request.user.username}")
            
            if data.get('full_name'):
                request.user.first_name = data.get('full_name')
                request.user.save()
                print(f"Updated user first_name to: {request.user.first_name}")
            
            date_of_birth = data.get('date_of_birth')
            if date_of_birth:
                try:
                    from datetime import datetime
                    profile.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                except ValueError:
                    print(f"Invalid date format: {date_of_birth}")
                    profile.date_of_birth = None
            else:
                profile.date_of_birth = None
                
            profile.father_name = data.get('father_name', '')
            profile.mother_name = data.get('mother_name', '')
            profile.job = data.get('job', '')
            profile.country = data.get('country', '')
            profile.state = data.get('state', '')
            profile.district = data.get('district', '')
            profile.location = data.get('location', '')
            profile.is_profile_complete = True
            
            print(f"Updated profile fields: DOB={profile.date_of_birth}, Father={profile.father_name}, Mother={profile.mother_name}, Job={profile.job}, Country={profile.country}")  # Debug print

            if data.get('profile_image'):
                image_data = data['profile_image']
                if image_data.startswith('data:image'):

                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    imgdata = base64.b64decode(imgstr)
                    filename = f"profile_{request.user.id}.{ext}"
                    profile.profile_image.save(filename, ContentFile(imgdata), save=True)
            
            profile.save()
            print(f"Profile saved successfully for user: {request.user.username}")  # Debug print
            
            return JsonResponse({
                'success': True, 
                'message': 'Profile updated successfully',
                'redirect_url': '/home/'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# @csrf_exempt
# def get_users_api(request):
#     if request.method == 'GET':
#         try:
#             # Get all users with completed profiles
#             users_with_profiles = User.objects.filter(
#                 profile__is_profile_complete=True
#             ).select_related('profile')
            
#             users_data = []
#             for user in users_with_profiles:
#                 profile = user.profile
#                 users_data.append({
#                     'id': user.id,
#                     'name': user.first_name or user.username,
#                     'username': user.username,
#                     'family': f"{profile.father_name} & {profile.mother_name}" if profile.father_name and profile.mother_name else "Family",
#                     'profile_image': profile.profile_image.url if profile.profile_image else '',
#                     'country': profile.country,
#                     'state': profile.state,
#                     'job': profile.job,
#                     'phone_number': profile.phone_number
#                 })
            
#             return JsonResponse({'success': True, 'users': users_data})
#         except Exception as e:
#             return JsonResponse({'success': False, 'message': str(e)})
    
#     return JsonResponse({'success': False, 'message': 'Invalid request method'})
@csrf_exempt
def get_users_api(request):
    if request.method == 'GET':
        try:
            users_with_profiles = User.objects.filter(
                profile__is_profile_complete=True
            ).select_related('profile')
            
            users_data = []
            for user in users_with_profiles:
                profile = user.profile
                users_data.append({
                    'id': user.id,
                    'name': user.first_name or user.username,
                    'username': user.username,
                    'family': f"{profile.father_name} & {profile.mother_name}" if profile.father_name and profile.mother_name else "Family",
                    'profile_image': profile.profile_image.url if profile.profile_image else '',
                    'country': profile.country,
                    'state': profile.state,
                    'job': profile.job,
                    'phone_number': profile.phone_number
                })
            
            return JsonResponse({
                'success': True, 
                'users': users_data,
                'current_user_id': request.user.id  # Add this line
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def relate_user_api(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})

        data = json.loads(request.body)

        from_user_id = data.get('from_user_id')
        to_user_id = data.get('to_user_id') or data.get('target_user_id')
        relationship_type = data.get('relation') or data.get('relationship_type')
        relation_label = data.get('label', '')
        middle_user_id = data.get('middle_user_id')
        message = data.get('message', '')

        try:
            from_user = request.user if not from_user_id else User.objects.get(id=from_user_id)
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})

        if from_user == to_user:
            return JsonResponse({'success': False, 'message': 'You cannot relate to yourself'})

        try:
            middle_user = None
            if middle_user_id:
                try:
                    middle_user = User.objects.get(id=middle_user_id)
                except User.DoesNotExist:
                    middle_user = None

            existing = FamilyRelationship.objects.filter(
                from_user=from_user,
                to_user=to_user,
                relationship_type=relationship_type,
                status__in=['pending', 'accepted']
            ).first()
            if existing:
                msg = 'Relationship request already sent' if existing.status == 'pending' else 'You are already related'
                return JsonResponse({'success': False, 'message': msg})

            rel = FamilyRelationship.objects.create(
                from_user=from_user,
                to_user=to_user,
                relationship_type=relationship_type,
                relation_label=relation_label,
                middle_user=middle_user,
                message=message,
            )

            return JsonResponse({
                'success': True,
                'message': f'Request sent to {to_user.first_name or to_user.username}',
                'id': rel.id,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def get_notifications_api(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})
        
        try:
            pending_requests = FamilyRelationship.objects.filter(
                to_user=request.user,
                status='pending'
            ).select_related('from_user', 'from_user__profile')
            
            notifications = []
            for req in pending_requests:
                notifications.append({
                    'id': req.id,
                    'from_user': {
                        'id': req.from_user.id,
                        'name': req.from_user.first_name or req.from_user.username,
                        'profile_image': req.from_user.profile.profile_image.url if req.from_user.profile.profile_image else None
                    },
                    'relationship_type': req.relationship_type,
                    'message': req.message,
                    'created_at': req.created_at.isoformat()
                })
            
            return JsonResponse({'success': True, 'notifications': notifications})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def respond_to_relationship_api(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})
        
        data = json.loads(request.body)
        relationship_id = data.get('relationship_id')
        action = data.get('action')
        
        try:
            relationship = FamilyRelationship.objects.get(
                id=relationship_id,
                to_user=request.user,
                status='pending'
            )
            
            if action == 'accept':
                relationship.status = 'accepted'
                relationship.save()
                return JsonResponse({
                    'success': True, 
                    'message': f'You are now {relationship.relationship_type} of {relationship.from_user.first_name or relationship.from_user.username}'
                })
            elif action == 'reject':
                relationship.status = 'rejected'
                relationship.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Relationship request rejected'
                })
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action'})
                
        except FamilyRelationship.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Relationship request not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def get_activity_api(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})

        try:
            accepted = FamilyRelationship.objects.filter(
                from_user=request.user,
                status='accepted'
            ).select_related('to_user', 'to_user__profile').order_by('-updated_at')

            items = []
            for rel in accepted:
                items.append({
                    'id': rel.id,
                    'to_user': {
                        'id': rel.to_user.id,
                        'name': rel.to_user.first_name or rel.to_user.username,
                        'profile_image': rel.to_user.profile.profile_image.url if getattr(rel.to_user, 'profile', None) and rel.to_user.profile.profile_image else None,
                    },
                    'relationship_type': rel.relationship_type,
                    'relation_label': rel.relation_label or rel.relationship_type,
                    'updated_at': rel.updated_at.isoformat(),
                })

            return JsonResponse({'success': True, 'activity': items})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# @csrf_exempt
# def get_family_graph_api(request):
#     if request.method == 'GET':
#         if not request.user.is_authenticated:
#             return JsonResponse({'success': False, 'message': 'User not authenticated'})

#         try:
#             center_user = request.user
#             q_user_id = request.GET.get('user_id')
#             if q_user_id:
#                 try:
#                     center_user = User.objects.get(id=int(q_user_id))
#                 except Exception:
#                     center_user = request.user
#             rels_1 = FamilyRelationship.objects.filter(
#                 status='accepted'
#             ).filter(
#                 models.Q(from_user=center_user) | models.Q(to_user=center_user)
#             ).select_related('from_user', 'to_user', 'from_user__profile', 'to_user__profile')

#             one_hop_user_ids = {center_user.id}
#             for r in rels_1:
#                 one_hop_user_ids.add(r.from_user_id)
#                 one_hop_user_ids.add(r.to_user_id)

#             rels_2 = FamilyRelationship.objects.filter(
#                 status='accepted'
#             ).filter(
#                 models.Q(from_user_id__in=one_hop_user_ids) | models.Q(to_user_id__in=one_hop_user_ids)
#             ).select_related('from_user', 'to_user', 'from_user__profile', 'to_user__profile')

#             rels = list(rels_2)

#             user_ids = set()
#             for r in rels:
#                 user_ids.add(r.from_user_id)
#                 user_ids.add(r.to_user_id)

#             users = User.objects.filter(id__in=user_ids).select_related('profile')
#             id_to_user = {u.id: u for u in users}

#             nodes = []
#             for uid in user_ids:
#                 u = id_to_user.get(uid)
#                 if not u:
#                     continue
#                 img = None
#                 if hasattr(u, 'profile') and u.profile and u.profile.profile_image:
#                     img = u.profile.profile_image.url
#                 nodes.append({
#                     'id': uid,
#                     'name': u.first_name or u.username,
#                     'job': getattr(getattr(u, 'profile', None), 'job', '') or '',
#                     'country': getattr(getattr(u, 'profile', None), 'country', '') or '',
#                     'state': getattr(getattr(u, 'profile', None), 'state', '') or '',
#                     'profile_image': img,
#                     'is_me': uid == center_user.id,
#                 })

#             links = []
#             for r in rels:
#                 links.append({
#                     'source': r.from_user_id,
#                     'target': r.to_user_id,
#                     'type': r.relationship_type,
#                     'label': r.relation_label or r.relationship_type,
#                 })

#             return JsonResponse({'success': True, 'current_user_id': center_user.id, 'nodes': nodes, 'links': links})
#         except Exception as e:
#             return JsonResponse({'success': False, 'message': str(e)})

#     return JsonResponse({'success': False, 'message': 'Invalid request method'})
@csrf_exempt
def get_family_graph_api(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})

        try:
            center_user = request.user
            q_user_id = request.GET.get('user_id')
            if q_user_id:
                try:
                    center_user = User.objects.get(id=int(q_user_id))
                except Exception:
                    center_user = request.user
            
            rels_1 = FamilyRelationship.objects.filter(
                status='accepted'
            ).filter(
                models.Q(from_user=center_user) | models.Q(to_user=center_user)
            ).select_related('from_user', 'to_user', 'from_user__profile', 'to_user__profile')

            one_hop_user_ids = {center_user.id}
            for r in rels_1:
                one_hop_user_ids.add(r.from_user_id)
                one_hop_user_ids.add(r.to_user_id)

            rels_2 = FamilyRelationship.objects.filter(
                status='accepted'
            ).filter(
                models.Q(from_user_id__in=one_hop_user_ids) | models.Q(to_user_id__in=one_hop_user_ids)
            ).select_related('from_user', 'to_user', 'from_user__profile', 'to_user__profile')

            rels = list(rels_2)

            # IMPORTANT: Always include center user even if no relations
            user_ids = {center_user.id}
            for r in rels:
                user_ids.add(r.from_user_id)
                user_ids.add(r.to_user_id)

            users = User.objects.filter(id__in=user_ids).select_related('profile')
            id_to_user = {u.id: u for u in users}

            nodes = []
            for uid in user_ids:
                u = id_to_user.get(uid)
                if not u:
                    continue
                
                profile = getattr(u, 'profile', None)
                img = None
                if profile and profile.profile_image:
                    img = profile.profile_image.url
                
                location_parts = []
                if profile:
                    if profile.location:
                        location_parts.append(profile.location)
                    if profile.district:
                        location_parts.append(profile.district)
                    if profile.state:
                        location_parts.append(profile.state)
                    if profile.country:
                        location_parts.append(profile.country)
                
                location_str = ', '.join(location_parts) if location_parts else 'Location not set'
                
                nodes.append({
                    'id': uid,
                    'name': u.first_name or u.username,
                    'username': u.username,
                    'job': getattr(profile, 'job', '') or '',
                    'country': getattr(profile, 'country', '') or '',
                    'state': getattr(profile, 'state', '') or '',
                    'location': location_str,
                    'profile_image': img,  # This will be None if no image, or the URL
                    'is_me': uid == center_user.id,
                })

            links = []
            for r in rels:
                links.append({
                    'source': r.from_user_id,
                    'target': r.to_user_id,
                    'type': r.relationship_type,
                    'label': r.relation_label or r.relationship_type,
                })

            return JsonResponse({
                'success': True, 
                'current_user_id': center_user.id, 
                'nodes': nodes, 
                'links': links
            })
        except Exception as e:
            import traceback
            print(f"Error in get_family_graph_api: {e}")
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})



@csrf_exempt
def relation_status_api(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})
        target_id = request.GET.get('user_id')
        if not target_id:
            return JsonResponse({'success': False, 'message': 'user_id is required'})
        try:
            target = User.objects.get(id=int(target_id))
            related = FamilyRelationship.objects.filter(
                models.Q(from_user=request.user, to_user=target) |
                models.Q(from_user=target, to_user=request.user),
                status='accepted'
            ).exists()
            pending_qs = FamilyRelationship.objects.filter(
                models.Q(from_user=request.user, to_user=target) |
                models.Q(from_user=target, to_user=request.user),
                status='pending'
            )
            pending = pending_qs.exists()
            my_outgoing = FamilyRelationship.objects.filter(
                from_user=request.user, to_user=target, status='pending'
            ).first()
            return JsonResponse({'success': True, 'related': related, 'pending': pending, 'outgoing_id': my_outgoing.id if my_outgoing else None})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def relation_withdraw_api(request):
    """Cancel/withdraw my pending request to a target user."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})
        try:
            data = json.loads(request.body)
            target_id = data.get('target_user_id')
            rel_id = data.get('relationship_id')
            if rel_id:
                rel = FamilyRelationship.objects.get(id=rel_id, from_user=request.user, status='pending')
            else:
                rel = FamilyRelationship.objects.get(from_user=request.user, to_user_id=target_id, status='pending')
            rel.delete()
            return JsonResponse({'success': True})
        except FamilyRelationship.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No pending request found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('login-verify')
    
    return render(request, 'profile-page.html', {
        'user': request.user
    })


@csrf_exempt
def update_profile_api(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})

        try:
            if 'first_name' in request.POST:
                request.user.first_name = request.POST['first_name']
            if 'last_name' in request.POST:
                request.user.last_name = request.POST['last_name']
            if 'email' in request.POST:
                request.user.email = request.POST['email']
            request.user.save()

            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            if 'phone_number' in request.POST:
                profile.phone_number = request.POST['phone_number']
            if 'date_of_birth' in request.POST and request.POST['date_of_birth']:
                profile.date_of_birth = request.POST['date_of_birth']
            if 'job' in request.POST:
                profile.job = request.POST['job']
            if 'father_name' in request.POST:
                profile.father_name = request.POST['father_name']
            if 'mother_name' in request.POST:
                profile.mother_name = request.POST['mother_name']
            if 'country' in request.POST:
                profile.country = request.POST['country']
            if 'state' in request.POST:
                profile.state = request.POST['state']
            if 'district' in request.POST:
                profile.district = request.POST['district']
            if 'location' in request.POST:
                profile.location = request.POST['location']
            
            profile.save()

            return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def update_profile_pic_api(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})

        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            if 'profile_image' in request.FILES:
                profile.profile_image = request.FILES['profile_image']
                profile.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Profile picture updated successfully',
                    'image_url': profile.profile_image.url
                })
            else:
                return JsonResponse({'success': False, 'message': 'No image provided'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def get_family_members_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'User not authenticated'})

    try:
        relationships = FamilyRelationship.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user),
            status='accepted'
        )
        
        members = []
        for rel in relationships:
            other_user = rel.to_user if rel.from_user == request.user else rel.from_user
            if other_user.profile.is_profile_complete:
                members.append({
                    'id': other_user.id,
                    'name': other_user.first_name or other_user.username,
                    'profile_image': other_user.profile.profile_image.url if other_user.profile.profile_image else None,
                    'relation': rel.relation_label or rel.relationship_type
                })
        
        return JsonResponse({'success': True, 'members': members})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})