'use client';

import Link from 'next/link';
import { Product } from '@/types/product';
import { formatCurrency } from '@/lib/utils';

type Props = {
  products: Product[];
};

export default function AdminProductTable({ products }: Props) {
  return (
    <div className="card overflow-x-auto">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr className="border-b border-orange-200">
            <th className="py-2">Name</th>
            <th className="py-2">Price</th>
            <th className="py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id} className="border-b border-orange-100">
              <td className="py-3">{product.name}</td>
              <td className="py-3">{formatCurrency(product.price)}</td>
              <td className="py-3">
                <Link
                  href={`/admin/products/${product.id}`}
                  className="rounded border px-2 py-1 text-xs hover:bg-orange-100"
                >
                  Edit
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
