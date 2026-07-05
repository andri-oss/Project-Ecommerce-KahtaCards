import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from apps.orders.models import Order
from apps.payments.models import Payment

@csrf_exempt
def midtrans_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        transaction_status = data.get('transaction_status')
        fraud_status = data.get('fraud_status')

        if not order_id:
            return JsonResponse({'error': 'Missing order_id'}, status=400)

        try:
            order = Order.objects.get(order_id=order_id)
            payment = order.payment
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)

        # Midtrans status mapping
        if transaction_status == 'capture':
            if fraud_status == 'challenge':
                payment.status = Payment.Status.PENDING
            elif fraud_status == 'accept':
                payment.status = Payment.Status.COMPLETED
                payment.paid_at = timezone.now()
                order.status = Order.Status.PAID
        elif transaction_status == 'settlement':
            payment.status = Payment.Status.COMPLETED
            payment.paid_at = timezone.now()
            order.status = Order.Status.PAID
        elif transaction_status in ['cancel', 'deny', 'expire']:
            payment.status = Payment.Status.FAILED if transaction_status in ['cancel', 'deny'] else Payment.Status.EXPIRED
            if order.status == Order.Status.PENDING:
                order.status = Order.Status.CANCELLED
        elif transaction_status == 'pending':
            payment.status = Payment.Status.PENDING

        payment.save()
        order.save()

        return JsonResponse({'status': 'ok'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
