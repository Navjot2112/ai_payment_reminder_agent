import { Send, Phone } from 'lucide-react';

const labels = { overdue: ['Overdue', 'red'], promise: ['Promise to pay', 'violet'], pending: ['Follow-up', 'amber'], upcoming: ['Upcoming', 'green'], paid: ['Paid', 'green'] };
const money = value => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value || 0);
const date = value => value ? new Date(`${value}T12:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : 'Not set';

export function InvoiceTable({ invoices, onRemind, onCall, limit }) {
  const rows = limit ? invoices.slice(0, limit) : invoices;
  if (!rows.length) return <div className="empty-state">No invoices yet. Add one manually or scan an image to get started.</div>;
  return <div className="invoice-list">{rows.map(invoice => {
    const [label, tone] = labels[invoice.status] || labels.upcoming;
    return <div className="invoice-row" key={invoice.id}>
      <div className="customer-icon">{(invoice.customer || '?').split(' ').map(word => word[0]).slice(0, 2).join('')}</div>
      <div className="invoice-name"><b>{invoice.customer || 'Unnamed customer'}</b><span>{invoice.invoiceNo || 'No invoice number'} · Due {date(invoice.dueDate || invoice.due_date)}</span></div>
      <strong>{money(invoice.amount)}</strong>
      <span className={`status ${tone}`}><i></i>{label}</span>
      {invoice.status !== 'paid' && (
        <div style={{ display: 'flex', gap: '6px' }}>
          <button className="remind" onClick={() => onRemind(invoice)}><Send size={14} />Remind</button>
          <button className="remind" onClick={() => onCall(invoice)}><Phone size={14} />Call</button>
        </div>
      )}
    </div>;
  })}</div>;
}