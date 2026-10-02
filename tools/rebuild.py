#!/usr/bin/env python3
"""Rebuild the reading files from pinned texts, reviewed mappings and TIPNR metadata.
Python 3 standard library only. No network access; source data remain unchanged.
"""
from pathlib import Path
import collections,gzip,json,re
ROOT=Path(__file__).resolve().parents[1]
LANGS=('English','中文','Français','Deutsch','Italiano','Latina')
VERSIONS={'Français':'lsg','Deutsch':'luth1912','Italiano':'diodati','Latina':'vulg'}
def read(name):return json.loads(gzip.decompress((ROOT/'data'/name).read_bytes()))
def clean(t,slug=''):
 t=re.sub(r'\s+',' ',t).strip().replace('\\|','|')
 if slug=='lsg':t=t.replace("''", "'")
 if slug=='vulg':
  t=re.sub(r'%\s*([A-Za-z]+);?',r'\1',t)
  if t and t[0].islower():t=t[0].upper()+t[1:]
 return t
BOOKS=json.loads((ROOT/'data/books.json').read_text()); BOOK={b['osis']:b for b in BOOKS}; ORDER={b['osis']:i for i,b in enumerate(BOOKS)}
def sortkey(k):return ORDER.get(k[0],99),k[1],k[2]
def path(k):
 b,c=k[:2];m=BOOK[b];return f"{m['directory']}/{m['name']} {c:0{len(str(len(m['verses'])))}d}"
def label(k):return f"{BOOK.get(k[0],{'name':k[0]})['name']} {k[1]}:{k[2]}"
def wiki(k):return f'[[{path(k)}#{k[2]}|{label(k)}]]'
BASE={tuple(r['ref']):{la:r[la] for la in ('English','中文')} for r in read('bilingual-base.json.gz')}
TEXT={s:{tuple(r['ref']):r['text'] for r in d} for s,d in read('source-texts.json.gz').items()}
MAP={s:{tuple(r['source']):r for r in d} for s,d in read('alignment.json.gz').items()}
HEADS={tuple(r['ref']):r['text'] for r in json.loads((ROOT/'data/headings.json').read_text())}
CHINESE_JOINS=json.loads((ROOT/'data/chinese-joins.json').read_text())
CHINESE_MERGES=json.loads((ROOT/'data/chinese-merge-refs.json').read_text())
NAMES=read('name-index.json.gz');byref=collections.defaultdict(list);byname=collections.defaultdict(list)
for rec in NAMES:
 for k in rec['refs']:byref[tuple(k)].append(rec)
 byname[rec['name']].append(rec)
def folder(rec):return 'People' if rec['category']=='PERSON(s)' else 'Places' if rec['category']=='PLACE' else 'Names'
# A name shared by people and places has a separate destination for each category.
used=collections.defaultdict(lambda:collections.defaultdict(set)); seen_records=collections.defaultdict(dict);links_count=collections.Counter()
def link_text(t,la,refs):
 candidates=collections.defaultdict(set)
 for k in refs:
  for rec in byref.get(k,[]):
   dest=folder(rec)+'/'+rec['name']
   for word in rec['spellings'].get(la,[]):
    if la=='中文' and len(word)<2:continue
    if len(word)<2:continue
    candidates[word].add(dest)
   seen_records[dest][rec['id']]=rec
 candidates={w:next(iter(ds)) for w,ds in candidates.items() if len(ds)==1}
 if not candidates:return t
 pat=re.compile('|'.join(re.escape(w) for w in sorted(candidates,key=len,reverse=True)))
 def sub(m):
  a,b=m.span();word=m[0]
  if (a>0 and t[a-1]=='[') or (b<len(t) and t[b]==']'):return word
  if la!='中文' and ((a>0 and t[a-1].isalpha()) or (b<len(t) and t[b].isalpha())):return word
  dest=candidates[word];used[dest][la].add(word);links_count[la]+=1
  return '[['+dest+'|'+word+']]'
 return pat.sub(sub,t)
# Each original source segment appears exactly once in the reading text or supplement.
render=collections.defaultdict(lambda:collections.defaultdict(list));titles=collections.defaultdict(list);appendix=collections.defaultdict(list);coverage=[];gaps=[]
for la,slug in VERSIONS.items():
 for src,text in TEXT[slug].items():
  m=MAP[slug][src];dest=[tuple(x) for x in m['to']];normal=sorted({x for x in dest if x in BASE},key=sortkey)
  if normal:
   anchor=normal[0]; rendered=link_text(clean(text,slug),la,normal)
   if src!=anchor or len(normal)>1:
    note='原编号 '+label(src)
    if len(normal)>1:note+='；合读对应 '+', '.join(label(k) for k in normal)
    rendered='〔'+note+'〕 '+rendered
   render[anchor][la].append((src,rendered))
   for k in normal[1:]:render[k][la].append((src,'〔合读见 '+wiki(anchor)+'；原编号 '+label(src)+'〕'))
   coverage.append((slug,src,'chapter',anchor))
  elif dest and all(k[2]==0 and k[0] in BOOK for k in dest):
   anchor=dest[0];titles[anchor[:2]].append(la+': 〔原编号 '+label(src)+'〕 '+clean(text,slug));coverage.append((slug,src,'title',anchor))
  else:
   appendix[slug].append((src,clean(text,slug)));coverage.append((slug,src,'appendix',src))
for k in sorted(BASE,key=sortkey):
 for la in LANGS:
  if la in ('English','中文'):
   t=BASE[k][la]
   if t=='*':
    gapinfo=CHINESE_JOINS;dest=tuple(gapinfo[':'.join(map(str,k))]);t='〔合读见 '+wiki(dest)+'〕'
   else:
    prefix='〔与相邻节的切句边界不同〕 ' if t.startswith('*') else ''
    merged=CHINESE_MERGES if la=='中文' else {}
    refs=[k]+[tuple(x) for x in merged.get(':'.join(map(str,k)),[])]
    t=prefix+link_text(clean(t.lstrip('*')),la,refs)
   render[k][la]=[(k,t)]
  elif not render[k][la]:
   t='〔所据数字底本此处无独立文本；见 [[Audit/校勘说明#拉丁语底本空缺|校勘说明]]〕'
   render[k][la]=[(k,t)];gaps.append({'ref':k,'language':la,'reason':'source-absence'})
# Rebuild each of the 1,189 chapters.
for book in BOOKS:
 b=book['osis']
 for c,n in enumerate(book['verses'],1):
  out=[HEADS.get((b,c),f"# {book['name']} {c} / 约翰一书 {c}"),'']
  if titles[b,c]:out+=['### 篇题（原文保留）','',*sum(([t,''] for t in titles[b,c]),[])]
  for v in range(1,n+1):
   k=(b,c,v);out+=['## '+str(v),'']
   for la in LANGS:out+=[la+': '+' '.join(t for _,t in sorted(render[k][la],key=lambda x:sortkey(x[0]))),'']
  (ROOT/(path((b,c,1))+'.md')).write_text('\n'.join(out),encoding='utf-8')
for slug,entries in appendix.items():
 (ROOT/'Appendix').mkdir(exist_ok=True)
 out=['# 拉丁语底本附加段落','', '以下原文在本项目所据拉丁语数字底本中存在，超出 KJV 66 卷对应范围；单独保留，不删去、不移入无关节。章、节均为来源编号。','']
 for k,t in sorted(entries,key=lambda x:sortkey(x[0])):out+=['## '+label(k),'',t,'']
 (ROOT/'Appendix'/f'{slug}.md').write_text('\n'.join(out))
# Restore source-supported former empty entries even if spelling matching linked no occurrence.
oldnames=set(json.loads((ROOT/'Audit/original-empty-entries.json').read_text()))
for name,recs in byname.items():
 if name not in oldnames and not any(folder(r)+'/'+name in used for r in recs):continue
 for rec in recs:seen_records[folder(rec)+'/'+name][rec['id']]=rec
indexes=collections.defaultdict(list)
for dest,recs in sorted(seen_records.items()):
 if dest not in used and dest.split('/',1)[1] not in oldnames:continue
 folder_name,name=dest.split('/',1);(ROOT/folder_name).mkdir(exist_ok=True)
 out=['# '+name,'','这是按名称检索的索引；同名人物或地点按来源标识分列，不据拼写相同认定为同一对象。','']
 if used[dest]:out+=['经文中已核定的显示形式：'+'；'.join(la+'：'+', '.join(sorted(ws)) for la,ws in used[dest].items())+'。','']
 for rec in sorted(recs.values(),key=lambda x:x['id']):
  out+=['## '+rec['id'],'', '类别：'+rec['category']+'。来源描述：'+rec['description'],'']
  refs=sorted({tuple(k) for k in rec['refs'] if tuple(k) in BASE},key=sortkey)
  out+=['经文索引：'+'、'.join(wiki(k) for k in refs)+'。','']
 out+=['来源：[STEPBible TIPNR](https://github.com/STEPBible/STEPBible-Data/tree/master/Proper%20Nouns)，CC BY 4.0。分类、身份标识和经节取自来源；此页重新编排，中文提示及拼写筛选由本项目添加。','']
 (ROOT/(dest+'.md')).write_text('\n'.join(out));indexes[folder_name].append(name)
for f,names in indexes.items():
 title={'People':'人物名称索引','Places':'地名索引','Names':'其他专名索引'}[f]
 out=['# '+title,'',f'共 {len(names)} 个名称索引。根据 STEPBible TIPNR 分类；同名者在页内分列。链接只在有经节依据、显示形式可核对时建立。','']
 out += ['- [['+f+'/'+n+'|'+n+']]' for n in names]
 (ROOT/f/'README.md').write_text('\n'.join(out)+'\n')
# Remove only stale generated notes after a rebuild, never a handwritten note.
for f,names in indexes.items():
 for p in (ROOT/f).glob('*.md'):
  if p.stem not in set(names)|{'README'} and '此页重新编排，中文提示及拼写筛选由本项目添加。' in p.read_text():p.unlink()
(ROOT/'Audit/source-coverage.json.gz').write_bytes(gzip.compress(json.dumps(coverage,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
(ROOT/'Audit/source-gaps.json').write_text(json.dumps(gaps,ensure_ascii=False,indent=2)+'\n')
(ROOT/'Audit/build-summary.json').write_text(json.dumps({'chapters':1189,'verses':len(BASE),'source_segments':{s:len(x) for s,x in TEXT.items()},'links':dict(links_count),'indexes':{s:len(x) for s,x in indexes.items()},'source_absences':len(gaps),'appendix_segments':{s:len(x) for s,x in appendix.items()}},ensure_ascii=False,indent=2)+'\n')
print((ROOT/'Audit/build-summary.json').read_text())
