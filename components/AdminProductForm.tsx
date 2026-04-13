'use client';

import { FormEvent, useState } from 'react';
import ImageUpload from '@/components/ImageUpload';
import { Product } from '@/types/product';

type Props = {
  initial?: Product;
  onSubmit: (data: Product) => void;
};

export default function AdminProductForm({ initial, onSubmit }: Props) {
  const [name, setName] = useState(initial?.name ?? '');
  const [description, setDescription] = useState(initial?.description ?? '');
  const [price, setPrice] = useState(initial?.price ?? 0);
  const [imageUrl, setImageUrl] = useState(initial?.imageUrl ?? '');

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({
      id: initial?.id ?? crypto.randomUUID(),
      name,
      description,
      price,
      imageUrl
    });
  };

  return (
    <form onSubmit={submit} className="card space-y-4">
      <h2 className="text-lg font-semibold">Product Form</h2>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Product name"
        className="w-full rounded-md border border-orange-200 px-3 py-2"
        required
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
        className="w-full rounded-md border border-orange-200 px-3 py-2"
        rows={3}
        required
      />
      <input
        type="number"
        min={0}
        step="0.01"
        value={price}
        onChange={(e) => setPrice(Number(e.target.value))}
        placeholder="Price"
        className="w-full rounded-md border border-orange-200 px-3 py-2"
        required
      />
      <ImageUpload value={imageUrl} onChange={setImageUrl} />
      <button className="rounded-md bg-slate-900 px-4 py-2 text-white hover:bg-slate-700">
        Save Product
      </button>
    </form>
  );
}
