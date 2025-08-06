from django.shortcuts import render, get_object_or_404
from .models import Polls,Vote,UserProfile
from .forms import PollForm
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def home(request):
    polls = Polls.objects.all().order_by("?")
    is_subscribed = False
    
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        is_subscribed = user_profile.is_subscribed
    return render(request, "polling_site/home.html",{"polls": polls ,'is_subscribed': is_subscribed})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})

@login_required
def poll_detail(request, poll_id):
    poll = Polls.objects.get(id=poll_id)
    has_voted = False
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    is_subscribed = user_profile.is_subscribed
    if request.user.is_authenticated:
        has_voted = Vote.objects.filter(user=request.user, poll = poll).exists()
    
    if request.method == "POST" and not has_voted and not is_subscribed:
        vote = request.POST.get("vote")
        if vote == "option1":
            poll.vote_count1 += 1
        elif vote == "option2":
            poll.vote_count2 += 1
        poll.save()
        if request.user.is_authenticated:
            Vote.objects.create(user=request.user, poll=poll)
        return redirect('poll_detail', poll_id=poll.id)
    
    
    if request.method == "POST" and has_voted and is_subscribed:
        vote = request.POST.get("vote")
        session_key = f"last_vote_poll_{poll.id}"
        last_vote = request.session.get(session_key, "") 
        
        if last_vote != vote:
            if vote == "option1":
                poll.vote_count1 += 1
                poll.vote_count2 -= 1
            elif vote == "option2":
                poll.vote_count2 += 1
                poll.vote_count1 -= 1
            
            request.session[session_key] = vote
            if poll.vote_count1 < 0:
                poll.vote_count1 = 0
            if poll.vote_count2 < 0:
                poll.vote_count2 = 0
            poll.save()
        
        return redirect('poll_detail', poll_id=poll.id)
    
    if request.method == "POST" and not has_voted and is_subscribed:
        vote = request.POST.get("vote")
        if vote == "option1":
            poll.vote_count1 += 1
        elif vote == "option2":
            poll.vote_count2 += 1
        poll.save()
        if request.user.is_authenticated:
            Vote.objects.create(user=request.user, poll=poll)
        return redirect('poll_detail', poll_id=poll.id)

    
    if request.user.is_authenticated:
     has_voted = Vote.objects.filter(user=request.user, poll=poll).exists()
    return render(request, "polling_site/polling_detail.html", {"poll": poll ,"has_voted": has_voted, "is_subscribed": is_subscribed})

@login_required
def create_poll(request):
    if request.method == "POST":
        form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.author = request.user
            poll.pub_date = timezone.now()
            poll.save()
            return redirect('home')
    else:
        form = PollForm()
    return render(request, 'polling_site/create_poll.html', {'form': form})
@login_required
def delete_poll(request, poll_id):
    poll = get_object_or_404(Polls, id=poll_id)
    if request.user == poll.author:
        poll.delete()
        return redirect('home')
    else:
        return render(request, 'polling_site/error.html', {'message': 'You are not authorized to delete this poll.'})

@login_required
def your_polls(request):
    polls = Polls.objects.filter(author=request.user)
    return render(request, 'polling_site/your_polls.html', {'polls': polls})

@login_required
def subscribe(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    is_subscribed = user_profile.is_subscribed
    return render(request, 'subscription/sub.html', {'is_subscribed': is_subscribed})

@login_required
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    stripe.api_key = settings.STRIPE_SECRET_KEY
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if user_profile.is_subscribed:
        return render(request, 'subscription/success.html', {'message': 'You are already subscribed.'})


    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Vote Change Subscription',
                    },
                    'unit_amount': 1000,  
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
def success(request):
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        if not user_profile.is_subscribed:
            user_profile.is_subscribed = True
            user_profile.save()
    return render(request, 'subscription/success.html')

def cancel(request):
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        if user_profile.is_subscribed:
            user_profile.is_subscribed = False
            user_profile.save()
    return render(request, 'subscription/cancel.html')

