from . import views
from django.urls import path

urlpatterns = [
    path("movies/", views.movie_list, name="movies"),
    path("register/", views.RegistrationView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("collection/", views.CollectionListView.as_view(), name="collection-list"),
    # path(
    #     "collection/<uuid>/",
    #     views.CollectionDetailView.as_view(),
    #     name="collection-detail",
    # ),
    # path(
    #     "collection/<uuid>/movies/",
    #     views.CollectionMoviesView.as_view(),
    #     name="collection-movies",
    # ),
]
