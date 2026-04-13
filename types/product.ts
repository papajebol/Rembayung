export type ProductRecord = {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string | null;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
};

export type Product = {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
};

export type CartItem = {
  product: Product;
  quantity: number;
};

export type SettingsRecord = {
  id: number;
  whatsapp_number: string;
  order_header: string;
  order_footer: string;
  updated_at?: string;
};
