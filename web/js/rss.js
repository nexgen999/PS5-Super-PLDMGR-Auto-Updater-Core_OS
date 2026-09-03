import {resolveUrl} from "./config.js";
import {discoverFiles} from "./github.js";
function textOf(el,selector){return el.querySelector(selector)?.textContent?.trim()||""}
function first(el,names){for(const n of names){const v=textOf(el,n);if(v)return v}return""}
function dateVal(v){const d=new Date(v);return Number.isNaN(d.getTime())?v:d}
export async function readFeed(feed,cfg){
  const url=resolveUrl(feed.url,cfg.repository);
  const r=await fetch(url,{cache:"no-store"}); if(!r.ok)throw new Error(`${r.status}`);
  const xml=await r.text(); const doc=new DOMParser().parseFromString(xml,"application/xml");
  if(doc.querySelector("parsererror"))throw new Error("RSS/XML invalide");
  return [...doc.querySelectorAll("item, entry")].map((el,i)=>{
    let link=el.querySelector("link")?.getAttribute("href")||textOf(el,"link")||textOf(el,"guid");
    const desc=first(el,["description","summary","content"]);
    const media=el.querySelector("media\:content, media\:thumbnail, enclosure");
    const image=media?.getAttribute("url")||el.querySelector("image url")?.textContent||"";
    return {id:`${feed.id}-${i}-${link}`,source:feed.label,title:first(el,["title"])||"Sans titre",description:desc.replace(/<[^>]*>/g," ").replace(/\s+/g," ").trim(),link,date:dateVal(first(el,["pubDate","published","updated","dc\:date"])),image};
  }).filter(x=>x.title);
}
export async function readAllFeeds(cfg){
  let feeds=(cfg.news.feeds||[]).filter(f=>f.enabled!==false); const errors=[];
  if(cfg.news.autoDiscover){
    try{
      const discovered=await discoverFiles(cfg,cfg.paths.rssDir||"/rss/",".xml");
      const known=new Set(feeds.map(f=>resolveUrl(f.url,cfg.repository)));
      for(const f of discovered){const url=resolveUrl("/"+f.path,cfg.repository);if(!known.has(url))feeds.push({id:f.path,label:f.path.split("/").pop(),url:"/"+f.path,enabled:true})}
    }catch(e){errors.push({feed:"auto-discovery RSS",error:e.message||"Erreur"})}
  }
  const results=await Promise.allSettled(feeds.map(f=>readFeed(f,cfg)));
  const items=[]; results.forEach((r,i)=>r.status==="fulfilled"?items.push(...r.value):errors.push({feed:feeds[i].label,error:r.reason?.message||"Erreur"}));
  items.sort((a,b)=>new Date(b.date)-new Date(a.date));
  return {items:items.slice(0,cfg.news.maxItems||20),errors};
}
