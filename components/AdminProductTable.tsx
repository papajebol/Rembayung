'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { ProductRecord } from '@/types/product';
import { formatCurrency } from '@/lib/utils';
import { supabase } from '@/lib/supabase';

type Props = {
  refreshToken: number;
};

export default function AdminProductTable({ refreshToken }: Props) {
  const [products, setProducts] = useState<ProductRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProducts = async () => {
    setLoading(true);
    const { data, error } = await supabase.from('products').select('*').order('created_at', { ascending: false });

    if (error) {
      console.error(error);
      alert('Error');
      setLoading(false);
      return;
    }

    setProducts((data || []) as ProductRecord[]);
    setLoading(false);
  };

  useEffect(() => {
    fetchProducts();
  }, [refreshToken]);

  const deleteProduct = async (id: string) => {
    const { error } = await supabase.from('products').delete().eq('id', id);
    if (error) {
      console.error(error);
      alert('Error');
      return;
    }
    fetchProducts();
  };

  return (
    <div className="card overflow-x-auto">
      {loading && <p className="mb-2 text-sm text-slate-500">Loading products...</p>}
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
                <div className="flex gap-2">
                  <Link
                    href={`/admin/products/${product.id}`}
                    className="rounded border px-2 py-1 text-xs hover:bg-orange-100"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={() => deleteProduct(product.id)}
                    className="rounded border border-red-300 px-2 py-1 text-xs text-red-700 hover:bg-red-50"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
