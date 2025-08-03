from django.shortcuts import render, get_object_or_404
from .models import Polls,Vote
from .forms import PollForm
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Create your views here.

def home(request):
    polls = Polls.objects.all()
    return render(request, "polling_site/home.html",{"polls": polls})

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
    if request.user.is_authenticated:
        has_voted = Vote.objects.filter(user=request.user, poll = poll).exists()
    
    if request.method == "POST" and not has_voted:
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
    return render(request, "polling_site/polling_detail.html", {"poll": poll ,"has_voted": has_voted})

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