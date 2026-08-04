const API_BASE = import.meta.env.VITE_API_BASE || '';

async function request(path, options) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.message || 'Something went wrong.');
  return body;
}

export const fetchInvoices = () => request('/api/invoices');
export const createInvoice = invoice => request('/api/invoices', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(invoice)
});
export const sendReminder = id => request(`/api/invoices/${id}/remind`, { method: 'POST' });
export const callInvoice = id => request(`/api/invoices/${id}/call`, { method: "POST" });
export async function extractInvoiceFromImage(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  return request('/api/invoices/extract', { method: 'POST', body: formData });
}
