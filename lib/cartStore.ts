'use client';

import { create } from 'zustand';
import { CartItem, Product } from '@/types/product';

type CartState = {
  isOpen: boolean;
  items: CartItem[];
  openCart: () => void;
  closeCart: () => void;
  addItem: (product: Product) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  subtotal: () => number;
};

export const useCartStore = create<CartState>((set, get) => ({
  isOpen: false,
  items: [],
  openCart: () => set({ isOpen: true }),
  closeCart: () => set({ isOpen: false }),
  addItem: (product) => {
    const existing = get().items.find((item) => item.product.id === product.id);
    if (existing) {
      set({
        items: get().items.map((item) =>
          item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        )
      });
      return;
    }

    set({ items: [...get().items, { product, quantity: 1 }] });
  },
  removeItem: (productId) =>
    set({ items: get().items.filter((item) => item.product.id !== productId) }),
  updateQuantity: (productId, quantity) => {
    if (quantity <= 0) {
      get().removeItem(productId);
      return;
    }

    set({
      items: get().items.map((item) =>
        item.product.id === productId ? { ...item, quantity } : item
      )
    });
  },
  clearCart: () => set({ items: [] }),
  subtotal: () =>
    get().items.reduce((sum, item) => sum + item.product.price * item.quantity, 0)
}));
