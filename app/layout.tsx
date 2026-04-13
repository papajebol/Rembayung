import './globals.css';
import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';
import CartDrawer from '@/components/CartDrawer';

export const metadata: Metadata = {
  title: 'Sandwich App',
  description: 'Simple sandwich ordering app'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="container-page py-6">{children}</main>
        <CartDrawer />
      </body>
    </html>
  );
}
