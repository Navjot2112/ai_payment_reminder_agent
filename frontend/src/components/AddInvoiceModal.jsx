import { useEffect, useRef, useState } from 'react';
import { Camera, FileScan, FileText, ImageUp, LoaderCircle, Plus, X } from 'lucide-react';
import { extractInvoiceFromImage } from '../api';

const initial = { customer: '', invoiceNo: '', amount: '', dueDate: '', deliveryDate: '', deliveryAddress: '', products: '', phone: '', rawText: '', fileUrl: '' };

export function AddInvoiceModal({ onClose, onAdd }) {
  const [data, setData] = useState(initial); const [source, setSource] = useState('manual'); const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(''); const [busy, setBusy] = useState(false); const [message, setMessage] = useState('');
  const pickerRef = useRef(null); const videoRef = useRef(null); const streamRef = useRef(null);
  const update = (key, value) => setData(old => ({ ...old, [key]: value }));
  const stopCamera = () => { streamRef.current?.getTracks().forEach(track => track.stop()); streamRef.current = null; };
  useEffect(() => () => { stopCamera(); if (preview) URL.revokeObjectURL(preview); }, [preview]);
  const readInvoice = async selected => {
    if (!selected) return; setFile(selected); setPreview(URL.createObjectURL(selected)); setBusy(true); setMessage('Reading invoice details...');
    try { const result = await extractInvoiceFromImage(selected); setData(old => ({ ...old, ...Object.fromEntries(Object.entries(result).filter(([, value]) => value !== '' && value != null)) })); setMessage('Details were suggested from the image. Review them before saving.'); }
    catch (error) { setMessage(error.message || 'Could not read this image. Please complete the fields manually.'); }
    finally { setBusy(false); }
  };
  const openCamera = async () => { setSource('camera'); setMessage(''); try { const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false }); streamRef.current = stream; videoRef.current.srcObject = stream; await videoRef.current.play(); } catch { setMessage('Camera access is unavailable. Upload an image instead.'); } };
  const capture = () => { const video = videoRef.current; if (!video?.videoWidth) return; const canvas = document.createElement('canvas'); canvas.width = video.videoWidth; canvas.height = video.videoHeight; canvas.getContext('2d').drawImage(video, 0, 0); canvas.toBlob(blob => { stopCamera(); setSource('gallery'); readInvoice(new File([blob], 'scanned-invoice.jpg', { type: 'image/jpeg' })); }, 'image/jpeg', 0.92); };
  const submit = async event => { event.preventDefault(); await onAdd({ ...data, amount: Number(data.amount), attachment: file?.name }); };
  return <div className="modal-backdrop"><form className="modal invoice-modal" onSubmit={submit}><button type="button" className="close" onClick={onClose}><X/></button><p className="eyebrow">NEW PAYMENT</p><h2>Add an invoice</h2><p>Scan a photographed invoice, upload an image, or enter the details yourself.</p>
    <input ref={pickerRef} className="hidden-input" accept="image/*" type="file" onChange={event => readInvoice(event.target.files?.[0])}/>
    <div className="source-buttons"><button type="button" className={source === 'camera' ? 'selected' : ''} onClick={openCamera}><Camera size={18}/>Camera</button><button type="button" className={source === 'gallery' ? 'selected' : ''} onClick={() => { stopCamera(); setSource('gallery'); pickerRef.current?.click(); }}><ImageUp size={18}/>Upload</button><button type="button" className={source === 'manual' ? 'selected' : ''} onClick={() => { stopCamera(); setSource('manual'); }}><FileText size={18}/>Manual</button></div>
    {source === 'camera' && <div className="camera-preview"><video ref={videoRef} playsInline muted/><button type="button" onClick={capture}><Camera size={15}/>Capture invoice</button></div>}
    {preview && source !== 'camera' && <div className="file-preview"><img src={preview}/><div><b>{file?.name}</b><span>Image attached to this invoice</span></div><FileScan size={20}/></div>}
    {(busy || message) && <div className={`scan-message ${busy ? 'loading' : ''}`}>{busy ? <LoaderCircle className="spin" size={15}/> : <FileScan size={15}/>} {message}</div>}
    <div className="form-fields"><label>Customer / business name<input required value={data.customer} onChange={e => update('customer', e.target.value)} placeholder="e.g. Acme Traders"/></label><div className="form-row"><label>Invoice number<input required value={data.invoiceNo} onChange={e => update('invoiceNo', e.target.value)} placeholder="INV-006"/></label><label>Total amount<input required min="0" type="number" value={data.amount} onChange={e => update('amount', e.target.value)} placeholder="15000"/></label></div><div className="form-row"><label>Payment due date<input required type="date" value={data.dueDate} onChange={e => update('dueDate', e.target.value)}/></label><label>Customer phone<input value={data.phone} onChange={e => update('phone', e.target.value)} placeholder="+91..."/></label></div><label>Delivery address<textarea value={data.deliveryAddress} onChange={e => update('deliveryAddress', e.target.value)} /></label><label>Products / line items<textarea value={data.products} onChange={e => update('products', e.target.value)} /></label></div><button className="primary submit" disabled={busy}><Plus size={17}/>Save invoice</button>
  </form></div>;
}
