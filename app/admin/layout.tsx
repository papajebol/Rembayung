import Link from 'next/link';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <section>
      <div className="mb-6 flex items-center justify-between rounded-xl border border-orange-200 bg-white p-4">
        <h1 className="text-xl font-bold">Admin Panel</h1>
        <div className="flex gap-2 text-sm">
          <Link href="/admin/products" className="rounded border px-3 py-2 hover:bg-orange-100">
            Products
          </Link>
          <Link href="/" className="rounded border px-3 py-2 hover:bg-orange-100">
            Storefront
          </Link>
        </div>
      </div>
      {children}
    </section>
  );
}
