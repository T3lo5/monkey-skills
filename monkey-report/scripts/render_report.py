#!/usr/bin/env python3
"""Renderiza findings.json como dashboard HTML local e fila de prioridade."""
import argparse, csv, html, json, sys, webbrowser
from datetime import datetime, timezone
from pathlib import Path

PORDER={"P0":0,"P1":1,"P2":2,"P3":3,"P4":4}
SORDER={"confirmed":0,"suspected":1,"blocked":2,"not_tested":3}
SLABEL={"confirmed":"Confirmado","suspected":"Suspeita","blocked":"Bloqueado","not_tested":"Não testado"}

def esc(v): return html.escape(str(v if v is not None else ""), quote=True)
def load(path):
    d=json.loads(path.read_text(encoding="utf-8"))
    for k in ("meta","findings","test_cases","queue"):
        if k not in d: raise ValueError("Campo obrigatório ausente: "+k)
    if not isinstance(d["findings"],list) or not isinstance(d["test_cases"],list) or not isinstance(d["queue"],list): raise ValueError("findings, test_cases e queue devem ser listas")
    return d

def queue_rows(d):
    byid={f.get("id"):f for f in d["findings"]}; rows=[]; seen=set()
    for q in d["queue"]:
        linked=[byid[x] for x in q.get("finding_ids",[]) if x in byid]
        linked=[f for f in linked if f.get("status") in ("confirmed","suspected")]
        if not linked: continue
        ids=[f.get("id","") for f in linked]; seen.update(ids)
        p=min((f.get("priority",q.get("priority","P4")) for f in linked),key=lambda x:PORDER.get(x,99))
        rows.append({"priority":p,"status":"confirmed" if any(f.get("status")=="confirmed" for f in linked) else "suspected","finding_ids":ids,"title":q.get("title") or linked[0].get("title","Sem título"),"rationale":q.get("rationale",""),"dependencies":q.get("dependencies",[]),"recommendation":" ".join(dict.fromkeys(f.get("recommendation","") for f in linked if f.get("recommendation")))})
    for f in d["findings"]:
        if f.get("id") not in seen and f.get("status") in ("confirmed","suspected"):
            rows.append({"priority":f.get("priority","P4"),"status":f["status"],"finding_ids":[f.get("id","")],"title":f.get("title","Sem título"),"rationale":"Achado ausente da fila original; incluído para não o perder.","dependencies":[],"recommendation":f.get("recommendation","")})
    rows.sort(key=lambda r:(PORDER.get(r["priority"],99),SORDER.get(r["status"],99)))
    return rows

def sanitize_evidence(d,out):
    warnings=[]
    root=out.resolve()
    for f in d["findings"]:
        for e in f.get("evidence",[]):
            rel=e.get("path")
            if not rel: continue
            p=(out/rel).resolve()
            try: p.relative_to(root)
            except ValueError: e["path"]=""; warnings.append(f'{f.get("id")}: evidência fora da pasta bloqueada'); continue
            if not p.is_file(): e["path"]=""; warnings.append(f'{f.get("id")}: evidência ausente ({rel})')
    return warnings

def render_html(d, rows, warnings):
    meta=d["meta"]; findings=d["findings"]; tests=d["test_cases"]
    counts={s:sum(f.get("status")==s for f in findings) for s in SLABEL}
    stats=[("Achados",len(findings)),("Confirmados",counts["confirmed"]),("Suspeitas",counts["suspected"]),("Bloqueados",counts["blocked"]+counts["not_tested"]),("Testes executados",sum(t.get("status") in ("passed","failed") for t in tests))]
    stat_html="".join(f'<div class="stat"><span>{esc(label)}</span><strong>{n}</strong></div>' for label,n in stats)
    cats=sorted({f.get("category","") for f in findings if f.get("category")})
    cats_html=''.join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in cats)
    limitations=''.join(f'<li>{esc(x)}</li>' for x in meta.get("limitations",[])) or '<li>Nenhuma limitação registrada.</li>'
    limitations+=''.join(f'<li>{esc(x)}</li>' for x in warnings)
    payload=json.dumps({"findings":findings,"tests":tests,"queue":rows},ensure_ascii=False).replace("</","<\\/")
    return '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>Monkey User — Relatório</title><style>
:root{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:dark;--bg:#0b1020;--panel:#141b2e;--panel2:#1b2540;--text:#eef2ff;--muted:#aab5d0;--line:#303b57;--accent:#9db8ff;--red:#ff7d8b;--orange:#ffbd76;--yellow:#f4dc83;--green:#80dfb0}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);line-height:1.5}a{color:var(--accent)}button,input,select{font:inherit;border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:9px;padding:9px 11px}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:2px}.wrap{max-width:1400px;margin:auto;padding:28px 22px 60px}.hero{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}.eyebrow{color:var(--accent);font-size:.78rem;text-transform:uppercase;letter-spacing:.13em;font-weight:800}h1{font-size:clamp(2rem,4vw,3.2rem);line-height:1.05;margin:.35rem 0 .7rem}h2{font-size:1.25rem;margin:0 0 14px}h3{margin:.3rem 0 .5rem;font-size:1rem}.muted,small{color:var(--muted)}.meta,.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.chip,.pill{display:inline-flex;border:1px solid var(--line);border-radius:99px;padding:4px 9px;font-size:.78rem}.notice{border:1px solid #347e63;background:#102c29;color:#b9f5d9;padding:12px 15px;border-radius:12px;margin:22px 0}.grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:20px 0}.stat,.panel,.finding,.queue-item{background:var(--panel);border:1px solid var(--line);border-radius:15px}.stat{padding:15px}.stat strong{display:block;font-size:1.8rem}.stat span{color:var(--muted);font-size:.86rem}.layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(280px,.72fr);gap:16px;align-items:start}.panel{padding:18px;margin-bottom:16px}.filters{display:grid;grid-template-columns:2fr repeat(3,minmax(120px,1fr));gap:9px;margin-bottom:15px}.findings,.queue-list{display:grid;gap:10px}.finding,.queue-item{padding:14px}.finding summary{cursor:pointer;list-style:none}.f-head{display:flex;align-items:flex-start;gap:10px;justify-content:space-between}.f-title{font-weight:750}.p0,.p1{color:var(--red);border-color:#884653}.p2{color:var(--orange)}.p3{color:var(--yellow)}.p4{color:var(--muted)}.confirmed{color:var(--green)}.suspected{color:var(--orange)}.blocked,.not_tested{color:var(--muted)}.details{border-top:1px solid var(--line);margin-top:13px;padding-top:12px;display:grid;gap:12px}.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.detail-box{background:var(--panel2);padding:11px;border-radius:10px;min-width:0}.detail-box p{margin:.25rem 0;overflow-wrap:anywhere}.steps{padding-left:22px}.steps li{margin:5px 0}.rank{font-weight:800;color:var(--accent);margin-right:6px}.empty{border:1px dashed var(--line);padding:25px;text-align:center;border-radius:12px;color:var(--muted)}.coverage-row{display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding:9px 0}footer{margin-top:24px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:.85rem}.small{font-size:.86rem}@media(max-width:950px){.grid{grid-template-columns:repeat(3,1fr)}.layout{grid-template-columns:1fr}.filters{grid-template-columns:1fr 1fr}}@media(max-width:560px){.wrap{padding:18px 12px 40px}.grid{grid-template-columns:repeat(2,1fr)}.filters,.detail-grid{grid-template-columns:1fr}.f-head{display:block}}
</style></head><body><main class="wrap"><header class="hero"><div><div class="eyebrow">Monkey User / UX Chaos Audit</div><h1>Relatório de auditoria</h1><div>'''+esc(meta.get("project","Projeto"))+'''</div><div class="meta"><span class="chip">Ambiente: '''+esc(meta.get("environment","Não informado"))+'''</span><span class="chip">Escopo: '''+esc(meta.get("scope","Não informado"))+'''</span><span class="chip">Gerado: '''+esc(meta.get("generated_at",""))+'''</span></div><div class="meta muted">Stack: '''+esc(", ".join(meta.get("stack",[])) or "Não informada")+'''</div></div><div class="actions"><button onclick="window.print()">Imprimir / salvar PDF</button><button id="exportCsv">Exportar fila CSV</button></div></header><div class="notice"><strong>Somente relatório:</strong> nenhuma correção foi aplicada ao código do produto.</div><section class="grid">'''+stat_html+'''</section><div class="layout"><section class="panel"><h2>Achados</h2><div class="filters"><input id="search" type="search" placeholder="Buscar título, rota, impacto…" aria-label="Buscar achados"><select id="status" aria-label="Filtrar status"><option value="">Todos os status</option><option value="confirmed">Confirmados</option><option value="suspected">Suspeitas</option><option value="blocked">Bloqueados</option><option value="not_tested">Não testados</option></select><select id="priority" aria-label="Filtrar prioridade"><option value="">Todas as prioridades</option><option>P0</option><option>P1</option><option>P2</option><option>P3</option><option>P4</option></select><select id="category" aria-label="Filtrar categoria"><option value="">Todas as categorias</option>'''+cats_html+'''</select></div><div id="findingList" class="findings"></div></section><aside><section class="panel"><h2>Fila de correções</h2><p class="muted small">Ordem sugerida. Confirme impacto e dependências antes de iniciar; suspeitas continuam identificadas.</p><div id="queueList" class="queue-list"></div></section><section class="panel"><h2>Cobertura dos testes</h2><div id="coverage"></div></section><section class="panel"><h2>Limitações</h2><ul>'''+limitations+'''</ul></section></aside></div><footer>Gerado localmente por monkey-report. Arquivo autônomo; nenhum conteúdo é enviado a serviços externos.</footer></main><script>
const DATA='''+payload+''';const $=id=>document.getElementById(id),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const po={P0:0,P1:1,P2:2,P3:3,P4:4},sl={confirmed:'Confirmado',suspected:'Suspeita',blocked:'Bloqueado',not_tested:'Não testado'};
function searchText(f){return [f.id,f.title,f.route,f.component,f.category,f.observed,f.expected,f.user_impact,f.recommendation,...(f.tags||[])].join(' ').toLowerCase()}
function evhtml(f){return (f.evidence||[]).length?'<ul>'+f.evidence.map(e=>'<li>'+(e.path?'<a href="'+esc(e.path)+'" target="_blank" rel="noopener">'+esc(e.description||e.path)+'</a>':esc(e.description||e.kind||'Evidência sem arquivo'))+(e.redacted?' (dados redigidos)':'')+'</li>').join('')+'</ul>':'<p class="muted small">Nenhuma evidência anexada.</p>'}
function fhtml(f){return '<details class="finding"><summary><div class="f-head"><div><div class="f-title">'+esc(f.id)+' — '+esc(f.title)+'</div><div class="muted small">'+esc(f.route||'Rota não informada')+' · '+esc(f.category||'Sem categoria')+'</div></div><div><span class="pill '+esc((f.priority||'P4').toLowerCase())+'">'+esc(f.priority||'P4')+'</span> <span class="pill '+esc(f.status)+'">'+esc(sl[f.status]||f.status)+'</span></div></div></summary><div class="details"><div class="meta"><span class="chip">Confiança: '+esc(f.confidence||'não informada')+'</span><span class="chip">Severidade: '+esc(f.severity||'não informada')+'</span>'+(f.component?'<span class="chip">'+esc(f.component)+'</span>':'')+'</div><div class="detail-grid"><div class="detail-box"><strong>Observado</strong><p>'+esc(f.observed||'Não informado')+'</p></div><div class="detail-box"><strong>Esperado</strong><p>'+esc(f.expected||'Não informado')+'</p></div></div><div><strong>Passos para reproduzir</strong>'+(f.steps?.length?'<ol class="steps">'+f.steps.map(s=>'<li>'+esc(s)+'</li>').join('')+'</ol>':'<p class="muted">Passos não informados.</p>')+'</div><div><strong>Impacto</strong><p>'+esc(f.user_impact||'Não informado')+'</p></div><div><strong>Recomendação</strong><p>'+esc(f.recommendation||'Não informada')+'</p></div><div><strong>Evidências</strong>'+evhtml(f)+'</div>'+((f.source_refs||[]).length?'<div><strong>Referências no código</strong><ul>'+f.source_refs.map(x=>'<li><code>'+esc(x)+'</code></li>').join('')+'</ul></div>':'')+'</div></details>'}
function renderF(){let q=$('search').value.toLowerCase(),s=$('status').value,p=$('priority').value,c=$('category').value;let fs=DATA.findings.filter(f=>(!q||searchText(f).includes(q))&&(!s||f.status===s)&&(!p||f.priority===p)&&(!c||f.category===c)).sort((a,b)=>(po[a.priority]??99)-(po[b.priority]??99)||( {confirmed:0,suspected:1,blocked:2,not_tested:3}[a.status]??9)-({confirmed:0,suspected:1,blocked:2,not_tested:3}[b.status]??9));$('findingList').innerHTML=fs.length?fs.map(fhtml).join(''):'<div class="empty">Nenhum achado corresponde aos filtros.</div>'}
function renderQ(){$('queueList').innerHTML=DATA.queue.length?DATA.queue.map((r,i)=>'<article class="queue-item"><div><span class="rank">#'+(i+1)+'</span><span class="pill '+esc((r.priority||'P4').toLowerCase())+'">'+esc(r.priority)+'</span> <span class="pill '+esc(r.status)+'">'+esc(sl[r.status]||r.status)+'</span></div><h3>'+esc(r.title)+'</h3><small>'+esc((r.finding_ids||[]).join(', '))+'</small><p>'+esc(r.rationale||'')+'</p>'+(r.dependencies?.length?'<p class="small"><strong>Dependências:</strong> '+esc(r.dependencies.join('; '))+'</p>':'')+(r.recommendation?'<p class="small"><strong>Próximo passo:</strong> '+esc(r.recommendation)+'</p>':'')+'</article>').join(''):'<div class="empty">Nenhuma correção priorizada.</div>'}
function renderC(){let c={passed:0,failed:0,blocked:0,not_tested:0,inconclusive:0};DATA.tests.forEach(t=>c[t.status]=(c[t.status]||0)+1);let labels={passed:'Passou',failed:'Falhou',blocked:'Bloqueado',not_tested:'Não executado',inconclusive:'Inconclusivo'};$('coverage').innerHTML=DATA.tests.length?Object.entries(c).map(([k,n])=>'<div class="coverage-row"><span>'+labels[k]+'</span><strong>'+n+'</strong></div>').join('')+'<p class="muted small">'+DATA.tests.length+' cenários registrados</p>':'<div class="empty">Nenhum cenário registrado.</div>'}
function csvq(){let rows=[['rank','priority','status','finding_ids','title','rationale','dependencies','recommendation'],...DATA.queue.map((r,i)=>[i+1,r.priority,r.status,(r.finding_ids||[]).join('; '),r.title,r.rationale,(r.dependencies||[]).join('; '),r.recommendation])];let blob=new Blob(['\\ufeff'+rows.map(row=>row.map(v=>'"'+String(v??'').replace(/"/g,'""')+'"').join(',')).join('\\r\\n')],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='priority-queue.csv';a.click();URL.revokeObjectURL(url)}
['search','status','priority','category'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',renderF));$('exportCsv').addEventListener('click',csvq);renderF();renderQ();renderC();</script></body></html>'''

def write_queues(rows,out):
    headers=["rank","priority","status","finding_ids","title","rationale","dependencies","recommendation"]
    with (out/"priority-queue.csv").open("w",encoding="utf-8-sig",newline="") as fp:
        w=csv.writer(fp);w.writerow(headers)
        for i,r in enumerate(rows,1): w.writerow([i,r["priority"],r["status"],"; ".join(r["finding_ids"]),r["title"],r["rationale"],"; ".join(r["dependencies"]),r["recommendation"]])
    lines=["# Fila de correções — monkey-user","","> Fila recomendada. Nenhuma correção foi aplicada.","","| # | Prioridade | Status | Achados | Tarefa | Justificativa | Dependências | Próximo passo |","|---:|---|---|---|---|---|---|---|"]
    for i,r in enumerate(rows,1):
        vals=[str(i),r["priority"],r["status"],", ".join(r["finding_ids"]),r["title"],r["rationale"],"; ".join(r["dependencies"]),r["recommendation"]]
        lines.append("| "+" | ".join(v.replace("|","\\|").replace("\n"," ") for v in vals)+" |")
    (out/"priority-queue.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("findings",type=Path);ap.add_argument("--outdir",type=Path);ap.add_argument("--open",action="store_true");a=ap.parse_args()
    src=a.findings.expanduser().resolve()
    if not src.is_file(): print("ERRO: arquivo não encontrado: "+str(src),file=sys.stderr);return 2
    try: d=load(src)
    except Exception as e: print("ERRO ao ler findings.json: "+str(e),file=sys.stderr);return 2
    out=(a.outdir.expanduser().resolve() if a.outdir else src.parent)
    if out.exists() and any((out/n).exists() for n in ("index.html","priority-queue.md","priority-queue.csv","report-meta.json")):
        print("ERRO: saídas já existem; escolha outra pasta para evitar sobrescrita.",file=sys.stderr);return 2
    out.mkdir(parents=True,exist_ok=True);warnings=sanitize_evidence(d,out);rows=queue_rows(d)
    (out/"index.html").write_text(render_html(d,rows,warnings),encoding="utf-8");write_queues(rows,out)
    opened=None
    if a.open:
        try: opened=bool(webbrowser.open((out/"index.html").as_uri(),new=2))
        except Exception: opened=False
    meta={"source":str(src),"generated_at":datetime.now(timezone.utc).isoformat(),"html":"index.html","queue_markdown":"priority-queue.md","queue_csv":"priority-queue.csv","findings":len(d["findings"]),"queue_items":len(rows),"warnings":warnings,"browser_open_attempted":a.open,"browser_open_result":opened}
    (out/"report-meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("HTML:",out/"index.html");print("Fila Markdown:",out/"priority-queue.md");print("Fila CSV:",out/"priority-queue.csv");print(f"Achados: {len(d['findings'])}; itens na fila: {len(rows)}")
    if a.open: print("Abertura do navegador:","solicitada ao sistema" if opened else "não confirmada; abra o HTML manualmente")
    for w in warnings: print("AVISO:",w)
    return 0
if __name__=="__main__": raise SystemExit(main())
