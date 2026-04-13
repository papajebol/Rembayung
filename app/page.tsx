import ProductCard from '@/components/ProductCard';
import { Product } from '@/types/product';

const products: Product[] = [
  {
    id: '1',
    name: 'Classic Chicken Sandwich',
    description: 'Grilled chicken, lettuce, tomato, and signature sauce.',
    price: 12.9,
    imageUrl:
      'https://images.unsplash.com/photo-1481070555726-e2fe8357725c?auto=format&fit=crop&w=1200&q=80'
  },
  {
    id: '2',
    name: 'Beef Cheese Melt',
    description: 'Juicy beef patty with cheddar and caramelized onions.',
    price: 15.5,
    imageUrl:
      'https://images.unsplash.com/photo-1550317138-10000687a72b?auto=format&fit=crop&w=1200&q=80'
  },
  {
    id: '3',
    name: 'Veggie Delight',
    description: 'Fresh vegetables, avocado, and herbed cream spread.',
    price: 11.75,
    imageUrl:
      'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?auto=format&fit=crop&w=1200&q=80'
  }
];

export default function HomePage() {
  return (
    <section>
      <h1 className="mb-6 text-3xl font-bold text-brand-700">Freshly Made Sandwiches</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
