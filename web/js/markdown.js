function esc(s){return s.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}
export function markdown(md){
  let s=esc(md.replace(/\r/g,""));
  const blocks=[];
  s=s.replace(/```([\w+-]*)\n([\s\S]*?)```/g,(_,lang,code)=>{blocks.push(`<pre><code class="language-${lang}">${code.trim()}</code></pre>`);return `@@BLOCK${blocks.length-1}@@`});
  s=s.replace(/^###### (.+)$/gm,"<h6>$1</h6>").replace(/^##### (.+)$/gm,"<h5>$1</h5>").replace(/^#### (.+)$/gm,"<h4>$1</h4>").replace(/^### (.+)$/gm,"<h3>$1</h3>").replace(/^## (.+)$/gm,"<h2>$1</h2>").replace(/^# (.+)$/gm,"<h1>$1</h1>");
  s=s.replace(/^> (.+)$/gm,"<blockquote>$1</blockquote>");
  s=s.replace(/^[-*] (.+)$/gm,"<li>$1</li>").replace(/(<li>.*<\/li>\n?)+/g,m=>`<ul>${m}</ul>`);
  s=s.replace(/^\d+\. (.+)$/gm,"<li>$1</li>");
  s=s.replace(/!\[([^\]]*)\]\(([^)]+)\)/g,'<img alt="$1" src="$2">');
  s=s.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
  s=s.replace(/`([^`]+)`/g,"<code>$1</code>").replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/__([^_]+)__/g,"<strong>$1</strong>").replace(/\*([^*]+)\*/g,"<em>$1</em>");
  s=s.split(/\n{2,}/).map(x=>/^<(h[1-6]|ul|blockquote|pre|img)/.test(x.trim())?x:`<p>${x.replace(/\n/g,"<br>")}</p>`).join("");
  blocks.forEach((b,i)=>{s=s.replace(`@@BLOCK${i}@@`,b)});
  return s;
}
