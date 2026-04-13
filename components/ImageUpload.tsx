'use client';

type Props = {
  value: string;
  onChange: (url: string) => void;
};

export default function ImageUpload({ value, onChange }: Props) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium">Image URL</label>
      <input
        type="url"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="https://..."
        className="w-full rounded-md border border-orange-200 px-3 py-2"
      />
    </div>
  );
}
