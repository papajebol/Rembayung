'use client';

import { useState } from 'react';
import AdminProductForm from '@/components/AdminProductForm';
import AdminProductTable from '@/components/AdminProductTable';

export default function AdminProductsPage() {
  const [refreshToken, setRefreshToken] = useState(0);

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <AdminProductForm onSaved={() => setRefreshToken((v) => v + 1)} />
      <AdminProductTable refreshToken={refreshToken} />
    </div>
  );
}
