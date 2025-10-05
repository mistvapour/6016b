import React, { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Search, RefreshCw, Gauge, ChartBar, Link2, ShieldAlert, Database, Loader2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Table, TableHeader, TableHead, TableRow, TableBody, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";

const API_BASE = (import.meta as any)?.env?.VITE_API_BASE || "http://localhost:8000";
async function jsonFetch<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
const fileUrl = (path: string) => `${API_BASE}${path}`;

interface Spec { spec_id: number; code: string; edition: string; part_label: string | null }
interface Message { message_id: number; j_series: string; spec_id?: number }

function SectionTitle({ icon: Icon, children }: { icon: any; children: React.ReactNode }) {
  return (<div className="flex items-center gap-2 text-lg font-semibold"><Icon className="h-5 w-5" /><span>{children}</span></div>);
}
function LoadingInline(){ return <span className="inline-flex items-center text-sm text-muted-foreground gap-2"><Loader2 className="h-4 w-4 animate-spin" /> Loading…</span> }

function BindDialog({ fieldId }: { fieldId: number }) {
  const [open, setOpen] = useState(false);
  const [concept, setConcept] = useState("");
  const [conf, setConf] = useState(0.95);
  const [busy, setBusy] = useState(false);
  async function onBind(){
    setBusy(true);
    try{
      await jsonFetch("/api/bind/field", { method:"POST", body: JSON.stringify({ concept, field_id: fieldId, confidence: conf }) });
      alert("Bound successfully");
      setOpen(false);
    }catch(e:any){ alert(e.message || String(e)); }
    finally{ setBusy(false); }
  }
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild><Button variant="outline" size="sm"><Link2 className="h-4 w-4 mr-1"/>Bind</Button></DialogTrigger>
      <DialogContent>
        <DialogHeader><DialogTitle>Bind field #{fieldId}</DialogTitle></DialogHeader>
        <div className="space-y-3">
          <Input placeholder="Concept name" value={concept} onChange={(e)=>setConcept(e.target.value)} />
          <div className="flex items-center gap-2">
            <Input type="number" step="0.01" value={conf} onChange={(e)=>setConf(parseFloat(e.target.value))} className="w-32" />
            <Badge variant="secondary">confidence</Badge>
          </div>
          <div className="flex justify-end gap-2">
            <Button onClick={()=>setOpen(false)} variant="secondary">Cancel</Button>
            <Button onClick={onBind} disabled={!concept || busy}>{busy? <LoadingInline/> : "Bind"}</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function QuickActions(){
  const [busy,setBusy] = useState(false);
  async function refresh(){ setBusy(true); try{ await jsonFetch("/api/exports/refresh",{method:"POST"}); alert("Exports refreshed"); }catch(e:any){ alert(e.message||String(e)); }finally{ setBusy(false);} }
  async function audit(){ setBusy(true); try{ const d = await jsonFetch<any>("/api/audit/quick"); const gaps=d.gaps?.length||0; const noDI=(d.no_data_item_fields||[]).reduce((a:number,r:any)=>a+(r.fields_no_data_item||0),0); const conf=(d.conflicts||[]).length; alert(`Gaps: ${gaps}\nFields without DI: ${noDI}\nConflict rows: ${conf}`);}catch(e:any){ alert(e.message||String(e)); }finally{ setBusy(false);} }
  return (<div className="flex gap-2"><Button onClick={refresh} disabled={busy}><RefreshCw className="h-4 w-4 mr-2"/>Refresh Exports</Button><Button onClick={audit} variant="secondary"><ShieldAlert className="h-4 w-4 mr-2"/>Quick Audit</Button></div>);
}

function CsvDownloads(){
  const [table, setTable] = useState("export_concept_fields");
  const maps = {
    export_concept_fields: "Fields",
    export_concept_by_spec: "By Spec",
    export_word_coverage: "Word Coverage",
    export_unbound_topN: "Unbound TopN",
  } as const;
  const href = fileUrl(`/api/export/csv?table=${encodeURIComponent(table)}`);
  return (
    <div className="flex items-center gap-2">
      <Select value={table} onValueChange={setTable}>
        <SelectTrigger className="w-56"><SelectValue placeholder="Choose export table" /></SelectTrigger>
        <SelectContent>
          {Object.keys(maps).map(k=> <SelectItem key={k} value={k}>{maps[k as keyof typeof maps]}</SelectItem>)}
        </SelectContent>
      </Select>
      <a className="inline-flex items-center px-3 py-2 rounded-lg border bg-white hover:bg-gray-50" href={href}>
        <Download className="h-4 w-4 mr-2"/>Download CSV
      </a>
    </div>
  );
}

function SearchPanel(){
  const [q,setQ] = useState("");
  const [rows,setRows] = useState<any[]>([]);
  const [loading,setLoading] = useState(false);
  const [specs,setSpecs] = useState<Spec[]>([]);
  const [specId,setSpecId] = useState<string>("");
  const [messages,setMessages] = useState<Message[]>([]);
  const [msgId,setMsgId] = useState<string>("");

  useEffect(()=>{ jsonFetch<Spec[]>("/api/specs").then(setSpecs).catch(()=>{}); },[]);
  useEffect(()=>{ if(!specId) return setMessages([]); jsonFetch<Message[]>(`/api/messages?spec_id=${specId}`).then(setMessages).catch(()=>{}); },[specId]);

  async function doSearch(){
    setLoading(true);
    try{
      const data = await jsonFetch<{query:string, results:any[]}>(`/api/search?q=${encodeURIComponent(q)}`);
      let r = data.results;
      if(specId) r = r.filter(x => String(x.spec_id || x.SPEC_ID || "") === String(specId));
      if(msgId) r = r.filter(x => String(x.message_id || x.MESSAGE_ID || "") === String(msgId));
      setRows(r);
    }catch(e:any){ alert(e.message || String(e)); }
    finally{ setLoading(false); }
  }

  return (
    <Card className="col-span-2">
      <CardHeader className="flex items-center justify-between flex-row">
        <SectionTitle icon={Search}>Search</SectionTitle>
        <div className="flex gap-2 items-center">
          <CsvDownloads/>
          <Select value={specId} onValueChange={setSpecId}>
            <SelectTrigger className="w-48"><SelectValue placeholder="All specs" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="">All</SelectItem>
              {specs.map(s => <SelectItem key={s.spec_id} value={String(s.spec_id)}>{s.code} {s.edition} {s.part_label ?? ""}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={msgId} onValueChange={setMsgId}>
            <SelectTrigger className="w-40"><SelectValue placeholder="All messages" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="">All</SelectItem>
              {messages.map(m => <SelectItem key={m.message_id} value={String(m.message_id)}>{m.j_series}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-3">
          <Input placeholder="Search concepts / aliases / data items / fields…" value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>{if(e.key==='Enter') doSearch();}}/>
          <Button onClick={doSearch} disabled={loading}>{loading? <LoadingInline/> : <>Search</>}</Button>
        </div>
        <div className="border rounded-xl overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>source</TableHead><TableHead>hit_name</TableHead><TableHead>canonical</TableHead>
                <TableHead>spec</TableHead><TableHead>j_series</TableHead><TableHead>word</TableHead>
                <TableHead>field</TableHead><TableHead>bits</TableHead><TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.length===0 && <TableRow><TableCell colSpan={9} className="text-muted-foreground">No results</TableCell></TableRow>}
              {rows.map((r,i)=>(
                <TableRow key={i}>
                  <TableCell>{r.source}</TableCell>
                  <TableCell>{r.hit_name}</TableCell>
                  <TableCell>{r.canonical_name || ""}</TableCell>
                  <TableCell>{[r.code, r.edition, r.part_label].filter(Boolean).join(" ")}</TableCell>
                  <TableCell>{r.j_series || ""}</TableCell>
                  <TableCell>{r.word_label || ""}</TableCell>
                  <TableCell>{r.field_name || ""}</TableCell>
                  <TableCell>{(r.start_bit ?? "") + (r.end_bit!=null?`–${r.end_bit}`:"")}</TableCell>
                  <TableCell className="text-right">
                    {r.field_id ? <BindDialog fieldId={Number(r.field_id)} /> : null}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}

function ComparePanel(){
  const [q,setQ] = useState("Altitude");
  const [bySpec,setBySpec] = useState<any[]>([]);
  const [loading,setLoading] = useState(false);
  async function run(){ setLoading(true); try{
    const data = await jsonFetch<{by_spec:any[]}>(`/api/compare?q=${encodeURIComponent(q)}`);
    setBySpec(data.by_spec || []);
  }catch(e:any){ alert(e.message || String(e)); }finally{ setLoading(false); } }
  const chartData = useMemo(()=> bySpec.map(r=>({ spec:[r.code,r.edition,r.part_label].filter(Boolean).join(" "), fields:Number(r.field_bindings||0) })), [bySpec]);

  return (
    <Card>
      <CardHeader><SectionTitle icon={ChartBar}>Compare Concept</SectionTitle></CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-3">
          <Input value={q} onChange={e=>setQ(e.target.value)} placeholder="e.g. Altitude" onKeyDown={e=>{if(e.key==='Enter') run();}}/>
          <Button onClick={run} disabled={loading}>{loading? <LoadingInline/> : "Compare"}</Button>
        </div>
        <div className="h-56 w-full border rounded-xl p-2 bg-white">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{left:10,right:10,top:10,bottom:10}}>
              <XAxis dataKey="spec" interval={0} angle={-20} textAnchor="end" height={60}/>
              <YAxis/><Tooltip/><Bar dataKey="fields"/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function TopConcepts(){
  const [rows,setRows] = useState<any[]>([]);
  useEffect(()=>{ jsonFetch<any[]>("/api/review/top").then(setRows).catch(()=>{}); },[]);
  return (
    <Card><CardHeader><SectionTitle icon={Gauge}>Top Concepts</SectionTitle></CardHeader>
    <CardContent>
      <div className="border rounded-xl overflow-hidden">
        <Table><TableHeader><TableRow>
          <TableHead>concept</TableHead><TableHead>fields</TableHead><TableHead>data_items</TableHead><TableHead>messages</TableHead><TableHead>specs</TableHead>
        </TableRow></TableHeader>
        <TableBody>
          {rows.map((r,i)=>(
            <TableRow key={i}>
              <TableCell className="font-medium">{r.canonical_name}</TableCell>
              <TableCell>{r.fields}</TableCell>
              <TableCell>{r.data_items}</TableCell>
              <TableCell>{r.messages}</TableCell>
              <TableCell>{r.specs}</TableCell>
            </TableRow>
          ))}
        </TableBody></Table>
      </div>
    </CardContent></Card>
  )
}

export default function App(){
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">MIL-STD-6016 Explorer</h1>
          <QuickActions/>
        </header>
        <Tabs defaultValue="search" className="w-full">
          <TabsList className="mb-3">
            <TabsTrigger value="search"><Search className="h-4 w-4 mr-1"/>Search</TabsTrigger>
            <TabsTrigger value="compare"><ChartBar className="h-4 w-4 mr-1"/>Compare</TabsTrigger>
            <TabsTrigger value="top"><Gauge className="h-4 w-4 mr-1"/>Top</TabsTrigger>
          </TabsList>
          <TabsContent value="search"><div className="grid grid-cols-1 md:grid-cols-3 gap-4"><SearchPanel/><ComparePanel/></div></TabsContent>
          <TabsContent value="compare"><div className="grid grid-cols-1 md:grid-cols-3 gap-4"><ComparePanel/><TopConcepts/></div></TabsContent>
          <TabsContent value="top"><TopConcepts/></TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
