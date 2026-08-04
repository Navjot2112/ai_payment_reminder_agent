const money = value => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value || 0);

export function CustomersPage({ invoices }) {
  const customers = Object.values(invoices.reduce((all, invoice) => {
    const name = invoice.customer || 'Unnamed customer';
    const customer = all[name] || { name, invoices: 0, outstanding: 0 };
    customer.invoices += 1;
    if (invoice.status !== 'paid') customer.outstanding += Number(invoice.amount || 0);
    all[name] = customer;
    return all;
  }, {}));
  return <section className="table-card page-table"><div className="section-head"><div><h2>Customers</h2><p>Payment exposure grouped by customer.</p></div><b>{customers.length} total</b></div>{customers.length ? <div className="customer-list">{customers.map(customer => <div className="customer-row" key={customer.name}><div className="customer-icon">{customer.name.split(' ').map(word => word[0]).slice(0, 2).join('')}</div><b>{customer.name}</b><span>{customer.invoices} invoice{customer.invoices !== 1 ? 's' : ''}</span><strong>{money(customer.outstanding)}</strong></div>)}</div> : <div className="empty-state">Customers will appear here when you add invoices.</div>}</section>;
}
