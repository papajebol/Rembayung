import { Product, ProductRecord } from '@/types/product';

export const formatCurrency = (amount: number) => `RM${amount.toFixed(2)}`;

export const generateOrderId = () => Math.floor(1000 + Math.random() * 9000);

export const toProduct = (record: ProductRecord): Product => ({
  id: record.id,
  name: record.name,
  description: record.description,
  price: Number(record.price),
  imageUrl: record.image_url || 'https://placehold.co/600x400?text=Sandwich'
});
