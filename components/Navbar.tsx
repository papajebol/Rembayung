'use client';

import Link from 'next/link';
import { useCartStore } from '@/lib/cartStore';

export default function Navbar() {
  const openCart = useCartStore((state) => state.openCart);
  const items = useCartStore((state) => state.items);
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <header className="sticky top-0 z-20 border-b border-orange-200 bg-white/95 backdrop-blur">
      <div className="container-page flex h-16 items-center justify-between">
        <Link href="/" className="text-lg font-bold text-brand-700">
          Sandwich App
        </Link>

        <div className="flex items-center gap-2">
          <Link
            href="/admin/login"
            className="rounded-md border border-orange-200 px-3 py-2 text-sm font-medium hover:bg-orange-100"
          >
            Admin
          </Link>
          <button
            onClick={openCart}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
          >
            Cart ({itemCount})
          </button>
        </div>
      </div>
    </header>
  );
}
