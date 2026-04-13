import { CartItem } from '@/types/product';
import { formatCurrency, generateOrderId } from '@/lib/utils';

type CheckoutPayload = {
  name: string;
  address: string;
  date: string;
  delivery: boolean;
};

export const buildWhatsAppMessage = (items: CartItem[], payload: CheckoutPayload) => {
  const subtotal = items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  const orderId = generateOrderId();

  const itemsText = items
    .map((item, idx) => `${idx + 1}. ${item.product.name} x${item.quantity}`)
    .join('\n');

  const message = `--- ORDER DETAILS ---\n\nOrder ID: #${orderId}\n\nItems:\n${itemsText}\n\nSubtotal: ${formatCurrency(subtotal)}\n\nDelivery: ${payload.delivery ? 'Yes' : 'No'}\nAlamat: ${payload.address || '-'}\n\nTarikh: ${payload.date}\n\nNama: ${payload.name}\n\n---`;

  return encodeURIComponent(message);
};

export const createWhatsAppLink = (phone: string, encodedMessage: string) =>
  `https://wa.me/${phone}?text=${encodedMessage}`;
