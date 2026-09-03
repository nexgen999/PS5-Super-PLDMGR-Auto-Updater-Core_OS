import {resolveUrl} from "./config.js";
import {discoverFiles} from "./github.js";
const first=(o,keys)=>{for(const k of keys||[]){if(o?.[k]!==undefined&&o[k]!==null&&String(o[k]).trim()!=="")return o[k]}return""};
function arr(data,keys){if(Array.isArray(data))return data; for(const k of keys||[])if(Array.isArray(data?.[k]))return data[k]; return Object.values(data||{}).find(Array.isArray)||[]}
export async function loadStore(cfg){
  let sources=(cfg.store.sources||[]).filter(s=>s.enabled!==false);
  const errors=[];
  if(cfg.store.autoDiscover){
    try{
      const discovered=await discoverFiles(cfg,cfg.paths.jsonDir||"/json/",".json");
      const known=new Set(sources.map(s=>resolveUrl(s.url,cfg.repository)));
      for(const f of discovered){
        const url=resolveUrl("/"+f.path,cfg.repository);
        if(!known.has(url))sources.push({id:f.path,label:f.path.split("/").pop(),type:"json",url:"/"+f.path,arrayKeys:["items","data","payloads","packages","apps","applications","files","ffpfsc"]});
      }
    }catch(e){errors.push({source:"auto-discovery JSON",error:e.message||"Erreur"})}
  }
  const out=[];
  for(const src of sources){
    try{
      const r=await fetch(resolveUrl(src.url,cfg.repository),{cache:"no-store"}); if(!r.ok)throw new Error(`${r.status}`);
      const data=await r.json();
      arr(data,src.arrayKeys).forEach((raw,i)=>{
        const m=cfg.store.fieldMap||{}, local=first(raw,m.filename)||"";
        let sub=first(raw,m.subcategory)||"";
        if(!sub && cfg.store.subcategory?.inferFromPath && local){
          const parts=local.replaceAll("\\","/").split("/").filter(Boolean);
          const n=Number(cfg.store.subcategory.pathSegments||1); sub=parts[n]||"";
        }
        out.push({id:`${src.id}-${i}`,source:src.label,sourceId:src.id,name:String(first(raw,m.name)||"Unnamed"),filename:String(local),url:String(first(raw,m.url)||""),description:String(first(raw,m.description)||""),version:String(first(raw,m.version)||""),author:String(first(raw,m.author)||""),category:String(first(raw,m.category)||src.label),subcategory:String(sub),icon:String(first(raw,m.icon)||""),checksum:String(first(raw,m.checksum)||""),raw});
      });
    }catch(e){errors.push({source:src.label,error:e.message||"Erreur"})}
  }
  return {items:out,errors};
}
