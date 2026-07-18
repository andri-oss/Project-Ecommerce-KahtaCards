from django.db.models import Q

from .models import Conversation


def chat_context(request):
    """Make the customer's unread staff-reply count available in all templates."""
    count = 0
    if request.user.is_authenticated:
        conversation = Conversation.objects.filter(customer=request.user).first()
        if conversation:
            count = conversation.messages.filter(~Q(sender=request.user), read_at__isnull=True).count()
    return {'chat_unread_count': count}
