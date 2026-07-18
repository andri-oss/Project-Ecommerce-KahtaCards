from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Product
from apps.dashboard.access import dashboard_access_required
from .models import Conversation, Message


def _serialize_message(message, request_user):
    data = {
        'id': message.id,
        'body': message.body,
        'sender': message.sender.username,
        'is_mine': message.sender_id == request_user.id,
        'created_at': message.created_at.strftime('%H:%M'),
        'product': None,
    }
    if message.product_id:
        data['product'] = {
            'id': message.product.id,
            'name': message.product.name,
            'slug': message.product.slug,
            'price': message.product.price,
            'image_url': message.product.image.url if message.product.image else '',
            'url': reverse('catalog:product_detail', args=[message.product.slug]),
        }
    return data


@login_required
def customer_chat_view(request):
    """Buyer-facing chat page — one conversation per customer with the store."""
    conversation, _ = Conversation.objects.get_or_create(customer=request.user)
    messages = conversation.messages.select_related('sender', 'product')
    messages.filter(~Q(sender=request.user), read_at__isnull=True).update(read_at=timezone.now())

    mentioned_product = None
    product_id = request.GET.get('product')
    if product_id:
        mentioned_product = Product.objects.filter(pk=product_id, is_active=True).first()

    return render(request, 'chat/customer_chat.html', {
        'conversation': conversation,
        'messages': messages,
        'mentioned_product': mentioned_product,
    })


@login_required
def customer_chat_send(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    body = request.POST.get('body', '').strip()
    product_id = request.POST.get('product_id')
    product = Product.objects.filter(pk=product_id).first() if product_id else None

    if not body and not product:
        return JsonResponse({'error': 'Pesan tidak boleh kosong.'}, status=400)

    conversation, _ = Conversation.objects.get_or_create(customer=request.user)
    message = Message.objects.create(conversation=conversation, sender=request.user, body=body, product=product)

    return JsonResponse(_serialize_message(message, request.user))


@login_required
def customer_chat_poll(request):
    """Return messages newer than `after` (a message id) for AJAX polling."""
    conversation, _ = Conversation.objects.get_or_create(customer=request.user)
    after_id = request.GET.get('after', 0)

    messages = conversation.messages.select_related('sender', 'product').filter(id__gt=after_id)
    messages.filter(~Q(sender=request.user), read_at__isnull=True).update(read_at=timezone.now())

    return JsonResponse({'messages': [_serialize_message(m, request.user) for m in messages]})


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
    messages = conversation.messages.select_related('sender', 'product')
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
    product_id = request.POST.get('product_id')
    product = Product.objects.filter(pk=product_id).first() if product_id else None

    if not body and not product:
        return JsonResponse({'error': 'Pesan tidak boleh kosong.'}, status=400)

    message = Message.objects.create(conversation=conversation, sender=request.user, body=body, product=product)

    return JsonResponse(_serialize_message(message, request.user))


@dashboard_access_required('chat')
def staff_chat_poll(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    after_id = request.GET.get('after', 0)

    messages = conversation.messages.select_related('sender', 'product').filter(id__gt=after_id)
    messages.filter(sender=conversation.customer, read_at__isnull=True).update(read_at=timezone.now())

    return JsonResponse({'messages': [_serialize_message(m, request.user) for m in messages]})


@login_required
def customer_unread_count(request):
    """Small badge poll for the navbar — how many unread staff replies the customer has."""
    conversation = Conversation.objects.filter(customer=request.user).first()
    if not conversation:
        return JsonResponse({'unread': 0})

    unread = conversation.messages.filter(~Q(sender=request.user), read_at__isnull=True).count()
    return JsonResponse({'unread': unread})
