import {loadConfig,resolveUrl} from "./config.js";
import {icon,iconHtml} from "./icons.js";
import {getProfile,getRepo} from "./github.js";
import {readAllFeeds} from "./rss.js";
import {loadStore} from "./store.js";
import {loadDocs,loadDoc,sortDocs} from "./docs.js";
import {markdown} from "./markdown.js";

let cfg, repo, profile, repository, storeData, newsData, docsData=[];
const state={page:"home",category:"",subcategory:"",query:"",doc:"",theme:"dark"};
const $=s=>document.querySelector(s);
const content=$("#content");
function esc(v=""){return String(v).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}
function fmtDate(v){const d=new Date(v);return Number.isNaN(d.getTime())?String(v||""):new Intl.DateTimeFormat(cfg.site.language||"fr",{dateStyle:"medium"}).format(d)}
function toast(msg){const t=$("#toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2500)}
function setTitle(label){$("#page-title").textContent=label;$("#page-kicker").textContent=cfg.site.name}
function nav(){
  $("#main-nav").innerHTML=(cfg.navigation||[]).filter(x=>x.enabled!==false).map(x=>`<a href="#${x.id}" class="nav-item ${state.page===x.id?"active":""}" data-page="${x.id}"><span class="nav-icon">${iconHtml(x.icon)}</span><span>${esc(x.label)}</span></a>`).join("");
  document.querySelectorAll("[data-page]").forEach(a=>a.onclick=()=>{state.page=a.dataset.page;render()});
}
async function profileUI(){
  const p=profile||{}; const avatar=p.avatar_url||cfg.profile.avatar||"./web/assets/avatar-placeholder.svg";
  $("#profile").classList.remove("skeleton-card");
  $("#profile").innerHTML=`<div class="profile-head"><img class="avatar" src="${esc(avatar)}" onerror="this.src='./web/assets/avatar-placeholder.svg'" alt=""><div><div class="profile-name">${esc(p.name||repo.owner||"GitHub User")}</div><div class="profile-handle">@${esc(p.login||repo.owner||"")}</div></div></div>${cfg.profile.showBio?`<p class="bio">${esc(p.bio||cfg.profile.bioFallback||"")}</p>`:""}<div class="profile-meta">${cfg.profile.showLocation&& (p.location||cfg.profile.locationFallback)?`<span>⌖ ${esc(p.location||cfg.profile.locationFallback)}</span>`:""}${cfg.profile.showStats&&p.public_repos!=null?`<span>◈ ${p.public_repos} repos</span>`:""}</div>`;
}
function socialsUI(){
  const list=(cfg.socials||[]).filter(x=>x.enabled!==false&&x.url!==undefined);
  $("#sidebar-bottom").innerHTML=`<div class="socials">${list.map(s=>`<a class="social" href="${esc(s.url||repo.githubUrl||"#")}" target="_blank" rel="noopener" title="${esc(s.label)}">${s.iconType==="image"?`<img src="${esc(resolveUrl(s.icon,repo))}" alt="">`:iconHtml(s.icon||"link")}</a>`).join("")}</div>`;
}
function shell(){nav();profileUI();socialsUI();$("#brand-logo").src=cfg.branding.logo||"./web/assets/logo.svg";$("#brand-title").textContent=cfg.site.shortName||cfg.site.name;$("#brand-subtitle").textContent=(cfg.site.name||"").replace(cfg.site.shortName||"","").trim()||"Core OS";$("#github-top").href=repo.githubUrl||"#";$("#github-top").style.display=repo.githubUrl?"":"none";if(!cfg.site.showThemeToggle)$("#theme-toggle").style.display="none"}
function hero(){
 return `<section class="hero">${cfg.branding.heroImage?`<img class="hero-bg" src="${esc(resolveUrl(cfg.branding.heroImage,repo))}" alt="">`:""}<div class="eyebrow">${esc(cfg.site.name)}</div><h1>${esc(cfg.branding.heroTitle)}</h1><p>${esc(cfg.branding.heroText)}</p><div class="tags">${(cfg.branding.heroTags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join("")}</div></section>`
}
function quickCards(){
 const items=[["news","rss","News","Flux RSS transformés en articles."],["downloads","download","Download","Packs et fichiers prêts à télécharger."],["store","store","Store","Catalogue JSON avec recherche et catégories."],["docs","book","Documentation","Wiki Markdown parcourable."],["services","link","Services","Accès rapide à vos services."]];
 return `<div class="grid">${items.filter(x=>(cfg.navigation||[]).find(n=>n.id===x[0]&&n.enabled!==false)).map(x=>`<a class="card feature" href="#${x[0]}"><div class="feature-icon">${iconHtml(x[1])}</div><div><h3>${x[2]}</h3><p>${x[3]}</p></div></a>`).join("")}</div>`
}
async function home(){
 setTitle("Home"); content.innerHTML=hero()+`<div class="section-title"><div><h2>Accès rapide</h2><p>Votre espace, piloté par configuration.</p></div></div>${quickCards()}<div class="section-title"><div><h2>État du projet</h2><p>Informations détectées automatiquement.</p></div></div><div class="grid"><div class="card stat"><span class="muted">Dépôt</span><strong>${esc(repo.name||"—")}</strong></div><div class="card stat"><span class="muted">Propriétaire</span><strong>${esc(repo.owner||"—")}</strong></div><div class="card stat"><span class="muted">Branche</span><strong>${esc(repo.branch||"main")}</strong></div></div>${footer()}`
}
async function news(){
 setTitle("News"); if(!newsData)newsData=await readAllFeeds(cfg);
 content.innerHTML=`${hero()}<div class="section-title"><div><h2>Dernières actualités</h2><p>${newsData.items.length} article(s) chargé(s) depuis RSS.</p></div></div>${newsData.errors.length?`<div class="error">Certains flux n'ont pas pu être lus : ${newsData.errors.map(e=>esc(e.feed)).join(", ")}</div>`:""}<div class="news-list">${newsData.items.map(n=>`<article class="news-card"><div class="news-thumb">${n.image?`<img src="${esc(n.image)}" alt="">`:"◔"}</div><div><span class="date">${esc(n.source)} • ${fmtDate(n.date)}</span><h3>${esc(n.title)}</h3><p>${esc(n.description).slice(0,280)}${n.description.length>280?"…":""}</p>${n.link?`<a class="btn" href="${esc(n.link)}" target="_blank" rel="noopener">Lire la suite ${iconHtml("external")}</a>`:""}</div></article>`).join("")||`<div class="empty">Aucune actualité disponible.</div>`}</div>${footer()}`
}
function downloads(){
 setTitle("Download"); const items=cfg.downloads?.items||[];
 content.innerHTML=`${hero()}<div class="section-title"><div><h2>Téléchargements</h2><p>${items.length} ressource(s) configurée(s).</p></div></div>${cfg.downloads.search?`<div class="toolbar"><input id="dl-search" class="input" placeholder="Rechercher un fichier..." value="${esc(state.query)}"></div>`:""}<div id="download-list" class="list"></div>${footer()}`;
 const draw=()=>{const q=state.query.toLowerCase();$("#download-list").innerHTML=items.filter(i=>(i.name+" "+i.filename+" "+i.description+" "+i.category).toLowerCase().includes(q)).map(i=>`<div class="download-row"><div class="row-icon">${iconHtml("download")}</div><div class="row-main"><strong>${esc(i.name)}</strong><p>${esc(i.description||i.filename)} ${i.category?`• ${esc(i.category)}`:""}</p></div><div class="row-actions"><a class="btn" href="${esc(resolveUrl(i.url,repo))}" target="_blank" rel="noopener">Télécharger</a></div></div>`).join("")||`<div class="empty">Aucun fichier trouvé.</div>`};
 $("#dl-search")?.addEventListener("input",e=>{state.query=e.target.value;draw()});draw()
}
async function store(){
 setTitle("Store"); if(!storeData)storeData=await loadStore(cfg); const all=storeData.items; const cats=[...new Set(all.map(x=>x.category).filter(Boolean))].sort();
 content.innerHTML=`${hero()}<div class="section-title"><div><h2>Store</h2><p>${all.length} éléments provenant des JSON.</p></div></div>${storeData.errors.length?`<div class="error">Sources indisponibles : ${storeData.errors.map(e=>esc(e.source)).join(", ")}</div>`:""}<div class="toolbar"><input id="store-search" class="input" placeholder="Rechercher un fichier ou outil..." value="${esc(state.query)}"><select id="store-category" class="select"><option value="">Toutes les catégories</option>${cats.map(c=>`<option ${state.category===c?"selected":""}>${esc(c)}</option>`).join("")}</select><select id="store-subcategory" class="select"><option value="">Toutes les sous-catégories</option></select><button id="store-reset" class="btn ghost">Réinitialiser</button></div><div id="store-list" class="store-grid"></div>${footer()}`;
 const cat=$("#store-category"),sub=$("#store-subcategory");
 function subOptions(){const vals=[...new Set(all.filter(x=>!state.category||x.category===state.category).map(x=>x.subcategory).filter(Boolean))].sort();sub.innerHTML=`<option value="">Toutes les sous-catégories</option>`+vals.map(x=>`<option ${state.subcategory===x?"selected":""}>${esc(x)}</option>`).join("")}
 function draw(){const q=state.query.toLowerCase();const rows=all.filter(x=>(!state.category||x.category===state.category)&&(!state.subcategory||x.subcategory===state.subcategory)&&(x.name+" "+x.filename+" "+x.description+" "+x.author+" "+x.category+" "+x.subcategory).toLowerCase().includes(q));$("#store-list").innerHTML=rows.map(x=>`<article class="store-card"><div class="store-head"><div class="store-icon">${x.icon?`<img src="${esc(resolveUrl(x.icon,repo))}" alt="">`:iconHtml(x.sourceId==="packages"?"store":"code")}</div><div><h3>${esc(x.name)}</h3><div class="store-meta">${x.version?`<span class="pill">${esc(x.version)}</span>`:""}${x.category?`<span class="pill">${esc(x.category)}</span>`:""}${x.subcategory?`<span class="pill">${esc(x.subcategory)}</span>`:""}${x.author?`<span class="pill">${esc(x.author)}</span>`:""}</div></div></div><p>${esc(x.description||x.filename)}</p>${cfg.store.showChecksum&&x.checksum?`<p class="muted">SHA-256: ${esc(x.checksum)}</p>`:""}<div class="row-actions">${x.url?`<a class="btn" href="${esc(resolveUrl(x.url,repo))}" target="_blank" rel="noopener">Télécharger</a>`:""}<button class="btn ghost" data-details="${esc(x.id)}">Détails</button></div></article>`).join("")||`<div class="empty">Aucun élément ne correspond aux filtres.</div>`;document.querySelectorAll("[data-details]").forEach(b=>b.onclick=()=>{const x=all.find(i=>i.id===b.dataset.details);toast(x?.filename||x?.name||"")})}
 $("#store-search").oninput=e=>{state.query=e.target.value;draw()};cat.onchange=e=>{state.category=e.target.value;state.subcategory="";subOptions();draw()};sub.onchange=e=>{state.subcategory=e.target.value;draw()};$("#store-reset").onclick=()=>{state.query="";state.category="";state.subcategory="";cat.value="";subOptions();$("#store-search").value="";draw()};subOptions();draw()
}
async function docs(){
 setTitle("Documentation"); if(!docsData.length){try{docsData=sortDocs(await loadDocs(cfg),cfg)}catch(e){content.innerHTML=hero()+`<div class="error">Impossible de lire ${esc(cfg.docs.root)} via l'API GitHub : ${esc(e.message)}</div>${footer()}`;return}}
 const selected=state.doc||cfg.docs.homeDocument||docsData[0]?.relative;
 const item=docsData.find(x=>x.relative===selected)||docsData[0];
 content.innerHTML=`${hero()}<div class="wiki"><aside class="card wiki-tree"><strong>Documentation</strong><div style="margin-top:10px">${docsData.map(x=>{const depth=x.relative.split("/").length-1;return `<a class="doc-link ${x.relative===item?.relative?"active":""}" style="padding-left:${10+depth*14}px" href="#docs/${x.relative.split("/").map(encodeURIComponent).join("/")}">${iconHtml(depth?"file":"file")} ${esc(x.relative)}</a>`}).join("")}</div></aside><article id="doc-body" class="markdown">Chargement…</article></div>${footer()}`;
 if(item)try{$("#doc-body").innerHTML=markdown(await loadDoc(cfg,item))}catch(e){$("#doc-body").innerHTML=`<div class="error">Erreur de lecture : ${esc(e.message)}</div>`}
}
function thanks(){setTitle("Remerciements");const d=cfg.thanks||{};content.innerHTML=`${hero()}<div class="section-title"><div><h2>${esc(d.title||"Merci !")}</h2><p>${esc(d.text||"")}</p></div></div><div class="grid">${(d.items||[]).map(x=>`<div class="card feature"><div class="feature-icon">${iconHtml("heart")}</div><div><h3>${esc(x.name)}</h3><p>${esc(x.text||"")}</p>${x.url?`<a class="btn ghost" href="${esc(x.url)}" target="_blank" rel="noopener">Visiter ↗</a>`:""}</div></div>`).join("")}</div>${footer()}`}
function services(){setTitle("Services");const d=cfg.services||{};content.innerHTML=`${hero()}<div class="section-title"><div><h2>Services</h2><p>Vos raccourcis configurables.</p></div></div><div class="grid">${(d.items||[]).map(x=>`<a class="card feature" href="${esc(x.url||"#")}" target="_blank" rel="noopener"><div class="feature-icon">${iconHtml(x.icon||"link")}</div><div><h3>${esc(x.name)}</h3><p>${esc(x.description||"")}</p></div></a>`).join("")}</div>${footer()}`}
function about(){setTitle("About");const d=cfg.about||{};content.innerHTML=`${hero()}<div class="card" style="margin-top:16px"><h2>${esc(d.title||"À propos")}</h2><p class="muted" style="line-height:1.7">${esc(d.text||"")}</p></div><div class="grid" style="margin-top:14px">${(d.cards||[]).map(x=>`<div class="card"><h3>${esc(x.title)}</h3><p class="muted">${esc(x.text)}</p></div>`).join("")}</div>${footer()}`}
function footer(){if(cfg.footer?.enabled===false)return"";const f=cfg.footer||{};const links=(f.links||[]).map(x=>`<a href="${esc(x.url)}" ${x.newTab!==false?'target="_blank" rel="noopener"':''}>${esc(x.label)}</a>`).join(" • ");const badges=(f.badges||[]).map(b=>`<a href="${esc(b.href||"#")}" target="_blank" rel="noopener"><img src="${esc(b.image)}" alt="${esc(b.alt||b.label||"Badge")}"></a>`).join("");return `<footer class="footer"><div class="footer-row"><span>${esc(f.text||"")} ${f.showYear?`• ${new Date().getFullYear()}`:""} ${links?`• ${links}`:""}</span><div class="badges">${badges}</div></div></footer>`}
async function render(){
  nav(); const id=location.hash.replace(/^#/,"").split("/"); state.page=id[0]||cfg.site.defaultPage||"home"; if(state.page==="docs")state.doc=id.slice(1).map(decodeURIComponent).join("/");
  const exists=(cfg.navigation||[]).some(n=>n.id===state.page&&n.enabled!==false); if(!exists)state.page=cfg.site.defaultPage||"home";
  try{if(state.page==="home")await home();else if(state.page==="news")await news();else if(state.page==="downloads")downloads();else if(state.page==="store")await store();else if(state.page==="thanks")thanks();else if(state.page==="services")services();else if(state.page==="about")about();else if(state.page==="docs")await docs();else await home()}catch(e){content.innerHTML=`<div class="error">Une erreur est survenue : ${esc(e.message||e)}</div>`}
  document.querySelectorAll("[data-page]").forEach(a=>a.classList.toggle("active",a.dataset.page===state.page));
}
function theme(){document.documentElement.dataset.theme=state.theme}
async function init(){
 try{cfg=await loadConfig();repo=cfg.repository; if(cfg.themeColors) for(const [k,v] of Object.entries(cfg.themeColors)) document.documentElement.style.setProperty(`--${k.replace(/[A-Z]/g,m=>"-"+m.toLowerCase())}`,v); [profile,repository]=await Promise.all([cfg.profile?.enabled?getProfile(cfg):null,getRepo(cfg)]);
  if(repository?.default_branch && (cfg.repository.branch==="auto" || !cfg.repository.branch)) cfg.repository.branch=repository.default_branch;
  repo=cfg.repository; shell(); theme(); window.addEventListener("hashchange",render);$("#mobile-menu").onclick=()=>$("#sidebar").classList.toggle("open");$("#theme-toggle").onclick=()=>{state.theme=state.theme==="dark"?"light":"dark";document.body.classList.toggle("light",state.theme==="light")};await render()}catch(e){content.innerHTML=`<div class="error"><h2>evoX Core OS</h2><p>Impossible de charger la configuration.</p><pre>${esc(e.stack||e.message||e)}</pre></div>`}
}
init();
