'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import AdminProductForm from '@/components/AdminProductForm';
import { Product } from '@/types/product';

export default function AdminEditProductPage() {
  const params = useParams<{ id: string }>();
  const [saved, setSaved] = useState(false);

  const mockProduct: Product = {
    id: params.id,
    name: 'Sample Product',
    description: 'Update this product information.',
    price: 10,
    imageUrl: 'https://images.unsplash.com/photo-1481070555726-e2fe8357725c?auto=format&fit=crop&w=600&q=80'
  };

  return (
    <div className="max-w-2xl">
      <h1 className="mb-4 text-2xl font-bold">Edit Product #{params.id}</h1>
      <AdminProductForm
        initial={mockProduct}
        onSubmit={() => {
          setSaved(true);
        }}
      />
      {saved && <p className="mt-3 text-sm font-medium text-green-700">Product saved (UI only).</p>}
    </div>
  );
}
