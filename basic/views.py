from django.db.models import Q
from django.views.generic import ListView

from .models import med_basic


class basic_view(ListView):
    template_name = "basic.html"
    model = med_basic

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        self.search_term = query
        if not query:
            return med_basic.objects.none()

        filters = (
            Q(Plant_Name__icontains=query)
            | Q(Scientific_Name__icontains=query)
            | Q(Description__icontains=query)
        )
        return med_basic.objects.filter(filters).order_by("Plant_Name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = getattr(self, "search_term", "")
        context["catalogue"] = (
            med_basic.objects.all()
            .order_by("Plant_Name")
            .values_list("Plant_Name", "Scientific_Name")
        )
        context["result_count"] = context["object_list"].count()
        return context