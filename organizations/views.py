from django.views.generic.base import TemplateView

class BaseOrganizationView(TemplateView):
    template_name = 'organizations/base.html'

    def get_context_data(self, **kwargs):
        ctx = super(BaseProfileView, self).get_context_data(**kwargs)

        ctx.update({
            
        })
        return ctx
