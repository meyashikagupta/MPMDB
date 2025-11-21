from django.db.models import Q
from django.views.generic import ListView

from .models import med_proteom


class proteom_view(ListView):
    template_name = "proteome.html"
    model = med_proteom

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        self.search_term = query
        if not query:
            return med_proteom.objects.none()

        filters = (
            Q(Plant_Name__icontains=query)
            | Q(Scientific_Name__icontains=query)
            | Q(Protein__icontains=query)
        )
        return med_proteom.objects.filter(filters).order_by("Plant_Name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = getattr(self, "search_term", "")
        context["catalogue"] = (
            med_proteom.objects.all()
            .order_by("Plant_Name")
            .values_list("Plant_Name", "Scientific_Name")
        )
        context["result_count"] = context["object_list"].count()
        return context