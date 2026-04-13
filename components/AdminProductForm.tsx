'use client';

import { FormEvent, useState } from 'react';
import ImageUpload from '@/components/ImageUpload';
import { ProductRecord } from '@/types/product';
import { supabase } from '@/lib/supabase';

type Props = {
  initial?: ProductRecord;
  onSaved?: () => void;
};

export default function AdminProductForm({ initial, onSaved }: Props) {
  const [name, setName] = useState(initial?.name ?? '');
  const [description, setDescription] = useState(initial?.description ?? '');
  const [price, setPrice] = useState(initial?.price ?? 0);
  const [imageUrl, setImageUrl] = useState(initial?.image_url ?? '');
  const [saving, setSaving] = useState(false);

  const resetForm = () => {
    setName('');
    setDescription('');
    setPrice(0);
    setImageUrl('');
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      if (initial?.id) {
        const { error } = await supabase
          .from('products')
          .update({ name, description, price, image_url: imageUrl })
          .eq('id', initial.id);

        if (error) {
          console.error(error);
          alert('Error');
          return;
        }
      } else {
        const { error } = await supabase
          .from('products')
          .insert({ name, description, price, image_url: imageUrl });

        if (error) {
          console.error(error);
          alert('Error');
          return;
        }

        resetForm();
      }

      onSaved?.();
    } catch (error) {
      console.error(error);
      alert('Error');
    } finally {
      setSaving(false);
    }
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
      <button
        disabled={saving}
        className="rounded-md bg-slate-900 px-4 py-2 text-white hover:bg-slate-700 disabled:opacity-60"
      >
        {saving ? 'Saving...' : initial ? 'Update Product' : 'Save Product'}
      </button>
    </form>
  );
}
