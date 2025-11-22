<<<<<<< HEAD
from django.db.models import Q
from django.views.generic import ListView

from .models import med_geno


class geno_view(ListView):
    template_name = "genomes.html"
    model = med_geno

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        self.search_term = query
        if not query:
            return med_geno.objects.none()

        filters = (
            Q(Plant_Name__icontains=query)
            | Q(Scientific_Name__icontains=query)
            | Q(Nucleotide__icontains=query)
        )
        return med_geno.objects.filter(filters).order_by("Plant_Name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = getattr(self, "search_term", "")
        context["catalogue"] = (
            med_geno.objects.all()
            .order_by("Plant_Name")
            .values_list("Plant_Name", "Scientific_Name")
        )
        context["result_count"] = context["object_list"].count()
        return context
=======
from django.views.generic import ListView
from django.shortcuts import render
from django.db.models import Q
from .models import med_geno

#genome_view
class geno_view(ListView):
    template_name= "genomes.html"

    def get_queryset(self):
        query = self.request.GET.get("q", default=".")
        object_list = med_geno.objects.filter(Q(Plant_Name=query))
        return object_list

>>>>>>> b0548c3294d8b00c66890a6c51f462e421424374
