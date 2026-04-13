export type Product = {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  category?: string;
  stock?: number;
};

export type CartItem = {
  product: Product;
  quantity: number;
};
