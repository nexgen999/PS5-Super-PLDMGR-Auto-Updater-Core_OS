const CONFIG_URL="./web/data/config.json";
const isHttp=s=>/^https?:\/\//i.test(s||"");
function githubGuess(){
  const host=location.hostname;
  const path=location.pathname.split("/").filter(Boolean);
  if(host.endsWith(".github.io")){
    const owner=host.split(".")[0];
    const repo=path[0] || `${owner}.github.io`;
    return {owner,repo};
  }
  return {owner:"",repo:""};
}
export function detectRepository(cfg){
  const guess=githubGuess();
  const owner=cfg.repository.owner || (cfg.autoDetect.enabled&&cfg.autoDetect.owner?guess.owner:"");
  const name=cfg.repository.name || (cfg.autoDetect.enabled&&cfg.autoDetect.repository?guess.repo:"");
  const branch=cfg.repository.branch || cfg.autoDetect.branch || "main";
  let basePath="/";
  if(cfg.repository.pagesUrl){
    try{basePath=new URL(cfg.repository.pagesUrl,location.href).pathname.replace(/\/?$/,"/")}catch{}
  }else{
    const p=location.pathname.split("/").filter(Boolean);
    if(location.hostname.endsWith(".github.io") && p.length && p[0]===name) basePath=`/${p[0]}/`;
    else if(location.hostname.endsWith(".github.io") && name===`${owner}.github.io`) basePath="/";
    else basePath="/";
  }
  const origin=location.origin;
  const baseUrl=cfg.repository.baseUrl || `${origin}${basePath}`;
  const githubUrl=cfg.repository.githubUrl || (owner&&name?`https://github.com/${owner}/${name}`:"");
  return {...cfg.repository,owner,name,branch,basePath,baseUrl:baseUrl.replace(/\/?$/,"/"),githubUrl};
}
export function resolveUrl(value,repo){
  if(!value)return "";
  if(isHttp(value))return value;
  const clean=value.replace(/^\//,"");
  return new URL(clean,repo.baseUrl).href;
}
export async function loadConfig(){
  const res=await fetch(CONFIG_URL,{cache:"no-store"});
  if(!res.ok)throw new Error(`Configuration introuvable (${res.status})`);
  const cfg=await res.json();
  cfg.repository=detectRepository(cfg);
  cfg.paths=cfg.paths||{};
  return cfg;
}
