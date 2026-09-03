import {getDocsTree,rawDocUrl} from "./github.js";
export async function loadDocs(cfg){return await getDocsTree(cfg)}
export async function loadDoc(cfg,item){
  const url=rawDocUrl(cfg,item.path);
  const r=await fetch(url,{cache:"no-store"});if(!r.ok)throw new Error(`${r.status}`);
  return await r.text();
}
export function sortDocs(items,cfg){
  const order=cfg.docs.order||[];
  const rank=p=>{const i=order.indexOf(p);return i<0?99999:i};
  return [...items].sort((a,b)=>rank(a.relative)-rank(b.relative)||a.relative.localeCompare(b.relative));
}
