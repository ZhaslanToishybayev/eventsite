from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse

class IndexView(generic.TemplateView):
    """
    View for displaying the main page of the site.

    This class displays the main page, including top-16 clubs, nearest 16 events, and 3 services for clubs.

    Attributes:
        template_name (str): Path to the main page template.
    """

    template_name = 'clubs/index.html'

    def get_context_data(self, **kwargs):
        """
        Adds additional context to the main page.

        Context includes:
        - Top-16 clubs, sorted by member count and like count.
        - Nearest 16 events, sorted by start date.
        - 3 services for clubs, sorted by creation date.

        Parameters:
            **kwargs: Additional arguments for the context.

        Returns:
            dict: Context for rendering the main page template.
        """
        context = super().get_context_data(**kwargs)

        # Temporarily disable database queries to test template
        try:
            context['top_16_clubs'] = []
            context['nearest_16_events'] = []
            context['services'] = []
        except Exception as e:
            context['top_16_clubs'] = []
            context['nearest_16_events'] = []
            context['services'] = []

        return context