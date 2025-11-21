from django.db.models import Q
from django.views.generic import ListView

from .models import med_transcriptom


class transcriptom_view(ListView):
    template_name = "transcriptom.html"
    model = med_transcriptom

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        self.search_term = query
        if not query:
            return med_transcriptom.objects.none()

        filters = (
            Q(Plant_Name__icontains=query)
            | Q(Scientific_Name__icontains=query)
            | Q(SRA__icontains=query)
            | Q(BioProject__icontains=query)
            | Q(BioSample__icontains=query)
        )
        return med_transcriptom.objects.filter(filters).order_by("Plant_Name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = getattr(self, "search_term", "")
        context["catalogue"] = (
            med_transcriptom.objects.all()
            .order_by("Plant_Name")
            .values_list("Plant_Name", "Scientific_Name")
        )
        context["result_count"] = context["object_list"].count()
        return context