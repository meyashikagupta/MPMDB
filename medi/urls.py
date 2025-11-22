"""
URL configuration for medi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from phytochem.views import phytochem_view
from geno.views import geno_view
from transcriptom.views import transcriptom_view
from basic.views import basic_view
from proteom.views import proteom_view
from classification.views import classification_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
<<<<<<< HEAD
from pages.views import home_view ,intro_view, aloevera_view , amla_view , ashwagandha_view , babool_view , bhringraj_view , cinnamon_view , clove_view , cumin_view , curry_view , eucalyptus_view , ginger_view , lavender_view , mehndi_view , neem_view , peppermint_view , tulsi_view , turmeric_view, plantbot_view, plantbot_api 
=======
from pages.views import home_view ,intro_view, aloevera_view , amla_view , ashwagandha_view , babool_view , bhringraj_view , cinnamon_view , clove_view , cumin_view , curry_view , eucalyptus_view , ginger_view , lavender_view , mehndi_view , neem_view , peppermint_view , tulsi_view , turmeric_view 
>>>>>>> b0548c3294d8b00c66890a6c51f462e421424374


urlpatterns = [
    path('admin/', admin.site.urls),
    path ('home.html', home_view ,name="home"),
    path('intro.html', intro_view, name="intro"),
    path('classification.html',classification_view.as_view(), name="classification"),
    path('basic.html', basic_view.as_view(), name="basic"),
    path('genomes.html', geno_view.as_view(), name="genomes"),
    path('proteome.html', proteom_view.as_view(), name="proteom"),
   path('metabolites.html', phytochem_view.as_view(), name="metabolites"),
    path('transcriptom.html', transcriptom_view.as_view(), name="transcriptom"),
    path('aloevera.html', aloevera_view, name="aloevera"),
    path('amla.html', amla_view, name="amla"),
    path('ashwagandha.html', ashwagandha_view, name="ashwagandha"),
    path('babool.html', babool_view, name="babool"),
    path('bhringraj.html', bhringraj_view, name="bhringraj"),
    path('cinnamon.html', cinnamon_view, name="cinnamon"),
    path('clove.html', clove_view, name="clove"),
    path('cumin.html', cumin_view, name="cumin"),
    path('curry.html', curry_view, name="curry"),
    path('eucalyptus.html', eucalyptus_view, name="eucalyptus"),
    path('ginger.html', ginger_view, name="ginger"),
    path('lavender.html', lavender_view, name="lavender"),
    path('mehndi.html', mehndi_view, name="mehndi"),
    path('neem.html', neem_view, name="neem"),
    path('peppermint.html', peppermint_view, name="peppermint"),
    path('tulsi.html', tulsi_view, name="tulsi"),
    path('turmeric.html', turmeric_view, name="turmeric"),
<<<<<<< HEAD
    path('plantbot.html', plantbot_view, name="plantbot"),
    path('api/plantbot/', plantbot_api, name="plantbot_api"),
=======
>>>>>>> b0548c3294d8b00c66890a6c51f462e421424374
    path('home/', home_view , name='home'),
    path('intro/',intro_view ,name='intro'),
    path('basic/',basic_view.as_view() ,name='basic'),
    path('basic/',classification_view.as_view() ,name='classification'),
    path('basic/',geno_view.as_view(),name='genomes'),
    path('basic/',proteom_view.as_view(),name='proteom'),
    path('basic/',phytochem_view.as_view() ,name='metabolites'),
    path('basic/',transcriptom_view.as_view(),name='transcriptom'),
    path('home/intro.html',intro_view,name='intro'),
    path('home/home.html',home_view,name='home'),
    path('home/classification.html',classification_view.as_view(),name='classification'),
    path('home/genomes.html',geno_view.as_view(),name='genomes'),
    path('home/proteome.html',proteom_view.as_view(), name='proteom'),
   path('home/metabolites.html',phytochem_view.as_view(),name='metabolites'),
    path('home/basic.html',basic_view.as_view(), name='basic'),
    path('home/transcriptom.html',transcriptom_view.as_view(), name='transcriptom'),

    path('',home_view)

] 

urlpatterns += staticfiles_urlpatterns()