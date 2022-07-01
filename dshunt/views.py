import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView
from django.views.generic.dates import DayArchiveView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .forms import BookCreateForm, VideoCreateForm, TutorialCreateForm, PodcastEpisodeCreateForm, PostTypeForm
from .models import Post, PostVote


class PostListHomeView(View):
    model = Post

    def get_posts_and_votes(self, posts):
        # return [(post, post.get_vote_count()) for post in posts]
        return [
            {
                'post': post,
                'vote': post.get_vote_count(),
                'is_voted': post.is_voted(self.request.user)
            } for post in posts]

    def get(self, request, *args, **kwargs):
        main_posts = {}
        post_count = {}
        today = datetime.date.today()

        for i in range(7):
            post_date = today-datetime.timedelta(days=i)
            posts = self.model.objects.filter(published_at__date=post_date, approved=True)

            if posts.exists():
                sorted_posts = sorted(posts, key=lambda obj: obj.get_vote_count(), reverse=True)[:5]
                main_posts[post_date] = self.get_posts_and_votes(sorted_posts)
                post_count[post_date] = posts.count()

        # Redirecting to all post list when main_posts is empty
        if not main_posts:
            return render('posts')

        context = {'posts': main_posts, 'post_count': post_count, 'yesterday': today-datetime.timedelta(days=1)}
        return render(request, 'posts.html', context)


class PostListView(ListView):
    queryset = Post.objects.filter(approved=True).order_by('-published_at')

    def get_posts_and_votes(self, posts):
        # return [(post, post.get_vote_count()) for post in posts]
        return [
            {
                'post': post,
                'vote': post.get_vote_count(),
                'is_voted': post.is_voted(self.request.user)
            } for post in posts]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.core.paginator import Paginator
        per_page = self.request.GET.get('per_page', 10)
        page_number = self.request.GET.get('page', 1)

        paginator = Paginator(self.queryset, per_page)
        page_obj = paginator.page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page_obj
        context['is_paginated'] = True
        context['post_list'] = self.get_posts_and_votes(page_obj.object_list)
        return context


class PostListByDateView(DayArchiveView):
    queryset = Post.objects.filter(approved=True).order_by('-published_at')
    date_field = 'published_at'
    template_name = 'dshunt/post_list.html'
    paginate_by = 10

    def get_posts_and_votes(self, posts):
        return [
            {
                'post': post,
                'vote': post.get_vote_count(),
                'is_voted': post.is_voted(self.request.user)
            } for post in posts]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_list'] = self.get_posts_and_votes(context['post_list'])
        return context


class PostSubmitPageView(View):
    template_name = 'dshunt/post_submit.html'
    form = PostTypeForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'post_type_form': self.form})

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            post_type = form.cleaned_data.get('post_type')
            post_views = {'Book': 'book-create', 'Video': 'video-create', 'Tutorial': 'tutorial-create',
                          'Podcast': 'podcast-episode-create'}
            return redirect(post_views.get(post_type))
        self.get(request, *args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = PostTypeForm()
    #     context['book_form'] = BookCreateForm()
    #     context['video_form'] = VideoCreateForm()
    #     context['tutorial_form'] = TutorialCreateForm()
    #     context['podcast_form'] = PodcastEpisodeCreateForm()
    #     return context


class BookCreateView(View):
    form_class = BookCreateForm
    template_name = 'dshunt/book_create_form.html'
    post_type_form = PostTypeForm(initial={'post_type': 'Book'})

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'post_type_form': self.post_type_form, 'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_user = self.request.user
            book.post_type = 'Book'
            book.save()
            return redirect('post-list')
        else:
            return render(request, self.template_name, {'form': self.post_type_form, 'book_form': form})


class VideoCreateView(CreateView):
    form_class = VideoCreateForm
    template_name = 'dshunt/video_create_form.html'
    initial = {'post_type': 'Video'}
    post_type = 'Video'
    success_url = reverse_lazy('post-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['form'] = self.form_class
        context['post_type_form'] = PostTypeForm(initial=self.initial)
        return context

    def form_valid(self, form):
        form.instance.post_type = self.post_type
        form.instance.created_user = self.request.user
        return super().form_valid(form)


@login_required()
def tutotrial_create(request):
    post_type_form = PostTypeForm(initial={'post_type': 'Tutorial'})
    form = TutorialCreateForm()
    context = {'post_type_form': post_type_form, 'form': form}

    if request.method == 'POST':
        form = TutorialCreateForm(request.POST)
        if form.is_valid():
            tutorial = form.instance
            # tutorial = form.save(commit=False)
            tutorial.post_type = 'Tutorial'
            tutorial.created_user = request.user
            tutorial.save()
            return redirect('post-list')
        else:
            context['form'] = form
            return render(request, 'dshunt/tutorial_create_from.html', context)
    else:
        return render(request, 'dshunt/tutorial_create_form.html', context)


class PodcastEpisodeCreateView(VideoCreateView):
    form_class = PodcastEpisodeCreateForm
    template_name = 'dshunt/podcast_episode_create_form.html'
    initial = {'post_type': 'Podcast'}
    post_type = 'Podcast'


# Voting to Post

class Vote(View):
    def get(self, request, *args, **kwargs):
        post = Post.objects.get(id=kwargs['id'])
        vote = PostVote(post=post, created_user=request.user)
        vote.save()
        return redirect('post-list')


# CATEGORY

def category(request):
    cat = Category.objects.all()
    context = {'category':cat}
    return render(request, 'dshunt/category.html', context)


from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView, DayArchiveView
from .models import Post


class ArchiveView(DayArchiveView):
    # model = Post
    queryset = Post.objects.all()
    date_field = 'published_at'
    template_name_suffix = '_archive'
    # make_object_list = True
    # allow_future = True
    allow_empty = True
