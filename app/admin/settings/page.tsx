'use client';

import { FormEvent, useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { SettingsRecord } from '@/types/product';

const defaultSettings: SettingsRecord = {
  id: 1,
  whatsapp_number: '',
  order_header: '--- ORDER DETAILS ---',
  order_footer: '---'
};

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState<SettingsRecord>(defaultSettings);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchSettings = async () => {
      setLoading(true);
      const { data, error: fetchError } = await supabase
        .from('settings')
        .select('*')
        .limit(1)
        .maybeSingle();

      if (fetchError) {
        setError(fetchError.message);
      } else if (data) {
        setSettings(data as SettingsRecord);
      }
      setLoading(false);
    };

    fetchSettings();
  }, []);

  const saveSettings = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    const { error: saveError } = await supabase
      .from('settings')
      .upsert(settings, { onConflict: 'id' });

    if (saveError) {
      setError(saveError.message);
    } else {
      setSuccess('Settings saved.');
    }

    setSaving(false);
  };

  return (
    <div className="max-w-2xl card">
      <h1 className="mb-4 text-2xl font-bold">Admin Settings</h1>
      {loading ? (
        <p className="text-sm text-slate-500">Loading settings...</p>
      ) : (
        <form onSubmit={saveSettings} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">WhatsApp Number</label>
            <input
              value={settings.whatsapp_number}
              onChange={(e) => setSettings((prev) => ({ ...prev, whatsapp_number: e.target.value }))}
              className="w-full rounded-md border border-orange-200 px-3 py-2"
              placeholder="60123456789"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Order Header</label>
            <input
              value={settings.order_header}
              onChange={(e) => setSettings((prev) => ({ ...prev, order_header: e.target.value }))}
              className="w-full rounded-md border border-orange-200 px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Order Footer</label>
            <input
              value={settings.order_footer}
              onChange={(e) => setSettings((prev) => ({ ...prev, order_footer: e.target.value }))}
              className="w-full rounded-md border border-orange-200 px-3 py-2"
              required
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          {success && <p className="text-sm text-green-700">{success}</p>}
          <button
            disabled={saving}
            className="rounded-md bg-slate-900 px-4 py-2 text-white disabled:opacity-60"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </form>
      )}
    </div>
  );
}
