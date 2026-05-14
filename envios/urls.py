from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views, views_cbv

app_name = 'envios'

urlpatterns = [
    path('', login_required(views.dashboard), name='dashboard'),
    path('lista/', login_required(views.encomienda_lista), name='lista'),
    path('crear/', login_required(views.encomienda_crear), name='crear'),
    path('<int:pk>/', login_required(views.encomienda_detalle), name='detalle'),
    path('<int:pk>/cambiar-estado/', login_required(views.encomienda_cambiar_estado), name='cambiar_estado'),
    path('<int:pk>/estado-json/', login_required(views.encomienda_estado_json), name='encomienda_estado_json'),
    path('<int:pk>/eliminar/', login_required(views.eliminar_encomienda), name='eliminar_encomienda'),
    # CBV URLs
    path('cbv/', login_required(views_cbv.EncomiendaListView.as_view()), name='cbv_lista'),
    path('cbv/<int:pk>/', login_required(views_cbv.EncomiendaDetailView.as_view()), name='cbv_detalle'),
    path('cbv/crear/', login_required(views_cbv.EncomiendaCreateView.as_view()), name='cbv_crear'),
    path('cbv/<int:pk>/editar/', login_required(views_cbv.EncomiendaUpdateView.as_view()), name='cbv_editar'),
]
