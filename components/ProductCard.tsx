'use client';

import { Product } from '@/types/product';
import { formatCurrency } from '@/lib/utils';
import { useCartStore } from '@/lib/cartStore';

type Props = {
  product: Product;
};

export default function ProductCard({ product }: Props) {
  const addItem = useCartStore((state) => state.addItem);
  const openCart = useCartStore((state) => state.openCart);

  return (
    <article className="card flex flex-col">
      <img
        src={product.imageUrl}
        alt={product.name}
        className="h-40 w-full rounded-lg object-cover"
      />
      <h3 className="mt-3 text-lg font-semibold">{product.name}</h3>
      <p className="mt-1 text-sm text-slate-600">{product.description}</p>
      <p className="mt-3 font-bold text-brand-700">{formatCurrency(product.price)}</p>
      <button
        onClick={() => {
          addItem(product);
          openCart();
        }}
        className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
      >
        Add to Cart
      </button>
    </article>
  );
}
