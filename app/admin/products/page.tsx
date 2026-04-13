'use client';

import { useState } from 'react';
import AdminProductForm from '@/components/AdminProductForm';
import AdminProductTable from '@/components/AdminProductTable';
import { Product } from '@/types/product';

const starterProducts: Product[] = [
  {
    id: '1',
    name: 'Classic Chicken Sandwich',
    description: 'Grilled chicken and veggies',
    price: 12.9,
    imageUrl: 'https://images.unsplash.com/photo-1481070555726-e2fe8357725c?auto=format&fit=crop&w=600&q=80'
  }
];

export default function AdminProductsPage() {
  const [products, setProducts] = useState<Product[]>(starterProducts);

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <AdminProductForm onSubmit={(p) => setProducts((prev) => [p, ...prev])} />
      <AdminProductTable products={products} />
    </div>
  );
}
