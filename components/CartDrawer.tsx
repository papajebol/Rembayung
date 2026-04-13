'use client';

import Link from 'next/link';
import { useCartStore } from '@/lib/cartStore';
import { formatCurrency } from '@/lib/utils';

export default function CartDrawer() {
  const { isOpen, closeCart, items, updateQuantity, removeItem, subtotal } = useCartStore();

  return (
    <div className={`fixed inset-0 z-30 ${isOpen ? 'pointer-events-auto' : 'pointer-events-none'}`}>
      <div
        onClick={closeCart}
        className={`absolute inset-0 bg-black/40 transition ${isOpen ? 'opacity-100' : 'opacity-0'}`}
      />

      <aside
        className={`absolute right-0 top-0 h-full w-full max-w-md bg-white p-5 shadow-xl transition-transform ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold">Your Cart</h2>
          <button onClick={closeCart} className="text-sm text-slate-500 hover:text-slate-900">
            Close
          </button>
        </div>

        <div className="space-y-3">
          {items.length === 0 && <p className="text-sm text-slate-500">No items yet.</p>}

          {items.map((item) => (
            <div key={item.product.id} className="rounded-lg border border-orange-100 p-3">
              <p className="font-semibold">{item.product.name}</p>
              <p className="text-sm text-slate-600">{formatCurrency(item.product.price)}</p>
              <div className="mt-2 flex items-center gap-2">
                <button
                  onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                  className="rounded border px-2"
                >
                  -
                </button>
                <span>{item.quantity}</span>
                <button
                  onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                  className="rounded border px-2"
                >
                  +
                </button>
                <button
                  onClick={() => removeItem(item.product.id)}
                  className="ml-auto text-xs text-red-600"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 border-t pt-4">
          <p className="mb-4 flex items-center justify-between font-semibold">
            <span>Subtotal</span>
            <span>{formatCurrency(subtotal())}</span>
          </p>
          <Link
            href="/checkout"
            onClick={closeCart}
            className="block rounded-md bg-brand-600 px-4 py-3 text-center font-semibold text-white hover:bg-brand-700"
          >
            Proceed to Checkout
          </Link>
        </div>
      </aside>
    </div>
  );
}
