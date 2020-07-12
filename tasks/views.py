from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.datetime_safe import datetime
from django.views.decorators.cache import cache_page
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from tasks.models import TodoItem, Category

@cache_page(300)
def cached_page(request):
    return HttpResponse(f"<p>Cached time: {datetime.now().isoformat()}</p><p>5 minutes to update.</p>")


def index(request):

    # 1st version
    # counts = {t.name: random.randint(1, 100) for t in Tag.objects.all()}

    # 2nd version
    # counts = {t.name: t.taggit_taggeditem_items.count()
    # for t in Tag.objects.all()}

    # 3rd version
    from django.db.models import Count
    counts = Category.objects.all()
    return render(request, "tasks/index.html", {"counts": counts})


def filter_tasks(tags_by_task):
    return set(sum(tags_by_task, []))


def tasks_by_cat(request, cat_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all()

    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        tasks = tasks.filter(category__in=[cat])

    categories = []
    for t in tasks:
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)

    return render(
        request,
        "tasks/list_by_cat.html", {
            "category": cat,
            "tasks": tasks,
            "categories": sorted(categories, key=lambda x: x.todo_count, reverse=True)
        },
    )


class TaskListView(ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        return qs.filter(owner=u)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_tasks = self.get_queryset()
        tags = []
        for t in user_tasks:
            tags.append(list(t.category.all()))
        context['categories'] = sorted(
            filter_tasks(tags), key=lambda cat: cat.todo_count, reverse=True
        )
        return context


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = "tasks/details.html"
