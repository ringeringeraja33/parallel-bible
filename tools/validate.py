#!/usr/bin/env python3
"""Check the full canon, all language rows, links and preservation of input texts."""
import collections,gzip,json,re,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LANGS=['English','中文','Français','Deutsch','Italiano','Latina']
def data(name):return json.loads(gzip.decompress((ROOT/'data'/name).read_bytes()))
def plain(t):return re.sub(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]',lambda m:m[2] or m[1].split('/')[-1],t)
def clean(t,s=''):
 t=re.sub(r'\s+',' ',t).strip().replace('\\|','|')
 if s=='lsg':t=t.replace("''", "'")
 if s=='vulg':
  t=re.sub(r'%\s*([A-Za-z]+);?',r'\1',t)
  if t and t[0].islower():t=t[0].upper()+t[1:]
 return t
books=json.loads((ROOT/'data/books.json').read_text()); book={b['osis']:b for b in books}
def file(k):
 b,c=k[:2];m=book[b];return ROOT/m['directory']/f"{m['name']} {c:0{len(str(len(m['verses'])))}d}.md"
expected={(b['osis'],c,v) for b in books for c,n in enumerate(b['verses'],1) for v in range(1,n+1)}
errors=[];rows={};chapters=0;contents={};headings={}
for b in books:
 for c,n in enumerate(b['verses'],1):
  p=file((b['osis'],c));chapters+=1
  if not p.exists():errors.append('Missing chapter '+str(p.relative_to(ROOT)));continue
  t=p.read_text();contents[p]=t
  secs=re.findall(r'^## (\d+)\n(.*?)(?=^## |\Z)',t,re.M|re.S)
  if [int(v) for v,_ in secs]!=list(range(1,n+1)):errors.append('Invalid verse sequence '+str(p.relative_to(ROOT)))
  for v,sec in secs:
   found=re.findall(r'^(English|中文|Français|Deutsch|Italiano|Latina): (.*)$',sec,re.M)
   k=(b['osis'],c,int(v));rows[k]=dict(found)
   if [la for la,_ in found]!=LANGS or any(not x.strip() for _,x in found):errors.append('Invalid language rows '+str(k))
   if any(x.strip()=='*' for _,x in found):errors.append('Unexplained placeholder '+str(k))
if set(rows)!=expected:errors.append('Coordinate set mismatch')
# Compare every English verse against an independently acquired CrossWire witness.
ref=data('bilingual-reference.json.gz');kr={tuple(x['ref']):x['text'] for x in ref['English']}
for k,v in rows.items():
 if plain(v['English'])!=clean(kr[k]):errors.append('English changed/lost '+str(k))
# Every original Chinese segment is retained, or represented by an explicit documented join.
zh={tuple(x['ref']):x['text'] for x in ref['中文']};joins=json.loads((ROOT/'data/chinese-joins.json').read_text())
for k,t in zh.items():
 if t in ('','a','并入上节'):continue
 anchor=('3John',1,14) if k==('3John',1,15) else ('Rev',13,1) if k==('Rev',12,18) else k
 if t not in plain(rows[anchor]['中文']):errors.append('Chinese source segment lost '+str(k))
for k,target in joins.items():
 kk=k.split(':');kk=(kk[0],int(kk[1]),int(kk[2]))
 if '合读见' not in rows[kk]['中文'] or tuple(target) not in rows:errors.append('Invalid Chinese join '+k)
# Check all four added translations against retained source snapshots at their actual output locations.
coverage=json.loads(gzip.decompress((ROOT/'Audit/source-coverage.json.gz').read_bytes()));source=data('source-texts.json.gz');count=collections.Counter();lang={'lsg':'Français','luth1912':'Deutsch','diodati':'Italiano','vulg':'Latina'}
lookup={(s,tuple(r['ref'])):r['text'] for s,rr in source.items() for r in rr}
for s,src,kind,dest in coverage:
 key=(s,tuple(src));count[key]+=1;t=clean(lookup[key],s)
 if kind=='chapter':out=plain(rows[tuple(dest)][lang[s]])
 elif kind=='title':out=plain(contents[file(tuple(dest))].split('\n## 1\n')[0])
 elif kind=='appendix':out=(ROOT/'Appendix'/f'{s}.md').read_text()
 else:errors.append('Unknown coverage kind '+kind);continue
 if t not in out:errors.append('Source segment lost '+str(key))
if set(count)!=set(lookup) or any(v!=1 for v in count.values()):errors.append('Source segment coverage is not one-to-one')
# Resolve every wiki-link and its heading anchor, including notes and supplements.
allmd={p.relative_to(ROOT).with_suffix('').as_posix():p for p in ROOT.rglob('*.md') if '.git' not in p.parts}
links=0
for p in allmd.values():
 t=p.read_text();headings[p]={x.strip() for x in re.findall(r'^#{1,6} (.+)$',t,re.M)}
for p in allmd.values():
 # Fenced examples in README are deliberately not treated as live links.
 t=re.sub(r'```.*?```','',p.read_text(),flags=re.S)
 for target in re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]',t):
  links+=1;parts=target.split('#',1);base=parts[0]
  if base not in allmd:errors.append('Broken link '+target+' in '+str(p.relative_to(ROOT)))
  elif len(parts)==2 and parts[1] not in headings[allmd[base]]:errors.append('Broken heading '+target)
# Regression examples cover previously wrong joins, missing verses and false-positive linking.
checks=[(('Gen',1,3),'Italiano','[[People/Sia|',False),(('1John',5,21),'English','Little children',True),(('1Chr',22,1),'English','Then David said',True),(('Matt',28,7),'中文','快去告诉',True),(('Ps',51,1),'Latina','Miserere',True),(('Ruth',4,22),'Latina','Isai genuit David',True),(('Amos',9,15),'Latina','plantabo',True)]
for k,la,needle,present in checks:
 if (needle in plain(rows[k][la]) if present else needle in rows[k][la])!=present:errors.append('Regression '+str((k,la,needle)))
# Detect accidental changes to fixed source data or checked mappings.
manifest=ROOT/'data/checksums.json'
if manifest.exists():
 for name,digest in json.loads(manifest.read_text()).items():
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:errors.append('Pinned input changed '+name)
report={'passed':not errors,'books':len(books),'chapters':chapters,'verses':len(rows),'language_rows':len(rows)*6,'source_segments_verified':len(count),'chinese_source_records':len(zh),'wiki_links_verified':links,'known_latin_source_absences':len(json.loads((ROOT/'Audit/source-gaps.json').read_text())),'errors':errors}
(ROOT/'Audit/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(bool(errors))
