from multiselectfield import MultiSelectField

from django.forms import ModelForm, ClearableFileInput

from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from django import forms

# Create your models here.

class User(AbstractUser):
    pass

class Profile(models.Model):
    
    HOBBY_CHOICES=[
        ('golf', 'GOLF'),
        ('reading', 'READING'),
        ('pottery', 'POTTERY'),
        ('bingewatching', 'BINGEWATCHING'),
      
    ]
    SEEK_CHOICES=[
        ('casual relationship', 'CASUAL RELATIONSHIP'),
        ('romantic relationship','ROMANTIC RELATIONSHIP'),
        ('not sure','NOT SURE'),
                  ]
    
    seeking=MultiSelectField(choices=SEEK_CHOICES,default='ralationship')
    username=models.ForeignKey(User, on_delete=models.CASCADE )
    location=models.CharField(max_length=99,null=True)
    hobbies=MultiSelectField( choices=HOBBY_CHOICES, default="reading")
    gender=models.CharField(max_length=65,default= 'female' )
    bio=models.CharField(max_length=300)
    age=models.IntegerField(null=False)
    widget=forms.Select(choices=HOBBY_CHOICES)
    class Meta:
        db_table = 'Profile'
        
    ''' def calculate_age(born):
     today = date.today()
     return today.year - born.year - ((today.month, today.day) < (born.month, born.day)) '''
 
 
class ProfileForm(ModelForm):
     class Meta:
        model=Profile
        fields = ['location', 'hobbies', 'gender','age']
        
     def test_func(self):
         
        post = self.get_object()
        return self.request.user == post.user
    
from django.db import models

class Message(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("User", on_delete=models.PROTECT, related_name="messages_sent")
    recipients = models.ManyToManyField("User", related_name="messages_received")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.username,
            "recipients": [user.username for user in self.recipients.all()],
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "read": self.read,
            "archived": self.archived
        }