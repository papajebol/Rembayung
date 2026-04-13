# Sandwich App

A Next.js App Router project for sandwich ordering with a simple admin panel.

## Stack
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- Zustand (cart state)
- Supabase client setup

## Features
- Landing page with product list
- Client-side cart drawer
- Checkout form and WhatsApp order message
- Admin login + product CRUD-style UI

## Getting Started

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Environment Variables

Create `.env.local` if needed:

```bash
NEXT_PUBLIC_SUPABASE_URL=your-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```
