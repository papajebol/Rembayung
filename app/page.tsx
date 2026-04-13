import ProductCard from '@/components/ProductCard';
import { supabase } from '@/lib/supabase';
import { toProduct } from '@/lib/utils';
import { ProductRecord } from '@/types/product';

export default async function HomePage() {
  const { data, error } = await supabase
    .from('products')
    .select('*')
    .eq('is_active', true)
    .order('created_at', { ascending: false });

  const products = ((data || []) as ProductRecord[]).map(toProduct);

  return (
    <section>
      <h1 className="mb-6 text-3xl font-bold text-brand-700">Freshly Made Sandwiches</h1>
      {error && <p className="mb-4 text-sm text-red-600">Failed to load products: {error.message}</p>}
      {!error && products.length === 0 && (
        <p className="mb-4 text-sm text-slate-600">No active products available right now.</p>
      )}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
