from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import User, Profile,ProfileForm, Message
from .forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views import View
# Create your views here.

def index(request):

    return render(request, "unmismatch3d/index.html")
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "unmismatch3d/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "unmismatch3d/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "unmismatch3d/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "unmismatch3d/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "unmismatch3d/register.html")
    
@login_required
def profile(request):
    profile=Profile.objects.filter(username=request.user).all()
    
    
    return render(request, "unmismatch3d/profile.html",{"items":profile})
@login_required
def edit_profile(request):
  if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            post=form.save(commit=False)
            post.username=request.user
            post.save()

            return HttpResponseRedirect("/") 
        else:return redirect('unmismatch3d/editprofile.html')

  else:
        form = ProfileForm()
  return render(request, "unmismatch3d/editprofile.html", {
        "form": form
    })
 
def us2_profile(request,user_id):
    profile=Profile.objects.filter(id=user_id).all()
    
    
    return render(request, "unmismatch3d/profile2.html",{"items":profile})
@login_required
def match(request):
    if request.method == "POST":
        query_seek = request.POST.get('seeking', None)
        query_hobbie = request.POST.get('hobbies', None)
        query_age = request.POST.get('age', None)
        query_gender = request.POST.get('gender', None)


        if query_seek:
            results = Profile.objects.filter(seeking__icontains=query_seek)
            return render(request, 'unmismatch3d/match.html', {"results":results})

        if query_hobbie:
            results = Profile.objects.filter(hobbies__icontains=query_hobbie)
            return render(request, 'unmismatch3d/match.html', {"results":results})

    return render(request, 'unmismatch3d/match.html')

def mess(request):
    if request.user.is_authenticated:
        return render(request, "unmismatch3d/messages.html")


@csrf_exempt
@login_required
def compose(request):

    # Composing a new email must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check recipient emails
    data = json.loads(request.body)
    messages = [message.strip() for message in data.get("recipients").split(",")]
    if messages == [""]:
        return JsonResponse({
            "error": "At least one recipient required."
        }, status=400)

    # Convert email addresses to users
    recipients = []
    for message in messages:
        try:
            user = User.objects.get(username=message)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with message {message} does not exist."
            }, status=400)

    # Get contents of email
    # subject = data.get("subject", "")
    body = data.get("body", "")

    # Create one email for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        message = Message(
            user=user,
            sender=request.user,
            # subject=subject,
            body=body,
            read=user == request.user
        )
        message.save()
        for recipient in recipients:
            message.recipients.add(recipient)
        message.save()

    return JsonResponse({"message": "Email sent successfully."}, status=201)


@login_required
def mailbox(request, mailbox):

    # Filter emails returned based on mailbox
    if mailbox == "inbox":
        messages = Message.objects.filter(
            user=request.user, recipients=request.user, archived=False
        )
    elif mailbox == "sent":
        messages = Message.objects.filter(
            user=request.user, sender=request.user
        )
    elif mailbox == "archive":
        messages = Message.objects.filter(
            user=request.user, recipients=request.user, archived=True
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    # Return emails in reverse chronologial order
    messages = messages.order_by("-timestamp").all()
    return JsonResponse([message.serialize() for message in messages], safe=False)


@csrf_exempt
@login_required
def message(request, Message_id):

    # Query for requested email
    try:
        message = Message.objects.get(user=request.user, pk=Message_id)
    except Message.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(message.serialize())

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            message.read = data["read"]
        if data.get("archived") is not None:
            message.archived = data["archived"]
        message.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)
