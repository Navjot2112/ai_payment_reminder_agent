import { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Bell, CalendarDays, ChevronDown, ChevronRight, CircleHelp, FileText, LayoutDashboard, Menu, MoreHorizontal, Plus, Users, WalletCards } from 'lucide-react';
import { createInvoice, fetchInvoices, sendReminder, callInvoice } from './api';
import { AddInvoiceModal } from './components/AddInvoiceModal';
import { ReminderCalendar } from './pages/ReminderCalendar';
import { InvoicesPage } from './pages/InvoicesPage';
import { OverviewPage } from './pages/OverviewPage';
import { CustomersPage } from './pages/CustomersPage';
import { PaymentActivityPage } from './pages/PaymentActivityPage';
import './styles.css';

const nav = [[LayoutDashboard, 'Overview'], [FileText, 'Invoices'], [CalendarDays, 'Reminder calendar'], [Users, 'Customers'], [WalletCards, 'Payment activity']];
const descriptions = { Overview: 'A clear view of every due date and payment conversation.', Invoices: 'Manage invoice details, payment status, and reminders.', 'Reminder calendar': 'A clear view of every due date and payment conversation.', Customers: 'Customers are grouped automatically from your invoice records.', 'Payment activity': 'Track invoice follow-ups and collection activity.' };

function App() {
  const [invoices, setInvoices] = useState([]); const [tab, setTab] = useState('Reminder calendar'); const [modal, setModal] = useState(false); const [toast, setToast] = useState('');
  useEffect(() => { fetchInvoices().then(setInvoices).catch(error => setToast(error.message)); }, []);
  const overdue = useMemo(() => invoices.filter(invoice => invoice.status === 'overdue').length, [invoices]);
  const notify = text => { setToast(text); window.setTimeout(() => setToast(''), 2800); };
  const remind = async (invoice) => {
    try {
      const updated = await sendReminder(invoice.id);

      setInvoices(old =>
        old.map(row => row.id === updated.id ? updated : row)
      );

      notify(`Reminder sent to ${invoice.customer}`);
    } catch (error) {
      notify(error.message);
    }
  };
  const call = async invoice => {
    try {
      const result = await callInvoice(invoice.id);
      notify(result.message);
    } catch (error) {
      notify(error.message);
    }
  };
  const addInvoice = async invoice => { try { const created = await createInvoice(invoice); setInvoices(old => [...old, created]); setModal(false); notify('Invoice added to your workspace'); } catch (error) { notify(error.message); } };
  const view = tab === 'Reminder calendar' ? <ReminderCalendar invoices={invoices} />
    : tab === 'Invoices' ? <InvoicesPage invoices={invoices} onRemind={remind} onCall={call} />
      : tab === 'Customers' ? <CustomersPage invoices={invoices} />
        : tab === 'Payment activity' ? <PaymentActivityPage invoices={invoices} />
          : <OverviewPage invoices={invoices} onRemind={remind} onCall={call} onAdd={() => setModal(true)} />;
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">P</span><span>Pay<span>Flow</span></span></div>
      <div className="workspace"><div className="company-avatar">SI</div><div><b>Sahib Industries</b><small>Workspace</small></div><ChevronDown size={15} /></div>
      <nav>{nav.map(([Icon, label]) => <button key={label} className={tab === label ? 'active' : ''} onClick={() => setTab(label)}><Icon size={18} />{label}{label === 'Reminder calendar' && overdue > 0 && <i>{overdue}</i>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="profile"><div className="avatar">NS</div><div><b>Navjot Singh</b><small>Administrator</small></div><MoreHorizontal size={18} /></div></div>
    </aside>
    <main>
      <header>
        <div className="mobile-menu"><Menu /></div>
        <div className="crumb"><span>Workspace</span><ChevronRight size={15} /><b>{tab}</b></div>
        <div className="top-actions"><button className="icon-btn"><Bell size={19} /><em /></button><button className="help"><CircleHelp size={19} /></button></div>
      </header>
      <section className="content">
        <div className="title-row">
          <div><p className="eyebrow">PAYMENT FOLLOW-UPS</p><h1>{tab}</h1><p className="sub">{descriptions[tab]}</p></div>
          <button className="primary" onClick={() => setModal(true)}><Plus size={18} />Add invoice</button>
        </div>
        {view}
      </section>
    </main>
    {modal && <AddInvoiceModal onClose={() => setModal(false)} onAdd={addInvoice} />}
    {toast && <div className="toast">{toast}</div>}
  </div>;
}
createRoot(document.getElementById('root')).render(<App />);
