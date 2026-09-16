(()=>{'use strict';
const R6_WORKFLOW=['PENDIENTE','REVISADO','HACIENDO','LISTO','PROGRAMADO','PUBLICADO'];
const DONE=new Set(['ready','done','approved','placed','created','complete','completed','verified']);
const PROFILE_LABELS={XR_FULL:'Cinematic Edit',MOTION_SFX:'Dynamic Edit',SFX_ONLY:'Clean Edit'};
const checklistKeys=['editorial','source','cut','xr','images','broll','cine','motion','sfx','music','captions','cover','copy','qa'];
const baseRenderBuild=typeof renderBuild==='function'?renderBuild:null;
const baseRenderLibrary=typeof renderLibrary==='function'?renderLibrary:null;
const baseRender=typeof render==='function'?render:null;

function pieceId(p){return String(p?.canonicalId||p?.contentId||p?.id||'')}
function validation(){return APP_STATE.r6Validation||current()?.r6Validation||null}
function validationRow(id){return validation()?.pieces?.find(x=>String(x.id)===String(id))||null}
function checklistProgress(piece){
  const row=validationRow(pieceId(piece));
  if(row&&Number.isFinite(+row.progressPercent))return +row.progressPercent;
  const c=piece?.productionChecklist;
  if(!c||typeof c!=='object')return 0;
  let done=0;
  for(const key of checklistKeys){const raw=c[key],status=String((raw&&typeof raw==='object'?raw.status:raw)||'pending').toLowerCase();if(DONE.has(status))done++}
  return Math.round(done/checklistKeys.length*100);
}
function badge(text,kind='neutral'){return `<span class="r6-validation-badge r6-${kind}">${esc(text)}</span>`}
function statusBadges(piece){const row=validationRow(pieceId(piece));let out=badge(piece.stage||'BETA','stage');const profile=piece?.editProfile,code=typeof profile==='string'?profile:profile?.code;if(code){const name=(typeof profile==='object'&&profile?.commercialName)||PROFILE_LABELS[code]||code;out+=badge(`${name} · ${code}`,'profile')}if(row){out+=badge(row.alphaReady?'Alpha ✓':'Alpha revisar',row.alphaReady?'ok':'warn');if(['intro','vertical','horizontal','video','clip','full_episode'].includes(piece.type))out+=badge(row.cutterReady?'Cutter ✓':'Cutter revisar',row.cutterReady?'ok':'warn')}return out}
function progressMarkup(piece){const pct=checklistProgress(piece);return `<div class="r6-progress"><i style="width:${Math.max(0,Math.min(100,pct))}%"></i></div><small class="r6-progress-label">${pct}% producción</small>`}

async function refreshR6Validation(renderAfter=false){
  if(!APP_STATE.currentProjectId)return null;
  try{const result=await api('/api/r6_validate','POST',{projectId:APP_STATE.currentProjectId});APP_STATE.r6Validation=result.validation;if(current())current().r6Validation=result.validation;if(renderAfter&&typeof render==='function')render();return result.validation}catch(err){return null}
}

renderKanban=function(){
  const host=$('#kanban');if(!host)return;
  const rows=pieces();
  host.innerHTML=`<div class="hero"><div><small>PRODUCCIÓN R6</small><h1>Kanban</h1></div><span class="badge">${rows.length} fichas</span></div><div class="kanban-grid r6-kanban-grid">${R6_WORKFLOW.map(w=>`<section class="kanban-col r6-kanban-col" data-workflow="${w}"><h3>${w}</h3><div class="r6-kanban-count">${rows.filter(p=>(p.workflowStatus||'PENDIENTE')===w).length}</div>${rows.filter(p=>(p.workflowStatus||'PENDIENTE')===w).map(p=>`<button class="r6-kanban-card" draggable="true" data-kanban-piece="${esc(pieceId(p))}"><b>${esc(p.title||pieceId(p))}</b><small>${esc(p.type||'')} · ${esc(pieceId(p))}</small><div class="r6-badges">${statusBadges(p)}</div>${progressMarkup(p)}</button>`).join('')}</section>`).join('')}</div>`;
  $$('[data-kanban-piece]').forEach(card=>card.ondragstart=e=>{e.dataTransfer.setData('text/plain',card.dataset.kanbanPiece);e.dataTransfer.effectAllowed='move'});
  $$('[data-workflow]').forEach(col=>{
    col.ondragover=e=>{e.preventDefault();col.classList.add('dragover')};
    col.ondragleave=()=>col.classList.remove('dragover');
    col.ondrop=async e=>{e.preventDefault();col.classList.remove('dragover');const id=e.dataTransfer.getData('text/plain');const p=pieces().find(x=>pieceId(x)===id);if(!p)return;const next=col.dataset.workflow;if(!R6_WORKFLOW.includes(next)||p.workflowStatus===next)return;try{await api('/api/update_piece','POST',{projectId:APP_STATE.currentProjectId,pieceId:id,patch:{workflowStatus:next}});p.workflowStatus=next;renderKanban();refreshR6Validation(false);toast(`Estado: ${next}`)}catch(err){toast(err.message||String(err))}}
  });
};

function decorateBuild(){
  const host=$('#build');if(!host)return;
  $$('[data-build-piece]',host).forEach(input=>{const p=pieces().find(x=>pieceId(x)===input.value);const row=input.closest('.build-row')||input.parentElement;if(!p||!row||row.querySelector('.r6-validation-badge'))return;const box=document.createElement('div');box.className='r6-build-meta';box.innerHTML=statusBadges(p)+progressMarkup(p);row.appendChild(box)});
  const aside=host.querySelector('aside');const v=validation();if(aside&&v&&!aside.querySelector('.r6-validation-summary')){const box=document.createElement('div');box.className='r6-validation-summary';box.innerHTML=`<b>R6 Preflight</b><small>${v.summary?.criticalCount||0} críticos · ${v.summary?.warningCount||0} warnings · ${v.summary?.alphaReadyCount||0} Alpha ready · ${v.summary?.cutterReadyCount||0} Cutter ready</small>`;aside.prepend(box)}
}
function decorateLibrary(){
  const host=$('#library');if(!host)return;const v=validation();if(!v||host.querySelector('.r6-validation-summary'))return;const box=document.createElement('div');box.className='r6-validation-summary r6-library-summary';box.innerHTML=`<b>${v.r6Detected?'R6 activo':'Legacy compatible'}</b><small>${v.summary?.criticalCount||0} críticos · ${v.summary?.warningCount||0} warnings · ${v.summary?.alphaReadyCount||0} Alpha ready</small>`;host.prepend(box)
}
if(baseRenderBuild)renderBuild=function(){baseRenderBuild();decorateBuild()};
if(baseRenderLibrary)renderLibrary=function(){baseRenderLibrary();decorateLibrary()};
if(baseRender)render=function(){baseRender();if(APP_STATE.view==='build')decorateBuild();else if(APP_STATE.view==='library')decorateLibrary()};

window.ABRXOS_GEOMETRA_R6={version:'3.1-r6',workflow:R6_WORKFLOW,refreshValidation:refreshR6Validation,progressFor:checklistProgress,validationRow};
setTimeout(()=>{if(!validation())refreshR6Validation(false).then(()=>{if(typeof render==='function')render()});},120);
})();
