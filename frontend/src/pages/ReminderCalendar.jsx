import { CalendarDays, Clock3, CreditCard, WalletCards } from 'lucide-react';
import { StatCard } from '../components/StatCard';

const money = value => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value || 0);
const dateValue = invoice => invoice.dueDate || invoice.due_date;

export function ReminderCalendar({ invoices }) {
  const today = new Date();
  const outstanding = invoices.filter(inv => inv.status !== 'paid').reduce((sum, inv) => sum + Number(inv.amount || 0), 0);
  const overdueCount = invoices.filter(inv => dateValue(inv) && new Date(`${dateValue(inv)}T23:59:59`) < today && inv.status !== 'paid').length;
  const collectedThisMonth = invoices.filter(inv => { const value = dateValue(inv); if (inv.status !== 'paid' || !value) return false; const due = new Date(`${value}T12:00:00`); return due.getMonth() === today.getMonth() && due.getFullYear() === today.getFullYear(); }).reduce((sum, inv) => sum + Number(inv.amount || 0), 0);
  const promiseCount = invoices.filter(inv => inv.status === 'promise').length;
  const days = Array.from({ length: 7 }, (_, offset) => { const date = new Date(today); date.setDate(today.getDate() - today.getDay() + 1 + offset); return date; });
  return <><div className="stat-grid"><StatCard icon={<CreditCard/>} label="Outstanding" value={money(outstanding)} note="Across unpaid invoices" tone="coral"/><StatCard icon={<Clock3/>} label="Overdue invoices" value={overdueCount} note="Needs attention" tone="orange"/><StatCard icon={<CalendarDays/>} label="Payment promises" value={promiseCount} note="Awaiting customer payment" tone="purple"/><StatCard icon={<WalletCards/>} label="Collected this month" value={money(collectedThisMonth)} note="Invoices marked as paid" tone="mint"/></div>
    <section className="calendar-card"><div className="calendar-head"><div><h2>{today.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}</h2><p>Plan and track reminder activity</p></div><div className="calendar-controls"><button>Today</button><button className="selected">Week</button></div></div><div className="calendar-scroll"><div className="calendar-grid"><div className="time-col"><div></div>{['8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM'].map(time => <div key={time}>{time}</div>)}</div>{days.map(day => <div className="day-col" key={day.toISOString()}><div className="day-head"><span>{day.toLocaleDateString('en-IN', { weekday: 'short' })}</span><b>{day.getDate()}</b></div>{Array.from({ length: 6 }, (_, i) => <div className="slot" key={i}/>)}</div>)}</div></div><div className="legend"><span><i className="dot red"/>Overdue</span><span><i className="dot violet"/>Promise to pay</span><span><i className="dot green"/>Upcoming</span></div></section></>;
}
