from django.shortcuts import render, get_object_or_404
from .models import Polls
from .forms import PollForm
from django.utils import timezone
from django.shortcuts import redirect

# Create your views here.

def home(request):
    polls = Polls.objects.all()
    return render(request, "polling_site/home.html",{"polls": polls})

def poll_detail(request, poll_id):
    poll = Polls.objects.get(id=poll_id)
    return render(request, "polling_site/polling_detail.html", {"poll": poll})

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