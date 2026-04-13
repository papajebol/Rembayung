'use client';

import { useState } from 'react';
import { supabase } from '@/lib/supabase';

type Props = {
  value: string;
  onChange: (url: string) => void;
};

export default function ImageUpload({ value, onChange }: Props) {
  const [uploading, setUploading] = useState(false);

  const handleFile = async (file: File) => {
    setUploading(true);

    try {
      const safeName = file.name.replace(/\s+/g, '-').toLowerCase();
      const filePath = `products/${Date.now()}-${safeName}`;

      const { error: uploadError } = await supabase.storage.from('products').upload(filePath, file, {
        cacheControl: '3600',
        upsert: false
      });

      if (uploadError) {
        console.error(uploadError);
        alert('Error');
        setUploading(false);
        return;
      }

      const { data } = supabase.storage.from('products').getPublicUrl(filePath);
      onChange(data.publicUrl);
    } catch (error) {
      console.error(error);
      alert('Error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-2">
      <label className="mb-1 block text-sm font-medium">Image</label>
      <input
        type="url"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="https://..."
        className="w-full rounded-md border border-orange-200 px-3 py-2"
      />
      <input
        type="file"
        accept="image/*"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            handleFile(file);
          }
        }}
        className="w-full text-sm"
        disabled={uploading}
      />
      {uploading && <p className="text-xs text-slate-500">Uploading image...</p>}
      {value && <img src={value} alt="Preview" className="h-24 w-24 rounded-md object-cover" />}
    </div>
  );
}
