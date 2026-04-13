'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (email && password) {
      router.push('/admin/products');
    }
  };

  return (
    <div className="mx-auto mt-20 max-w-md card">
      <h1 className="mb-4 text-2xl font-bold">Admin Login</h1>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          className="w-full rounded-md border border-orange-200 px-3 py-2"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="w-full rounded-md border border-orange-200 px-3 py-2"
          required
        />
        <button className="w-full rounded-md bg-slate-900 px-4 py-2 font-semibold text-white">
          Sign In
        </button>
      </form>
    </div>
  );
}
