import { useEffect, useMemo, useState } from "react";

const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";
async function j<T>(p: string){ const r = await fetch(API+p); if(!r.ok) throw new Error(await r.text()); return r.json(); }

export default function App() {
  const [top,setTop] = useState<any[]>([]);
  const [cmp,setCmp] = useState("Altitude");
  const [bySpec,setBySpec] = useState<any[]>([]);
  const [q,setQ] = useState("");
  const [search,setSearch] = useState<any[]>([]);

  useEffect(()=>{ j<any[]>("/api/review/top").then(setTop).catch(console.error); },[]);
  async function doCompare(){ const d = await j<any>(`/api/compare?q=${encodeURIComponent(cmp)}`); setBySpec(d.by_spec||[]); }
  async function doSearch(){ const d = await j<any>(`/api/search?q=${encodeURIComponent(q)}`); setSearch(d.results||[]); }

  return (
    <div style={{fontFamily:"Inter,ui-sans-serif", padding:20}}>
      <h1 style={{fontWeight:700}}>MIL-STD-6016 Explorer</h1>

      <section style={{marginTop:16}}>
        <h2>Search</h2>
        <div>
          <input value={q} onChange={e=>setQ(e.target.value)} placeholder="concept / alias / field / DI" />
          <button onClick={doSearch}>Search</button>
        </div>
        <div>
          <table><thead><tr>
            <th>source</th><th>hit_name</th><th>canonical</th><th>spec</th><th>j_series</th><th>word</th><th>field</th><th>bits</th>
          </tr></thead><tbody>
            {search.map((r:any,i:number)=>(
              <tr key={i}>
                <td>{r.source}</td>
                <td>{r.hit_name}</td>
                <td>{r.canonical_name||""}</td>
                <td>{[r.code,r.edition,r.part_label].filter(Boolean).join(" ")}</td>
                <td>{r.j_series||""}</td>
                <td>{r.word_label||""}</td>
                <td>{r.field_name||""}</td>
                <td>{r.start_bit!=null?`${r.start_bit}–${r.end_bit}`:""}</td>
              </tr>
            ))}
          </tbody></table>
        </div>
      </section>

      <section style={{marginTop:16}}>
        <h2>Compare</h2>
        <div>
          <input value={cmp} onChange={e=>setCmp(e.target.value)} placeholder="Altitude" />
          <button onClick={doCompare}>Compare</button>
        </div>
        <table><thead><tr><th>spec</th><th>field_bindings</th><th>data_item_bindings</th></tr></thead><tbody>
          {bySpec.map((r:any,i:number)=>(
            <tr key={i}><td>{[r.code,r.edition,r.part_label].filter(Boolean).join(" ")}</td><td>{r.field_bindings}</td><td>{r.data_item_bindings}</td></tr>
          ))}
        </tbody></table>
      </section>

      <section style={{marginTop:16}}>
        <h2>Top Concepts</h2>
        <table><thead><tr><th>concept</th><th>fields</th><th>data_items</th><th>messages</th><th>specs</th></tr></thead><tbody>
          {top.map((r:any,i:number)=>(
            <tr key={i}><td>{r.canonical_name}</td><td>{r.fields}</td><td>{r.data_items}</td><td>{r.messages}</td><td>{r.specs}</td></tr>
          ))}
        </tbody></table>
      </section>
    </div>
  );
}