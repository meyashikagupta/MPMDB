from django.db.models import Q
from django.views.generic import ListView
from django.shortcuts import render
from .models import med_class


class classification_view(ListView):
    template_name = "classification.html"
    model = med_class

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        self.search_term = query
        if not query:
            return med_class.objects.none()

        filters = (
            Q(Plant_Name__icontains=query)
            | Q(Scientific_Name__icontains=query)
            | Q(NCBI_Taxonomy_ID__icontains=query)
            | Q(Family__icontains=query)
            | Q(Genus__icontains=query)
            | Q(Species__icontains=query)
        )
        return med_class.objects.filter(filters).order_by("Plant_Name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = getattr(self, "search_term", "")
        context["catalogue"] = (
            med_class.objects.all()
            .order_by("Plant_Name")
            .values_list("Plant_Name", "Scientific_Name")
        )
        context["result_count"] = context["object_list"].count()
        return context

from django.views.generic import ListView
from django.shortcuts import render
from django.db.models import Q
from .models import med_class

