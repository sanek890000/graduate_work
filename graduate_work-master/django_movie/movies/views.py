from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.base import View
from django.urls import reverse_lazy
from .models import Movie, Category, Actor, Genre, Rating
from .forms import *

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.flatpages.models import FlatPage
from .forms import ConnectionForm
from .models import Feedback

# class FilterMoviesByRating(View):
#     # фильтр рейтинга
#     template_name = 'movies/movie_list.html'
#     paginate_by = 12
#
#     def get(self, request, rating):
#         filtered_movies = Movie.objects.filter(rating__star__value=rating)
#         context = {'movie_list': filtered_movies, 'selected_rating': rating}
#         return render(request, self.template_name, context)


def about_page(request):
    flatpage = FlatPage.objects.get(url='/about/')
    return render(request, 'pages/about.html', {'flatpage': flatpage})


def index_page(request):
    flatpage = FlatPage.objects.get(url='/index/')
    return render(request, 'pages/index.html', {'flatpage': flatpage})


class ConnectionFormView(View):
    template_name = 'contact/connection.html'
    success_url = reverse_lazy('about')

    def get(self, request, *args, **kwargs):
        form = ConnectionForm()
        context = {
            'title': "Обратная связь",
            'cat_selected': 2,
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ConnectionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            content = form.cleaned_data['content']

            # Save the feedback to the database
            feedback = Feedback(name=name, email=email, content=content)
            feedback.save()

            success_message = "Спасибо за обращение, мы рассмотрим его и обязательно Вас проинформируем."
            context = {
                'title': "Обратная связь",
                'cat_selected': 2,
                'form': form,
                'success_message': success_message,
            }
            return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, {'form': form})


class GenreYear:
    # Жанры и года выхода аниме
    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values("year").distinct().order_by("-year")


class MoviesView(GenreYear, ListView):
    # Список аниме
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    paginate_by = 9


class MovieDetailView(GenreYear, DetailView):
    # Полное описание аниме
    model = Movie
    slug_field = "url"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        return context


class AddReview(View):
    # Отзывы
    @method_decorator(login_required)  # Добавляем декоратор для проверки аутентификации
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url())


class ActorView(GenreYear, DetailView):
    # Вывод информации о персонаже
    model = Actor
    template_name = 'movies/actor.html'
    slug_field = "name"


class FilterMoviesView(GenreYear, ListView):
    # Фильтр аниме
    model = Movie
    paginate_by = 9
    template_name = 'movies/movie_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        selected_stars = self.kwargs.get('star')
        if selected_stars is not None:
            queryset = queryset.filter(rating__star__value=selected_stars)

        years = self.request.GET.getlist("year")
        genres = self.request.GET.getlist("genre")

        if years:
            queryset = queryset.filter(year__in=years)

        if genres:
            queryset = queryset.filter(genres__in=genres)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["year"] = ''.join([f"year={x}&" for x in self.request.GET.getlist("year")])
        context["genre"] = ''.join([f"genre={x}&" for x in self.request.GET.getlist("genre")])
        return context


class JsonFilterMoviesView(ListView):
    # Фильтр фильмов в json
    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) |
            Q(genres__in=self.request.GET.getlist("genre"))
        ).distinct().values("title", "tagline", "url", "poster")
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        return JsonResponse({"movies": queryset}, safe=False)


class AddStarRating(View):
    # Добавление рейтинга аниме

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


class Search(ListView):
    # Поиск аниме
    paginate_by = 3

    def get_queryset(self):
        return Movie.objects.filter(title__icontains=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context

