
from django.urls import path
from django.contrib import admin
from . import views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path("", views.index, name="index"),
    path('admin/', admin.site.urls),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("profile", views.profile, name="profile"),
    path("editprofile", views.edit_profile, name="editprofile"),
    path("us2profile/<int:user_id>", views.us2_profile,name="us2profile" ),
    path("messages", views.compose, name="compose"),
    path("messages/<int:Message_id>", views.message, name="message"),
    path("messages/<str:mailbox>", views.mailbox, name="mailbox"),
    path("mess",views.mess,name="mess"),
    path("match", views.match,name="match" ),
    path("register", views.register, name="register")
    ]



