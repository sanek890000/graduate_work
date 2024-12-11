from django.urls import path
# from .views import FilterMoviesByRating
from . import views

urlpatterns = [
    path("", views.MoviesView.as_view()),
    path("filter/", views.FilterMoviesView.as_view(), name='filter'),
    path("search/", views.Search.as_view(), name='search'),
    path("add-rating/", views.AddStarRating.as_view(), name='add_rating'),
    path("json-filter/", views.JsonFilterMoviesView.as_view(), name='json_filter'),
    path("<slug:slug>/", views.MovieDetailView.as_view(), name="movie_detail"),
    path("review/<int:pk>/", views.AddReview.as_view(), name="add_review"),
    path("actor/<str:slug>/", views.ActorView.as_view(), name="actor_detail"),
    path("connection", views.ConnectionFormView.as_view(), name="connection"),
    path('about/', views.about_page, name='about_page'),
    path('index/', views.index_page, name='index_page'),
    path("filter/<int:star>/", views.FilterMoviesView.as_view(), name='filter_by_star'),
    # path('filter/<int:rating>/', FilterMoviesByRating.as_view(), name='filter_movies_by_rating'),

]
