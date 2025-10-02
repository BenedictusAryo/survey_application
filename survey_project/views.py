from django.views.generic import TemplateView
from forms.models import Form
from master_data.models import MasterDataSet
from responses.models import Response


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'is_form_creator') and self.request.user.is_form_creator:
            # Get statistics for form creators
            context['total_datasets'] = MasterDataset.objects.filter(created_by=self.request.user).count()
            context['total_forms'] = Form.objects.filter(created_by=self.request.user).count()
            context['total_responses'] = Response.objects.filter(form__created_by=self.request.user).count()
        
        return context
