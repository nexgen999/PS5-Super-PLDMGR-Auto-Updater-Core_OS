export async function githubFetch(url,timeout=12000){
  const c=new AbortController(); const t=setTimeout(()=>c.abort(),timeout);
  try{const r=await fetch(url,{headers:{Accept:"application/vnd.github+json"},signal:c.signal}); if(!r.ok)throw new Error(`${r.status} ${r.statusText}`); return await r.json();}
  finally{clearTimeout(t)}
}
const apiBase=cfg=>(cfg.repository.apiBase||"https://api.github.com").replace(/\/$/,"");
export async function getProfile(cfg){
  if(!cfg.repository.owner)return null;
  return githubFetch(`${apiBase(cfg)}/users/${encodeURIComponent(cfg.repository.owner)}`,cfg.advanced.requestTimeoutMs);
}
export async function getRepo(cfg){
  if(!cfg.repository.owner||!cfg.repository.name)return null;
  return githubFetch(`${apiBase(cfg)}/repos/${encodeURIComponent(cfg.repository.owner)}/${encodeURIComponent(cfg.repository.name)}`,cfg.advanced.requestTimeoutMs);
}
export async function getTree(cfg){
  if(!cfg.repository.owner||!cfg.repository.name)return [];
  const branch=cfg.repository.branch||"main";
  const data=await githubFetch(`${apiBase(cfg)}/repos/${encodeURIComponent(cfg.repository.owner)}/${encodeURIComponent(cfg.repository.name)}/git/trees/${encodeURIComponent(branch)}?recursive=1`,cfg.advanced.requestTimeoutMs);
  return data.tree||[];
}
export async function discoverFiles(cfg,folder,extension){
  const root=(folder||"/").replace(/^\//,"").replace(/\/$/,"");
  return (await getTree(cfg)).filter(x=>x.type==="blob"&&x.path.toLowerCase().endsWith(extension.toLowerCase())&&(x.path===root||x.path.startsWith(root+"/")));
}
export async function getDocsTree(cfg){
  const root=(cfg.docs.root||"/docs/").replace(/^\//,"").replace(/\/$/,"");
  return (await discoverFiles(cfg,root,".md")).map(x=>({...x,relative:x.path.slice(root.length).replace(/^\//,"")})).filter(x=>!(cfg.docs.hideFiles||[]).some(h=>x.path.endsWith(h)));
}
export function rawDocUrl(cfg,path){
  return `https://raw.githubusercontent.com/${cfg.repository.owner}/${cfg.repository.name}/${cfg.docs.branch||cfg.repository.branch||"main"}/${path}`;
}
