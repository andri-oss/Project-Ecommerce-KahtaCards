from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from apps.accounts.models import User
from apps.dashboard.access import dashboard_access_required
from .models import Conversation, Message


@login_required
def customer_chat_view(request):
    """Buyer-facing chat page — one conversation per customer with the store."""
    conversation, _ = Conversation.objects.get_or_create(customer=request.user)
    messages = conversation.messages.select_related('sender')
    messages.filter(~Q(sender=request.user), read_at__isnull=True).update(read_at=timezone.now())

    return render(request, 'chat/customer_chat.html', {
        'conversation': conversation,
        'messages': messages,
    })


@login_required
def customer_chat_send(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    body = request.POST.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'Pesan tidak boleh kosong.'}, status=400)

    conversation, _ = Conversation.objects.get_or_create(customer=request.user)
    message = Message.objects.create(conversation=conversation, sender=request.user, body=body)

    return JsonResponse({
        'id': message.id,
        'body': message.body,
        'sender': message.sender.username,
        'is_mine': True,
        'created_at': message.created_at.strftime('%H:%M'),
    })


@login_required
def customer_chat_poll(request):
    """Return messages newer than `after` (a message id) for AJAX polling."""
    conversation, _ = Conversation.objects.get_or_create(customer=request.user)
    after_id = request.GET.get('after', 0)

    messages = conversation.messages.select_related('sender').filter(id__gt=after_id)
    messages.filter(~Q(sender=request.user), read_at__isnull=True).update(read_at=timezone.now())

    return JsonResponse({
        'messages': [{
            'id': m.id,
            'body': m.body,
            'sender': m.sender.username,
            'is_mine': m.sender_id == request.user.id,
            'created_at': m.created_at.strftime('%H:%M'),
        } for m in messages]
    })


@dashboard_access_required('chat')
def staff_chat_inbox(request):
    """List every customer conversation, most recently active first."""
    search = request.GET.get('q', '')
    conversations = Conversation.objects.select_related('customer').order_by('-updated_at')

    if search:
        conversations = conversations.filter(
            Q(customer__username__icontains=search) |
            Q(customer__email__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search)
        )

    paginator = Paginator(conversations, 15)
    page = paginator.get_page(request.GET.get('page'))

    unread_ids = set(
        Message.objects.filter(read_at__isnull=True)
        .exclude(sender__role__in=[User.Role.ADMIN, User.Role.STAFF])
        .values_list('conversation_id', flat=True)
    )

    return render(request, 'chat/staff_inbox.html', {
        'page_obj': page,
        'search': search,
        'unread_ids': unread_ids,
    })


@dashboard_access_required('chat')
def staff_chat_detail(request, pk):
    conversation = get_object_or_404(Conversation.objects.select_related('customer'), pk=pk)
    messages = conversation.messages.select_related('sender')
    messages.filter(sender=conversation.customer, read_at__isnull=True).update(read_at=timezone.now())

    return render(request, 'chat/staff_detail.html', {
        'conversation': conversation,
        'messages': messages,
    })


@dashboard_access_required('chat')
def staff_chat_send(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    conversation = get_object_or_404(Conversation, pk=pk)
    body = request.POST.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'Pesan tidak boleh kosong.'}, status=400)

    message = Message.objects.create(conversation=conversation, sender=request.user, body=body)

    return JsonResponse({
        'id': message.id,
        'body': message.body,
        'sender': message.sender.username,
        'is_mine': True,
        'created_at': message.created_at.strftime('%H:%M'),
    })


@dashboard_access_required('chat')
def staff_chat_poll(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    after_id = request.GET.get('after', 0)

    messages = conversation.messages.select_related('sender').filter(id__gt=after_id)
    messages.filter(sender=conversation.customer, read_at__isnull=True).update(read_at=timezone.now())

    return JsonResponse({
        'messages': [{
            'id': m.id,
            'body': m.body,
            'sender': m.sender.username,
            'is_mine': m.sender_id == request.user.id,
            'created_at': m.created_at.strftime('%H:%M'),
        } for m in messages]
    })


@login_required
def customer_unread_count(request):
    """Small badge poll for the navbar — how many unread staff replies the customer has."""
    conversation = Conversation.objects.filter(customer=request.user).first()
    if not conversation:
        return JsonResponse({'unread': 0})

    unread = conversation.messages.filter(~Q(sender=request.user), read_at__isnull=True).count()
    return JsonResponse({'unread': unread})
