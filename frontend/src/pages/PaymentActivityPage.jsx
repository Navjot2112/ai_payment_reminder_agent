const formatDate = value => value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'No reminders sent';

export function PaymentActivityPage({ invoices }) {
  const activity = invoices.filter(invoice => invoice.reminders || invoice.lastReminderAt || invoice.status === 'paid');
  return <section className="table-card page-table"><div className="section-head"><div><h2>Payment activity</h2><p>A history of reminders and marked payments.</p></div></div>{activity.length ? <div className="activity-list">{activity.map(invoice => <div className="activity-row" key={invoice._id}><div><b>{invoice.customer || 'Unnamed customer'}</b><span>{invoice.status === 'paid' ? 'Payment marked as collected' : `${invoice.reminders || 0} reminder${invoice.reminders === 1 ? '' : 's'} sent`}</span></div><time>{formatDate(invoice.lastReminderAt || invoice.createdAt)}</time></div>)}</div> : <div className="empty-state">Reminder and payment activity will appear here.</div>}</section>;
}
