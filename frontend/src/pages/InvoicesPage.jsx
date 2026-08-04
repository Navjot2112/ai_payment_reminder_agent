import { InvoiceTable } from '../components/InvoiceTable';
export function InvoicesPage({ invoices, onRemind, onCall }) {
    return <section className="table-card page-table">
        <div className="section-head">
            <div><h2>All invoices</h2><p>Review payment status, due dates, and reminder activity.</p></div>
            <b>{invoices.length} total</b>
        </div>
        <InvoiceTable invoices={invoices} onRemind={onRemind} onCall={onCall} />
    </section>;
}