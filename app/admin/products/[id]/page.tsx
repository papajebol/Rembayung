'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import AdminProductForm from '@/components/AdminProductForm';
import { supabase } from '@/lib/supabase';
import { ProductRecord } from '@/types/product';

export default function AdminEditProductPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [product, setProduct] = useState<ProductRecord | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      const { data, error } = await supabase.from('products').select('*').eq('id', params.id).single();

      if (error) {
        console.error(error);
        alert('Error');
        setLoading(false);
        return;
      }

      setProduct(data as ProductRecord);
      setLoading(false);
    };

    fetchProduct();
  }, [params.id]);

  if (loading) {
    return <p className="text-sm text-slate-500">Loading product...</p>;
  }

  if (!product) {
    return <p className="text-sm text-red-600">Product not found.</p>;
  }

  return (
    <div className="max-w-2xl">
      <h1 className="mb-4 text-2xl font-bold">Edit Product</h1>
      <AdminProductForm
        initial={product}
        onSaved={() => {
          router.push('/admin/products');
        }}
      />
    </div>
  );
}
