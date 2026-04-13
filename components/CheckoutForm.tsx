'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useCartStore } from '@/lib/cartStore';
import { buildWhatsAppMessage, createWhatsAppLink } from '@/lib/whatsapp';
import { formatCurrency } from '@/lib/utils';
import { supabase } from '@/lib/supabase';

export default function CheckoutForm() {
  const items = useCartStore((state) => state.items);
  const subtotal = useCartStore((state) => state.subtotal)();
  const clearCart = useCartStore((state) => state.clearCart);

  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [date, setDate] = useState('');
  const [delivery, setDelivery] = useState(true);
  const [whatsAppNumber, setWhatsAppNumber] = useState('');

  useEffect(() => {
    const loadSettings = async () => {
      const { data, error } = await supabase
        .from('settings')
        .select('whatsapp_number')
        .limit(1)
        .single();

      if (error) {
        console.error(error);
        return;
      }

      setWhatsAppNumber(data.whatsapp_number || '');
    };

    loadSettings();
  }, []);

  const isDisabled = useMemo(
    () => !name || !date || items.length === 0 || !whatsAppNumber,
    [name, date, items.length, whatsAppNumber]
  );

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const encoded = buildWhatsAppMessage(items, { name, address, date, delivery });
    const link = createWhatsAppLink(whatsAppNumber, encoded);
    window.open(link, '_blank');
    clearCart();
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <form onSubmit={handleSubmit} className="card space-y-4">
        <h1 className="text-2xl font-bold">Checkout</h1>

        <div>
          <label className="mb-1 block text-sm font-medium">Nama</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-md border border-orange-200 px-3 py-2"
            required
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Tarikh</label>
          <input
            type="text"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full rounded-md border border-orange-200 px-3 py-2"
            placeholder="15 April"
            required
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Alamat</label>
          <textarea
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            className="w-full rounded-md border border-orange-200 px-3 py-2"
            rows={3}
          />
        </div>

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={delivery}
            onChange={(e) => setDelivery(e.target.checked)}
          />
          Delivery
        </label>

        {!whatsAppNumber && (
          <p className="text-sm text-red-600">WhatsApp number is not configured in settings.</p>
        )}

        <button
          disabled={isDisabled}
          className="w-full rounded-md bg-brand-600 px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send via WhatsApp
        </button>
      </form>

      <div className="card h-fit">
        <h2 className="text-lg font-semibold">Order Summary</h2>
        <div className="mt-3 space-y-2 text-sm">
          {items.map((item) => (
            <p key={item.product.id} className="flex justify-between">
              <span>
                {item.product.name} x{item.quantity}
              </span>
              <span>{formatCurrency(item.product.price * item.quantity)}</span>
            </p>
          ))}
        </div>
        <p className="mt-4 border-t pt-3 font-semibold">Subtotal: {formatCurrency(subtotal)}</p>
      </div>
    </div>
  );
}
