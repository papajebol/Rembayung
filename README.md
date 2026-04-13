# Sandwich App

A Next.js App Router project for sandwich ordering with a working Supabase-backed admin panel and checkout flow.

## Stack
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- Zustand (cart state)
- Supabase (DB + Storage)

## Features
- Landing page reads active products from Supabase
- Client-side cart drawer
- Checkout form generates WhatsApp message using settings from Supabase
- WhatsApp message includes order timestamp in Malaysia time
- Admin product CRUD (create, update, delete, active toggle)
- Admin image upload to Supabase Storage bucket `products`
- Admin settings page to update WhatsApp number/header/footer

## Getting Started

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=your-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```
