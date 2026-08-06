"""
Full Web Server with all 21 module outputs + 5 blueprint outputs.
Real-time data integration. Run: python server.py
"""
import sys,os,json,traceback,urllib.request,urllib.parse,re
from pathlib import Path
from flask import Flask,request,jsonify,Response
sys.path.insert(0,str(Path(__file__).parent))
from intent_entity_platform.core.engine import PlatformEngine
from intent_entity_platform.core.input_framework import (
    InputFramework,SeedKeywordInput,FirstPartyData,SMEAsset,
    BrandConstraints,AudienceProfile,TechnicalCredentials
)
from intent_entity_platform.utils.web_data import web_search as _real_web_search

import random,time,smtplib,io,datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether,PageBreak,HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

MAIL_CONFIG={}
try:
    _mail_cfg_path=Path(__file__).parent/'mail_config.json'
    if _mail_cfg_path.exists():
        MAIL_CONFIG.update(json.loads(_mail_cfg_path.read_text(encoding='utf-8')))
except Exception:
    pass

def _mail_setting(key,env,default=None):
    v=os.environ.get(env)
    if v: return v
    v=MAIL_CONFIG.get(key)
    return v if v is not None else default

_OTP_STORE={}
_OTP_TTL=600
_OTP_MAX_TRIES=5
_OTP_MAX_REQUESTS=3
_OTP_WINDOW=600
_EMAIL_RE=re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

def _send_email(to_addr,subject,html_body,attach_name=None,attach_bytes=None):
    host=_mail_setting('smtp_host','SMTP_HOST','')
    if not host:
        raise RuntimeError('SMTP is not configured. Fill mail_config.json (smtp_host/smtp_user/smtp_pass) or set SMTP_HOST/SMTP_USER/SMTP_PASS environment variables.')
    port=int(_mail_setting('smtp_port','SMTP_PORT','587'))
    user=_mail_setting('smtp_user','SMTP_USER','')
    pwd=_mail_setting('smtp_pass','SMTP_PASS','')
    frm=_mail_setting('smtp_from','SMTP_FROM',user or host)
    use_tls=str(_mail_setting('smtp_use_tls','SMTP_USE_TLS','true')).lower() in ('1','true','yes')
    msg=MIMEMultipart('alternative')
    msg['Subject']=subject
    msg['From']=frm
    msg['To']=to_addr
    msg.attach(MIMEText(html_body,'html','utf-8'))
    if attach_name and attach_bytes:
        part=MIMEApplication(attach_bytes,name=attach_name)
        part.add_header('Content-Disposition','attachment',filename=attach_name)
        msg.attach(part)
    server=smtplib.SMTP(host,int(port),timeout=30)
    server.ehlo()
    if use_tls:
        server.starttls()
        server.ehlo()
    if user:
        server.login(user,pwd)
    try:
        server.sendmail(frm,[to_addr],msg.as_string())
    finally:
        try: server.quit()
        except Exception: pass

_PDF_HAS_SEGOE=False
_PDF_MONO='Courier'
try:
    _segoe=os.path.join(os.environ.get('WINDIR',r'C:\Windows'),'Fonts')
    if os.path.exists(os.path.join(_segoe,'segoeui.ttf')):
        pdfmetrics.registerFont(TTFont('SegoeUI',os.path.join(_segoe,'segoeui.ttf')))
        pdfmetrics.registerFont(TTFont('SegoeUI-Bold',os.path.join(_segoe,'segoeuib.ttf')))
        _PDF_HAS_SEGOE=True
    if os.path.exists(os.path.join(_segoe,'consola.ttf')):
        pdfmetrics.registerFont(TTFont('Consolas',os.path.join(_segoe,'consola.ttf')))
        _PDF_MONO='Consolas'
except Exception:
    pass

def _F(bold=False):
    if _PDF_HAS_SEGOE:
        return 'SegoeUI-Bold' if bold else 'SegoeUI'
    return 'Helvetica-Bold' if bold else 'Helvetica'

_MODULE_NAMES={
    'M01':'SERP & Knowledge Graph','M02':'GEO & AEO Simulator','M03':'Semantic Structure & Schema',
    'M04':'E-E-A-T Gap Profiler','M05':'Internal Link & Cannibalization','M06':'Fluff & Cliche Decoder',
    'M07':'Citation & Source Verifier','M08':'Multimodal Asset Blueprint','M09':'GEO Tracker',
    'M10':'CSR Simulator','M11':'RAG Tester','M12':'Brand Compliance Engine','M13':'Schema Payload Generator',
    'M14':'Intent & Bounce Predictor','M15':'Content Decay Engine','M16':'CDN Edge Previewer',
    'M17':'A/B Testing Engine','M18':'Indexing Sentinel','M19':'Localization Sync',
    'M20':'Digital PR Engine','M21':'DOM Inspector'
}

def _esc_pdf(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def _pretty(k):
    return _esc_pdf(str(k).replace('_',' ').replace('-',' ')).title()

def _txt(x,limit=160):
    if isinstance(x,(dict,list)):
        try: x=json.dumps(x,ensure_ascii=False)[:limit]
        except Exception: x=str(x)
    s=_esc_pdf(x)
    if len(s)>limit: s=s[:limit]+'...'
    return s

def _make_styles():
    reg=_F(False); regb=_F(True)
    return {
        'title':ParagraphStyle('t',fontName=regb,fontSize=20,leading=25,textColor=HexColor('#1e1b4b'),spaceAfter=2),
        'tbrand':ParagraphStyle('tb',fontName=reg,fontSize=9.5,leading=12,textColor=HexColor('#7c5cfc'),spaceAfter=4),
        'sub':ParagraphStyle('sub',fontName=reg,fontSize=9,leading=13,textColor=HexColor('#415070'),spaceAfter=2),
        'h2':ParagraphStyle('h2',fontName=regb,fontSize=13.5,leading=17,textColor=HexColor('#5b21b6'),spaceBefore=12,spaceAfter=3),
        'h3':ParagraphStyle('h3',fontName=regb,fontSize=10.5,leading=14,textColor=HexColor('#0e7490'),spaceBefore=7,spaceAfter=3),
        'body':ParagraphStyle('body',fontName=reg,fontSize=8.8,leading=12.5,textColor=HexColor('#1f2937'),spaceAfter=2,splitLongWords=1),
        'cell':ParagraphStyle('cell',fontName=reg,fontSize=7.8,leading=10.5,textColor=HexColor('#1f2937'),splitLongWords=1),
        'th':ParagraphStyle('th',fontName=regb,fontSize=8,leading=11,textColor=HexColor('#ffffff'),splitLongWords=1),
        'note':ParagraphStyle('note',fontName=reg,fontSize=7.8,leading=10,textColor=HexColor('#6b7280'),spaceBefore=3),
        'statlbl':ParagraphStyle('sl',fontName=reg,fontSize=7.5,leading=9.5,textColor=HexColor('#6b7280'),alignment=1),
        'statval':ParagraphStyle('sv',fontName=regb,fontSize=15,leading=19,textColor=HexColor('#5b21b6'),alignment=1),
        'raw':ParagraphStyle('raw',fontName=_PDF_MONO,fontSize=6,leading=7.5,textColor=HexColor('#374151'),splitLongWords=1),
    }

def _pdf_footer(canvas,doc):
    canvas.saveState()
    page_h=doc.pagesize[1]
    canvas.setStrokeColor(HexColor('#d6def2'))
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin,page_h-doc.topMargin-2,doc.width+doc.leftMargin,page_h-doc.topMargin-2)
    canvas.setFont(_F(False),7)
    canvas.setFillColor(HexColor('#94a3b8'))
    canvas.drawString(doc.leftMargin,doc.bottomMargin-14,'Intent, Entity & Semantic Intelligence Platform')
    canvas.drawRightString(doc.width+doc.leftMargin,doc.bottomMargin-14,'Page %d'%(doc.page))
    canvas.restoreState()

def _add_heading(story,styles,text,kind='h2'):
    story.append(KeepTogether([Paragraph(text,styles[kind])]))

def _add_table(story,rows,styles,width,maxrows=30):
    if not rows: return
    keys=[];seen=set()
    for r in rows:
        if isinstance(r,dict):
            for k in r:
                if k not in seen: seen.add(k); keys.append(k)
    if not keys:
        for i in rows[:maxrows]:
            story.append(Paragraph('&#8226; '+_txt(i),styles['body']))
        return
    all_keys=keys
    if len(keys)>6: keys=keys[:6]
    data=[[Paragraph(_pretty(k),styles['th']) for k in keys]]
    for r in rows[:maxrows]:
        data.append([Paragraph(_txt(r.get(k,'')),styles['cell']) for k in keys])
    t=Table(data,repeatRows=1,colWidths=[width/len(keys)]*len(keys),hAlign='LEFT')
    cmds=[
        ('GRID',(0,0),(-1,-1),0.4,HexColor('#cbd5e1')),
        ('BACKGROUND',(0,0),(-1,0),HexColor('#5b21b6')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),5),
        ('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]
    for i in range(1,len(data)):
        if i%2==0:
            cmds.append(('BACKGROUND',(0,i),(-1,i),HexColor('#f5f7ff')))
    t.setStyle(TableStyle(cmds))
    story.append(t)
    notes=[]
    if len(rows)>maxrows:
        notes.append('+ %d more rows (full details in the JSON appendix)'%(len(rows)-maxrows))
    if len(all_keys)>len(keys):
        notes.append('+ %d more fields (full details in the JSON appendix)'%(len(all_keys)-len(keys)))
    if notes:
        story.append(Paragraph(' &nbsp; '.join(notes),styles['note']))

def _add_content(story,data,styles,depth=0):
    if depth>4: return
    if isinstance(data,dict):
        for k,v in data.items():
            if k in ('raw_html',): continue
            if isinstance(v,dict):
                _add_heading(story,styles,_pretty(k),'h3')
                _add_content(story,v,styles,depth+1)
            elif isinstance(v,list):
                if v and all(isinstance(x,dict) for x in v):
                    _add_heading(story,styles,_pretty(k),'h3')
                    _add_table(story,v,styles,story_width,maxrows=30)
                else:
                    story.append(Paragraph('<b>'+_pretty(k)+':</b>',styles['body']))
                    for item in v:
                        story.append(Paragraph('&#8226; '+_txt(item),styles['body']))
            else:
                story.append(Paragraph('<b>'+_pretty(k)+':</b> '+_txt(v),styles['body']))
    elif isinstance(data,list):
        for item in data:
            story.append(Paragraph('&#8226; '+_txt(item),styles['body']))
    else:
        story.append(Paragraph(_txt(data),styles['body']))

def _add_section(story,styles,title,data):
    story.append(KeepTogether([Paragraph(title,styles['h2']),
                               HRFlowable(width='100%',thickness=1.2,color=HexColor('#7c5cfc'),spaceBefore=2,spaceAfter=8)]))
    _add_content(story,data,styles)

def _add_raw_json(story,styles,raw):
    if not raw: return
    lines=raw.split('\n')
    chunks=[];cur=''
    for ln in lines:
        if cur and len(cur)+len(ln)+1>3200:
            chunks.append(cur);cur=ln
        else:
            cur=(cur+'\n'+ln) if cur else ln
    if cur: chunks.append(cur)
    for chunk in chunks:
        story.append(Paragraph(_esc_pdf(chunk).replace('\n','<br/>'),styles['raw']))
        story.append(Spacer(1,4))

story_width=0

def build_report_pdf(results):
    if not results: results={}
    buf=io.BytesIO()
    styles=_make_styles()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=18*mm,bottomMargin=18*mm,
                          title='Content Intelligence Report',author='Intent, Entity & Semantic Intelligence Platform',
                          subject='21-Module Content Analysis Report')
    global story_width
    story_width=doc.width
    story=[]
    blueprint=results.get('blueprint') or {}
    module_results=results.get('module_results') or {}
    url_data=results.get('_url_data') or {}
    now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    story.append(Paragraph('Content Intelligence Report',styles['title']))
    story.append(Paragraph('Intent, Entity &amp; Semantic Intelligence Platform',styles['tbrand']))
    story.append(HRFlowable(width='100%',thickness=2.4,color=HexColor('#7c5cfc'),spaceBefore=3,spaceAfter=8))
    mode='URL Analysis' if url_data else 'Keyword / Manual Analysis'
    target=url_data.get('url') or results.get('entity') or results.get('seed') or 'N/A'
    brand=results.get('brand') or ''
    story.append(Paragraph('<b>Generated:</b> %s &nbsp;&nbsp;<b>Mode:</b> %s'%(_esc_pdf(now),_esc_pdf(mode)),styles['sub']))
    story.append(Paragraph('<b>Target:</b> %s'%_esc_pdf(target),styles['sub']))
    if brand:
        story.append(Paragraph('<b>Brand:</b> %s'%_esc_pdf(brand),styles['sub']))
    story.append(Spacer(1,10))
    es=(blueprint.get('executive_summary') or {})
    stats=[('Modules Executed',es.get('total_modules_executed') or len(module_results)),
           ('Critical Issues',es.get('critical_issues_count') or 0),
           ('High Priority',es.get('high_priority_count') or 0),
           ('Recommendations',es.get('total_recommendations') or 0)]
    tdata=[[Paragraph(l,styles['statlbl']) for l,_ in stats],
           [Paragraph(_esc_pdf(str(v)),styles['statval']) for _,v in stats]]
    tw=doc.width/len(stats)
    t=Table(tdata,colWidths=[tw]*len(stats),hAlign='LEFT')
    t.setStyle(TableStyle([('BOX',(0,0),(-1,-1),0.6,HexColor('#cbd5e1')),
                           ('INNERGRID',(0,0),(-1,-1),0.4,HexColor('#e2e8f0')),
                           ('TOPPADDING',(0,0),(-1,-1),7),
                           ('BOTTOMPADDING',(0,0),(-1,-1),7),
                           ('LEFTPADDING',(0,0),(-1,-1),5),
                           ('RIGHTPADDING',(0,0),(-1,-1),5)]))
    story.append(t)
    _add_section(story,styles,'1. Executive Summary',es)
    secs=[('output_1_editorial_blueprint','2. Editorial & Writing Blueprint'),
          ('output_2_geo_optimization','3. GEO & AEO Optimization'),
          ('output_3_technical_payload','4. Technical Payload'),
          ('output_4_cdn_deployment','5. CDN & Edge Deployment'),
          ('output_5_sentinel_brief','6. Post-Publish Sentinel Brief')]
    for key,title in secs:
        sec=blueprint.get(key)
        if sec:
            _add_section(story,styles,title,sec)
    story.append(PageBreak())
    story.append(KeepTogether([Paragraph('7. Module Results',styles['h2']),
                               HRFlowable(width='100%',thickness=1.2,color=HexColor('#7c5cfc'),spaceBefore=2,spaceAfter=8)]))
    for i in range(1,22):
        k='M%02d'%i
        mr=module_results.get(k)
        if not mr: continue
        _add_heading(story,styles,'Module %d: %s'%(i,_MODULE_NAMES.get(k,k)),'h3')
        if isinstance(mr,dict) and mr.get('error'):
            story.append(Paragraph('Error: '+_txt(mr['error']),styles['body']))
        else:
            _add_content(story,mr,styles)
    story.append(PageBreak())
    story.append(KeepTogether([Paragraph('8. Full JSON Export',styles['h2']),
                               HRFlowable(width='100%',thickness=1.2,color=HexColor('#7c5cfc'),spaceBefore=2,spaceAfter=8)]))
    story.append(Paragraph('Complete raw data used to generate this report.',styles['body']))
    story.append(Spacer(1,6))
    export={k:v for k,v in results.items() if k!='_url_data'}
    if url_data:
        export['_url_data']={k:v for k,v in url_data.items() if k not in ('raw_html','page_text')}
    try:
        raw=json.dumps(export,ensure_ascii=False,indent=1,default=str)
    except Exception:
        raw=str(export)
    if len(raw)>120000:
        raw=raw[:120000]+'\n... [truncated]'
    _add_raw_json(story,styles,raw)
    doc.build(story,onFirstPage=_pdf_footer,onLaterPages=_pdf_footer)
    buf.seek(0)
    return buf.read()

app=Flask(__name__)

def web_search(query,num=5):
    """Real SERP retrieval (DuckDuckGo HTML). Returns list of result dicts."""
    res=_real_web_search(query,num)
    return res.get("results",[])

def fetch_live_stats(entity):
    """Fetch real statistics snippets via live search results."""
    stats={}
    queries=[
        f"{entity} market size 2025 2026",
        f"{entity} adoption rate enterprise",
        f"{entity} ROI statistics",
        f"{entity} comparison top solutions",
        f"{entity} implementation cost average",
    ]
    for q in queries:
        results=web_search(q,3)
        if results:
            stats[q]=results
    return stats

@app.route('/')
def index():
    return Response(INDEX_HTML,mimetype='text/html')

@app.route('/api/analyze',methods=['POST'])
def api_analyze():
    try:
        data=request.json
        fw=InputFramework()
        fw.seed=SeedKeywordInput(
            seed_phrase=data.get('seed',''),
            primary_entity=data.get('entity',''),
            target_locale=data.get('locale','en-US'),
            target_device=data.get('device','desktop'),
            secondary_keywords=[k.strip() for k in data.get('secondary','').split(',') if k.strip()],
        )
        fw.brand=BrandConstraints(
            brand_name=data.get('brand','Default'),
            voice_profile=data.get('voice','authoritative'),
            do_not_say_terms=[t.strip() for t in data.get('blacklist','').split(',') if t.strip()],
        )
        fw.audience=AudienceProfile(
            funnel_stage=data.get('funnel','middle'),
            knowledge_floor=data.get('knowledge','intermediate'),
        )
        fw.technical=TechnicalCredentials(render_mode='ssr',js_framework='',cdn_provider='')
        fw.seed.brand_website=data.get('website','')
        sme=data.get('sme','')
        if sme:
            for n in sme.split('|'):
                n=n.strip()
                if n: fw.first_party.sme_assets.append(SMEAsset(content=n,expert_name="SME",expert_title="Expert"))
        errs=fw.validate_all()
        if errs: return jsonify({"error":errs}),400
        engine=PlatformEngine()
        results=engine.run_analysis(fw)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error":str(e),"trace":traceback.format_exc()}),500

@app.route('/api/analyze-url',methods=['POST'])
def api_analyze_url():
    try:
        data=request.json
        url=data.get('url','')
        brand=data.get('brand','')
        if not url: return jsonify({"error":"URL is required"}),400
        import html.parser
        class ContentExtractor(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_parts=[]
                self.title=''
                self.meta_desc=''
                self.meta_keywords=''
                self.h1=''
                self.h2s=[]
                self.in_title=False
                self.in_h1=False
                self.in_h2=False
                self.in_script=False
                self.in_style=False
                self.in_nav=False
                self.in_footer=False
                self.current_tag=''
                self.tag_stack=[]
                self.link_count=0
                self.image_count=0
                self.images=[]
                self.links=[]
                self.schema_data=[]
            def handle_starttag(self,tag,attrs):
                self.tag_stack.append(tag)
                attrs_dict=dict(attrs)
                if tag=='title': self.in_title=True
                if tag=='h1': self.in_h1=True
                if tag=='h2': self.in_h2=True
                if tag=='script':
                    self.in_script=True
                    if attrs_dict.get('type','')=='application/ld+json':
                        self.schema_data.append('ld+json_found')
                if tag=='style': self.in_style=True
                if tag=='nav': self.in_nav=True
                if tag=='footer': self.in_footer=True
                if tag=='meta':
                    name=attrs_dict.get('name','').lower()
                    prop=attrs_dict.get('property','').lower()
                    content=attrs_dict.get('content','')
                    if name=='description' or prop=='og:description': self.meta_desc=content
                    if name=='keywords': self.meta_keywords=content
                if tag=='a':
                    self.link_count+=1
                    href=attrs_dict.get('href','')
                    if href: self.links.append(href[:200])
                if tag=='img':
                    self.image_count+=1
                    src=attrs_dict.get('src','')
                    alt=attrs_dict.get('alt','')
                    if src: self.images.append({'src':src[:200],'alt':alt})
            def handle_endtag(self,tag):
                if self.tag_stack and self.tag_stack[-1]==tag: self.tag_stack.pop()
                if tag=='title': self.in_title=False
                if tag=='h1': self.in_h1=False
                if tag=='h2': self.in_h2=False
                if tag=='script': self.in_script=False
                if tag=='style': self.in_style=False
                if tag=='nav': self.in_nav=False
                if tag=='footer': self.in_footer=False
            def handle_data(self,data):
                text=data.strip()
                if not text: return
                if self.in_title: self.title=text
                if self.in_h1: self.h1=text
                if self.in_h2: self.h2s.append(text)
                if not self.in_script and not self.in_style and not self.in_nav and not self.in_footer:
                    if len(text)>15: self.text_parts.append(text)
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; ContentAnalyzer/1.0)'})
            with urllib.request.urlopen(req,timeout=15) as resp:
                html_content=resp.read().decode('utf-8',errors='ignore')
        except Exception as fe:
            return jsonify({"error":f"Failed to fetch URL: {str(fe)}"}),400
        extractor=ContentExtractor()
        try: extractor.feed(html_content)
        except: pass
        page_text=' '.join(extractor.text_parts)
        if len(page_text)<100:
            page_text=page_text+' (Minimal content extracted from URL. Analysis based on available text.)'
        seed_words=extractor.title.split()[:5] if extractor.title else page_text.split()[:5]
        seed_phrase=' '.join(seed_words)
        entity=extractor.h1 if extractor.h1 else (extractor.title or 'the content')
        fw=InputFramework()
        fw.seed=SeedKeywordInput(
            seed_phrase=seed_phrase,
            primary_entity=entity,
            target_locale=data.get('locale','en-US'),
            target_device=data.get('device','desktop'),
            secondary_keywords=[],
        )
        fw.seed.brand_website=url
        fw.brand=BrandConstraints(
            brand_name=brand or 'Unknown Brand',
            voice_profile='authoritative',
            do_not_say_terms=[],
        )
        fw.audience=AudienceProfile(funnel_stage='middle',knowledge_floor='intermediate')
        fw.technical=TechnicalCredentials(render_mode='ssr',js_framework='',cdn_provider='')
        engine=PlatformEngine()
        fw._url_mode=True
        fw._url_data={
            'url': url,
            'title': extractor.title,
            'meta_description': extractor.meta_desc,
            'meta_keywords': extractor.meta_keywords,
            'h1': extractor.h1,
            'h2s': extractor.h2s,
            'word_count': len(page_text.split()),
            'link_count': extractor.link_count,
            'image_count': extractor.image_count,
            'images': extractor.images[:20],
            'links': extractor.links[:30],
            'has_schema': len(extractor.schema_data)>0,
            'page_text': page_text[:5000],
            'raw_html': html_content[:200000],
            'fetched_status': getattr(resp, 'status', 200),
        }
        results=engine.run_analysis(fw)
        results['_url_mode']=True
        results['_url_data']=fw._url_data
        return jsonify(results)
    except Exception as e:
        return jsonify({"error":str(e),"trace":traceback.format_exc()}),500

@app.route('/api/send_otp',methods=['POST'])
def api_send_otp():
    data=request.get_json(silent=True) or {}
    email=str(data.get('email') or '').strip().lower()
    if not _EMAIL_RE.match(email):
        return jsonify({'error':'Please enter a valid email address.'}),400
    now=time.time()
    rec=_OTP_STORE.get(email)
    if rec and (now-rec.get('req_first',now))<=_OTP_WINDOW and rec.get('req_count',0)>=_OTP_MAX_REQUESTS:
        return jsonify({'error':'Too many OTP requests for this email. Please wait a few minutes and try again.'}),429
    if rec and (now-rec.get('req_first',now))>_OTP_WINDOW:
        _OTP_STORE.pop(email,None)
    otp='%06d'%random.randint(0,999999)
    req_count=1 if not rec else rec.get('req_count',0)+1
    req_first=now if not rec else rec.get('req_first',now)
    _OTP_STORE[email]={'otp':otp,'exp':now+_OTP_TTL,'tries':0,'req_count':req_count,'req_first':req_first}
    html=("<div style='font-family:Arial,sans-serif;padding:24px;background:#f5f7ff;border-radius:12px'>"
          "<h2 style='color:#1e1b4b'>Content Intelligence Platform</h2>"
          "<p>Your one-time password (OTP) is:</p>"
          "<div style='font-size:30px;font-weight:bold;letter-spacing:6px;color:#5b21b6'>%s</div>"
          "<p>This code is valid for 10 minutes and can be used only once.</p>"
          "<p style='color:#6b7280;font-size:12px'>If you did not request this, please ignore this email.</p></div>")%otp
    try:
        _send_email(email,'Content Intelligence Platform - Your OTP Code',html)
    except Exception as e:
        _OTP_STORE.pop(email,None)
        return jsonify({'error':'Could not send the OTP email: %s'%str(e)}),500
    return jsonify({'ok':True,'message':'OTP sent to %s'%email})

@app.route('/api/verify_and_send_report',methods=['POST'])
def api_verify_and_send_report():
    data=request.get_json(silent=True) or {}
    email=str(data.get('email') or '').strip().lower()
    otp=str(data.get('otp') or '').strip()
    rec=_OTP_STORE.get(email)
    if not rec:
        return jsonify({'error':'No active OTP for this email. Please request a new OTP first.'}),400
    if time.time()>rec['exp']:
        _OTP_STORE.pop(email,None)
        return jsonify({'error':'OTP has expired. Please request a new one.'}),400
    if rec['tries']>=_OTP_MAX_TRIES:
        _OTP_STORE.pop(email,None)
        return jsonify({'error':'Too many incorrect attempts. Please request a new OTP.'}),400
    if rec['otp']!=otp:
        rec['tries']+=1
        left=_OTP_MAX_TRIES-rec['tries']
        return jsonify({'error':'Incorrect OTP. %d attempt(s) remaining.'%left}),400
    _OTP_STORE.pop(email,None)
    results=data.get('report') or {}
    try:
        pdf=build_report_pdf(results)
    except Exception as e:
        return jsonify({'error':'Could not generate the PDF report: %s'%str(e)}),500
    ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    fname='content_intelligence_report_%s.pdf'%ts
    html=("<div style='font-family:Arial,sans-serif;padding:24px;background:#f5f7ff;border-radius:12px'>"
          "<h2 style='color:#1e1b4b'>Your Content Intelligence Report</h2>"
          "<p>Please find attached the full 21-module analysis report (PDF) you requested.</p>"
          "<p style='color:#6b7280;font-size:12px'>Generated by the Intent, Entity &amp; Semantic Intelligence Platform.</p></div>")
    try:
        _send_email(email,'Your Content Intelligence Report - %s'%ts,html,fname,pdf)
    except Exception as e:
        return jsonify({'error':'Could not email the report: %s'%str(e)}),500
    return jsonify({'ok':True,'message':'Report sent to %s'%email})

@app.route('/api/download_pdf',methods=['POST'])
def api_download_pdf():
    data=request.get_json(silent=True) or {}
    results=data.get('report') or {}
    try:
        pdf=build_report_pdf(results)
    except Exception as e:
        return jsonify({'error':'Could not generate the PDF report: %s'%str(e)}),500
    ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    fname='content_intelligence_report_%s.pdf'%ts
    return Response(pdf,mimetype='application/pdf',headers={'Content-Disposition':'attachment; filename=%s'%fname})

INDEX_HTML=r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Intent, Entity & Semantic Intelligence Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0e1a;--s1:#121a2e;--s2:#1a2440;--s3:#233055;--bd:#2b3a61;--bd2:#3c4f7f;--pri:#7c5cfc;--pri2:#b7a6ff;--acc:#22d3ee;--acc2:#7ae8fa;--grn:#34d399;--yel:#fbbf24;--red:#f87171;--pink:#f472b6;--txt:#eef2ff;--txt2:#a9b6d8;--txt3:#6b7a9e;--issue-fill:#ef4444;--issue-ink:#ffffff;--issue-row:rgba(239,68,68,.14);--csh:0 2px 10px rgba(0,0,0,.35)}
body{font-family:'Google Sans','Roboto',-apple-system,'Segoe UI','Helvetica Neue',Arial,sans-serif;font-size:15px;background:var(--bg);color:var(--txt);overflow:hidden;height:100vh;line-height:1.65;transition:background .3s,color .3s}
body.light{--bg:#f5f7ff;--s1:#ffffff;--s2:#eef2ff;--s3:#e3e9fb;--bd:#d6def2;--bd2:#b4c0e4;--pri:#6d4ff0;--pri2:#7c5cfc;--acc:#0891b2;--acc2:#0ea5c5;--grn:#059669;--yel:#d97706;--red:#dc2626;--pink:#db2777;--txt:#0f172a;--txt2:#415070;--txt3:#68779b;--issue-fill:#dc2626;--issue-ink:#ffffff;--issue-row:rgba(220,38,38,.10);--csh:0 1px 4px rgba(30,41,80,.10)}
.app{display:grid;grid-template-columns:340px 1fr;grid-template-rows:56px 1fr;height:100vh}
.topbar{grid-column:1/-1;background:var(--s1);border-bottom:1px solid var(--bd);display:flex;align-items:center;padding:0 24px;gap:16px;z-index:10;transition:background .3s}
.topbar .brand{display:flex;flex-direction:column;gap:2px}
.topbar h1{font-size:1.05rem;font-weight:700;background:linear-gradient(120deg,#a78bfa,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;white-space:nowrap}
.topbar .subtitle{font-size:.82rem;color:var(--txt3);letter-spacing:.3px}
.topbar .sep{width:1px;height:28px;background:var(--bd)}
.topbar .status{font-size:.82rem;color:var(--txt3)}
.topbar .right{margin-left:auto;display:flex;align-items:center;gap:12px}
.theme-toggle{position:relative;width:46px;height:26px;background:var(--s3);border-radius:13px;cursor:pointer;border:1px solid var(--bd2);transition:all .3s;padding:0}
.theme-toggle .knob{position:absolute;top:3px;left:3px;width:18px;height:18px;background:linear-gradient(135deg,var(--pri),var(--acc));border-radius:50%;transition:all .3s}
body.light .theme-toggle .knob{left:23px}
.sidebar{background:var(--s1);border-right:1px solid var(--bd);overflow-y:auto;padding:14px;transition:background .3s}
.sidebar::-webkit-scrollbar{width:5px}
.sidebar::-webkit-scrollbar-thumb{background:var(--bd);border-radius:2px}
.main{overflow-y:auto;padding:22px 26px}
.main::-webkit-scrollbar{width:7px}
.main::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}
.form-section{margin-bottom:12px}
.form-section summary{font-size:.8rem;font-weight:700;color:var(--txt2);text-transform:uppercase;letter-spacing:.8px;padding:8px 0;cursor:pointer;list-style:none;display:flex;align-items:center;gap:6px}
.form-section summary::before{content:'\25B6';font-size:.55rem;transition:transform .2s;color:var(--pri)}
.form-section[open] summary::before{transform:rotate(90deg)}
.fg{margin-bottom:12px}
.fg label{display:block;font-size:.8rem;font-weight:600;color:var(--txt2);margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px}
.fg input,.fg select,.fg textarea{width:100%;padding:10px 12px;background:var(--s2);border:1px solid var(--bd);border-radius:7px;color:var(--txt);font-size:.92rem;font-family:inherit;transition:all .2s}
.fg input:focus,.fg select:focus,.fg textarea:focus{outline:none;border-color:var(--pri);box-shadow:0 0 0 3px rgba(124,92,252,.18)}
.fg textarea{resize:vertical;min-height:60px}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.mode-divider{display:flex;align-items:center;gap:10px;margin:16px 0;color:var(--txt3);font-size:.78rem;text-transform:uppercase;letter-spacing:1px}
.mode-divider::before,.mode-divider::after{content:'';flex:1;height:1px;background:var(--bd)}
.url-section{background:linear-gradient(180deg,var(--s2),var(--s1));border:1px solid var(--bd2);border-radius:8px;padding:14px;margin-bottom:14px}
.url-section summary{font-size:.82rem;font-weight:700;color:var(--acc2);text-transform:uppercase;letter-spacing:.8px;padding:0 0 8px 0;cursor:pointer;list-style:none;display:flex;align-items:center;gap:6px}
.url-section summary::before{content:'\25B6';font-size:.55rem;transition:transform .2s;color:var(--acc)}
.url-section[open] summary::before{transform:rotate(90deg)}
.url-section .fg label{color:var(--acc2)}
.url-section .fg input:focus{border-color:var(--acc);box-shadow:0 0 0 3px rgba(34,211,238,.18)}
.btn-url{background:linear-gradient(135deg,var(--acc),#0891b2);border:none;color:#fff}
.btn-url:hover{box-shadow:0 4px 18px rgba(34,211,238,.35);transform:translateY(-1px)}
.mode-badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.76rem;font-weight:700;margin-left:8px;border:1px solid var(--bd2);color:var(--pri2);background:rgba(124,92,252,.12)}
.btn{width:100%;padding:11px;border:none;border-radius:8px;font-size:.92rem;font-weight:700;cursor:pointer;font-family:inherit;transition:all .2s}
.btn-go{background:linear-gradient(135deg,var(--pri),#6d28d9);color:#fff}
.btn-go:hover{box-shadow:0 4px 18px rgba(124,92,252,.4);transform:translateY(-1px)}
.btn-go:active{transform:translateY(0)}
.btn-go:disabled{opacity:.4;cursor:not-allowed;transform:none}
.tabs{display:flex;gap:3px;background:var(--s1);border:1px solid var(--bd);border-radius:9px;padding:4px;margin-bottom:16px;flex-wrap:wrap}
.tab{padding:7px 13px;border:none;background:transparent;color:var(--txt3);border-radius:6px;cursor:pointer;font-size:.82rem;font-weight:600;white-space:nowrap;font-family:inherit;transition:all .15s}
.tab.on{background:linear-gradient(135deg,var(--pri),#6d28d9);color:#fff;box-shadow:0 2px 10px rgba(124,92,252,.35)}
.tab:hover:not(.on){background:var(--s2);color:var(--txt2)}
.panel{display:none;animation:fadeIn .3s ease}
.panel.on{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.card{background:var(--s1);border:1px solid var(--bd);border-radius:14px;padding:22px;margin-bottom:18px;box-shadow:var(--csh);transition:all .3s}
.card:hover{border-color:var(--bd2)}
.card h3{font-size:1.05rem;font-weight:700;margin-bottom:16px;color:var(--acc2);display:flex;align-items:center;gap:8px}
.card h4{font-size:.9rem;font-weight:700;margin:18px 0 12px;color:var(--pri2);padding-bottom:6px;border-bottom:1px solid var(--bd)}
.card p,.card li{font-size:.92rem;color:var(--txt2);line-height:1.7}
.card ul{padding-left:20px}
.card li{margin-bottom:6px}
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:18px}
.sb{background:var(--s2);border:1px solid var(--bd);border-radius:12px;padding:15px;text-align:center;transition:all .2s}
.sb:hover{border-color:var(--bd2);transform:translateY(-2px)}
.sb .v{font-size:1.45rem;font-weight:700;color:var(--txt)}
.sb .l{font-size:.78rem;color:var(--txt3);margin-top:4px;text-transform:uppercase;letter-spacing:.5px}
.sb.g .v{color:var(--grn)}.sb.y .v{color:var(--yel)}.sb.r .v{color:var(--red)}.sb.b .v{color:var(--acc2)}.sb.p .v{color:var(--pri2)}
.sb.g{border-color:rgba(52,211,153,.4)}.sb.y{border-color:rgba(251,191,36,.4)}.sb.r{border-color:rgba(248,113,113,.5)}.sb.b{border-color:rgba(34,211,238,.4)}.sb.p{border-color:rgba(183,166,255,.4)}
.tag{display:inline-block;padding:4px 9px;border-radius:6px;font-size:.76rem;font-weight:700;margin:1px}
.tag.cr{background:rgba(239,68,68,.16);color:#fca5a5;border:1px solid rgba(239,68,68,.35)}
.tag.hi{background:rgba(251,191,36,.14);color:#fcd34d;border:1px solid rgba(251,191,36,.35)}
.tag.md{background:rgba(124,92,252,.15);color:#c4b5fd;border:1px solid rgba(124,92,252,.35)}
.tag.lo{background:rgba(52,211,153,.14);color:#6ee7b7;border:1px solid rgba(52,211,153,.35)}
.issue{display:inline-block;background:var(--issue-fill);color:var(--issue-ink);font-weight:700;padding:2px 9px;border-radius:6px;font-size:.78rem}
tr.issue td{background:var(--issue-row);border-left:3px solid var(--issue-fill);color:var(--txt)}
tr.issue td .tag{background:var(--issue-fill);color:var(--issue-ink);border-color:var(--issue-fill)}
pre{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:15px;overflow-x:auto;font-size:.8rem;color:var(--txt2);max-height:500px;overflow-y:auto;font-family:'Cascadia Code','Consolas',monospace;position:relative}
pre code{font-family:inherit}
.jk{color:#7dd3fc}.js{color:#86efac}.jn{color:#fbbf24}.jb{color:#c084fc}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:.88rem;margin:12px 0;border-radius:8px;overflow:hidden;border:1px solid var(--bd)}
th{text-align:left;padding:11px 13px;background:var(--s2);color:var(--acc2);font-weight:700;font-size:.78rem;text-transform:uppercase;letter-spacing:.3px;border-bottom:1px solid var(--bd)}
td{padding:10px 13px;border-bottom:1px solid var(--bd);color:var(--txt2);vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--s2);transition:background .15s}
.progress{width:100%;height:7px;background:var(--s2);border-radius:3px;overflow:hidden;margin:8px 0}
.progress .fill{height:100%;background:linear-gradient(90deg,var(--pri),var(--acc));transition:width .3s;border-radius:3px}
.mod-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:6px;margin:10px 0}
.mod-i{display:flex;align-items:center;gap:6px;padding:7px 11px;background:var(--s2);border-radius:8px;font-size:.8rem;transition:all .2s;border:1px solid transparent}
.mod-i:hover{border-color:var(--bd2)}
.mod-i .d{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.d.ok{background:var(--grn)}.d.er{background:var(--red)}.d.w{background:var(--txt3)}.d.r{background:var(--yel);animation:pu 1s infinite}
@keyframes pu{0%,100%{opacity:1}50%{opacity:.3}}
.hidden{display:none}
.info-page{max-width:880px;margin:0 auto;padding:20px 0}
.info-page h2{font-size:1.45rem;font-weight:700;margin-bottom:16px;background:linear-gradient(120deg,#a78bfa,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.info-page h3{font-size:1.15rem;font-weight:700;margin:24px 0 10px;color:var(--pri2);padding-bottom:6px;border-bottom:1px solid var(--bd)}
.info-page p{font-size:.94rem;line-height:1.75;margin-bottom:12px;color:var(--txt2)}
.info-page ul{padding-left:20px;margin-bottom:12px}
.info-page li{font-size:.9rem;line-height:1.7;margin-bottom:6px;color:var(--txt2)}
.feature-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:12px;margin:16px 0}
.feature-card{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:17px;transition:all .2s;cursor:default}
.feature-card:hover{border-color:var(--pri);transform:translateY(-2px);box-shadow:0 4px 16px rgba(124,92,252,.18)}
.feature-card h4{font-size:.92rem;font-weight:700;margin-bottom:6px;color:var(--acc2)}
.feature-card p{font-size:.86rem;margin:0;line-height:1.6}
.json-toggle{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:11px 15px;cursor:pointer;font-size:.88rem;color:var(--txt2);margin:8px 0;display:flex;align-items:center;gap:8px;transition:all .2s;width:100%;text-align:left;font-family:inherit}
.json-toggle:hover{border-color:var(--pri);color:var(--txt)}
.json-content{display:none;margin-top:8px}
.json-content.open{display:block}
.copy-toast{position:fixed;bottom:20px;right:20px;background:var(--grn);color:#04231a;padding:11px 18px;border-radius:8px;font-size:.86rem;font-weight:600;z-index:1000;animation:slideUp .3s ease;pointer-events:none}
@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.mblock{background:var(--s2);border:1px solid var(--bd);border-radius:12px;padding:15px;margin-bottom:14px;overflow:hidden}
.mblock.green{border-color:rgba(52,211,153,.4)}
.mblock.cyan{border-color:rgba(34,211,238,.4)}
.mblock .mh{font-size:.84rem;font-weight:700;color:var(--acc2);text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px;display:flex;align-items:center;gap:6px}
.mblock.green .mh{color:var(--grn)}
.mblock.cyan .mh{color:var(--acc2)}
table.kv2{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--bd);border-radius:8px;overflow:hidden;margin:0}
table.kv2 th{width:34%;text-align:left;padding:9px 13px;background:var(--s3);color:var(--txt3);font-size:.78rem;text-transform:uppercase;letter-spacing:.3px;border-bottom:1px solid var(--bd);vertical-align:top}
table.kv2 td{padding:9px 13px;border-bottom:1px solid var(--bd);color:var(--txt2);font-size:.88rem;vertical-align:top;word-break:break-word}
table.kv2 tr:last-child th,table.kv2 tr:last-child td{border-bottom:none}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:var(--s3);border:1px solid var(--bd2);color:var(--txt2);padding:5px 11px;border-radius:20px;font-size:.8rem;word-break:break-word}
.dash{color:var(--txt3)}
.ok{color:var(--grn);font-weight:700}
.no{color:#fff;font-weight:800;background:var(--issue-fill);padding:1px 7px;border-radius:5px}
.num{color:var(--acc2);font-weight:700}
.str{color:var(--txt2)}
.more{text-align:center;color:var(--txt3);font-size:.8rem}
ol.steps{margin:0;padding-left:20px}
ol.steps li{font-size:.88rem;color:var(--txt2);line-height:1.75;margin-bottom:6px}
ul.where{margin:0;padding-left:20px}
ul.where li{font-size:.88rem;color:var(--txt2);line-height:1.7;margin-bottom:6px}
.acc{margin-bottom:8px;border:1px solid var(--bd);border-radius:8px;overflow:hidden}
.accb{width:100%;text-align:left;background:var(--s3);border:none;padding:11px 15px;color:var(--txt);font-size:.84rem;font-weight:600;cursor:pointer;font-family:inherit;display:flex;justify-content:space-between;align-items:center}
.accb .accarrow{transition:transform .2s;font-size:.7rem;color:var(--txt3)}
.accb.open .accarrow{transform:rotate(180deg)}
.accp{display:none;padding:14px 15px}
.accp.open{display:block}
.subs{display:flex;flex-direction:column;gap:10px}
.sub{border:1px solid var(--bd);border-radius:8px;overflow:hidden}
.subh{background:var(--s3);padding:9px 13px;font-size:.8rem;font-weight:700;color:var(--acc2);text-transform:uppercase;letter-spacing:.4px}
.subb{padding:13px}
</style>
</head>
<body>
<div class="app">
<div class="topbar">
<div class="brand">
<h1>Intent, Entity & Semantic Intelligence Platform</h1>
<div class="subtitle">21-Module Analysis for Search & Generative AI Optimization</div>
</div>
<div class="sep"></div>
<div class="status" id="topStatus">Ready - 21 modules loaded</div>
<div class="right">
<button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode"><div class="knob"></div></button>
</div>
</div>
<div class="sidebar">
<div class="mode-divider">&#9679; Analysis Mode</div>
<details class="url-section" open>
<summary>&#128279; Analyze Published URL</summary>
<p style="font-size:.82rem;color:var(--txt3);margin-bottom:10px">Paste a published blog/article URL. The tool will fetch and analyze its content across all 21 modules.</p>
<div class="fg"><label>Published Blog / Article URL</label><input id="iUrl" type="url" placeholder="https://example.com/blog/your-article"></div>
<div class="fg"><label>Brand Name (for URL mode)</label><input id="iUrlBrand" placeholder="Your Brand"></div>
<button type="button" class="btn btn-url" id="urlBtn" onclick="runUrlAnalysis()">&#9654; Analyze This URL</button>
</details>
<div class="mode-divider">&#9679; Or Manual Input</div>
<form id="fForm">
<details class="form-section" open>
<summary>Seed &amp; Entity</summary>
<div class="fg"><label>Seed Keyword *</label><input id="iSeed" required placeholder="best enterprise B2B SaaS accounting software"></div>
<div class="fg"><label>Primary Entity *</label><input id="iEntity" required placeholder="multi-currency accounting software"></div>
<div class="fg"><label>Brand Website URL</label><input id="iWebsite" placeholder="https://example.com"></div>
</details>
<details class="form-section" open>
<summary>Brand &amp; Audience</summary>
<div class="fg"><label>Brand Name</label><input id="iBrand" value="FinTech Pro"></div>
<div class="row2">
<div class="fg"><label>Locale</label><select id="iLocale"><option value="en-US">en-US</option><option value="en-GB">en-GB</option><option value="de-DE">de-DE</option><option value="fr-FR">fr-FR</option><option value="ja-JP">ja-JP</option><option value="en-AU">en-AU</option><option value="en-IN">en-IN</option><option value="es-ES">es-ES</option></select></div>
<div class="fg"><label>Device</label><select id="iDevice"><option value="desktop">Desktop</option><option value="mobile">Mobile</option></select></div>
</div>
<div class="row2">
<div class="fg"><label>Funnel</label><select id="iFunnel"><option value="top">Top</option><option value="middle" selected>Middle</option><option value="bottom">Bottom</option></select></div>
<div class="fg"><label>Knowledge</label><select id="iKnow"><option value="beginner">Beginner</option><option value="intermediate" selected>Intermediate</option><option value="advanced">Advanced</option><option value="expert">Expert</option><option value="c-suite">C-Suite</option></select></div>
</div>
<div class="fg"><label>Voice</label><select id="iVoice"><option value="authoritative" selected>Authoritative</option><option value="conversational">Conversational</option><option value="academic">Academic</option><option value="technical">Technical</option></select></div>
</details>
<details class="form-section">
<summary>Keywords &amp; SME</summary>
<div class="fg"><label>Secondary Keywords</label><input id="iSec" placeholder="cloud accounting,financial reporting"></div>
<div class="fg"><label>Blacklisted Terms</label><input id="iBlack" placeholder="game-changer,delve"></div>
<div class="fg"><label>SME Notes (pipe sep)</label><textarea id="iSME" placeholder="Note 1|Note 2|Note 3"></textarea></div>
</details>
<button type="submit" class="btn btn-go" id="runBtn">Run 21-Module Analysis</button>
</form>
<div id="statusBox" style="margin-top:12px"></div>
</div>
<div class="main" id="mainArea">
<div class="info-page" id="infoArea">
<h2>Welcome to the Intent, Entity & Semantic Intelligence Platform</h2>
<p>A comprehensive 21-module analysis engine that evaluates your content for both traditional search engines and generative AI engines (Gemini, ChatGPT, Perplexity). Get maximum-depth blueprints for editorial, technical, GEO, CDN, and sentinel optimization.</p>
<h3>Why This Tool Exists</h3>
<p>Modern SEO requires optimizing for two audiences: traditional search engines (Google, Bing) and generative AI engines (ChatGPT, Gemini, Perplexity). Most tools only address one. This platform analyzes your content across 21 specialized dimensions to ensure maximum visibility in both ecosystems.</p>
<h3>What This Tool Does</h3>
<p>This platform runs 21 specialized analysis modules covering SERP analysis, GEO/AEO simulation, semantic structuring, E-E-A-T profiling, content decay detection, CDN edge preview, and more. Each module produces detailed, actionable output organized into 5 blueprint categories plus raw data.</p>
<h3>Modules Overview</h3>
<div class="feature-grid">
<div class="feature-card"><h4>M01: SERP & Knowledge Graph</h4><p>Analyze SERP features, entity graphs, and Knowledge Panel opportunities.</p></div>
<div class="feature-card"><h4>M02: GEO & AEO Simulator</h4><p>Simulate Generative Engine and Answer Engine optimization strategies.</p></div>
<div class="feature-card"><h4>M03: Semantic Structure</h4><p>Validate schema markup, heading hierarchy, and semantic HTML structure.</p></div>
<div class="feature-card"><h4>M04: E-E-A-T Gap Profiler</h4><p>Profile Experience, Expertise, Authoritativeness, and Trustworthiness gaps.</p></div>
<div class="feature-card"><h4>M05: Internal Link & Cannibalization</h4><p>Detect keyword cannibalization and optimize internal link architecture.</p></div>
<div class="feature-card"><h4>M06: Fluff & Cliche Decoder</h4><p>Identify filler content, cliches, and non-original phrases.</p></div>
<div class="feature-card"><h4>M07: Citation & Source Verifier</h4><p>Verify citation accuracy and source credibility for E-E-A-T signals.</p></div>
<div class="feature-card"><h4>M08: Multimodal Asset Blueprint</h4><p>Plan images, videos, infographics, and interactive assets.</p></div>
<div class="feature-card"><h4>M09: GEO Tracker</h4><p>Track Generative Engine Optimization performance across AI platforms.</p></div>
<div class="feature-card"><h4>M10: CSR Simulator</h4><p>Simulate Client-Side Rendering impact on search engine indexing.</p></div>
<div class="feature-card"><h4>M11: RAG Tester</h4><p>Test content for Retrieval-Augmented Generation compatibility.</p></div>
<div class="feature-card"><h4>M12: Brand Compliance Engine</h4><p>Enforce brand voice, terminology, and style guidelines.</p></div>
<div class="feature-card"><h4>M13: Schema Payload Generator</h4><p>Generate complete JSON-LD schema payloads for rich results.</p></div>
<div class="feature-card"><h4>M14: Intent & Bounce Predictor</h4><p>Predict bounce risk and align content with user intent signals.</p></div>
<div class="feature-card"><h4>M15: Content Decay Engine</h4><p>Detect content freshness decay and generate refresh briefs.</p></div>
<div class="feature-card"><h4>M16: CDN Edge Previewer</h4><p>Preview edge-injected schema, headers, and pre-rendered HTML.</p></div>
<div class="feature-card"><h4>M17: A/B Testing Engine</h4><p>Design statistical A/B tests for content experiments.</p></div>
<div class="feature-card"><h4>M18: Indexing Sentinel</h4><p>Monitor indexing status and crawl budget health.</p></div>
<div class="feature-card"><h4>M19: Localization Sync</h4><p>Manage hreflang, localized schema, and entity mapping.</p></div>
<div class="feature-card"><h4>M20: Digital PR Engine</h4><p>Plan PR outreach, authority signals, and brand mentions.</p></div>
<div class="feature-card"><h4>M21: DOM Inspector</h4><p>Analyze DOM structure, layout shifts, and performance impact.</p></div>
</div>
<h3>What You Need</h3>
<ul>
<li><strong>Seed Keyword</strong> - Your primary target keyword or phrase</li>
<li><strong>Primary Entity</strong> - The main entity/topic your content covers</li>
<li><strong>Brand Name</strong> - Your brand for compliance and authority checks</li>
<li><strong>Audience Profile</strong> - Funnel stage, knowledge level, and voice preference</li>
</ul>
<h3>What You Get</h3>
<ul>
<li><strong>Executive Summary</strong> - High-level overview with critical issues and priorities</li>
<li><strong>Editorial Blueprint</strong> - Content outline, H1/H2/H3 structure, SME placements, answer blocks</li>
<li><strong>GEO Optimization</strong> - AI engine strategies, citation triggers, RAG chunking</li>
<li><strong>Technical Payload</strong> - JSON-LD schemas, validation, internal linking, DOM analysis</li>
<li><strong>CDN Deployment</strong> - Edge workers, headers, pre-render simulation</li>
<li><strong>Sentinel Brief</strong> - Monitoring config, alerts, A/B test design, rollback guards</li>
<li><strong>21 Module Results</strong> - Deep analysis from each specialized module</li>
<li><strong>Raw JSON</strong> - Complete data export for programmatic use</li>
</ul>
<p style="margin-top:24px;color:var(--pri2);font-weight:600;font-size:.95rem">Enter your seed keyword and entity in the sidebar, then click <strong>Run 21-Module Analysis</strong> to begin.</p>
</div>
</div>
</div>

<script>
const MN={M01:"SERP & Knowledge Graph",M02:"GEO & AEO Simulator",M03:"Semantic Structure & Schema",M04:"E-E-A-T Gap Profiler",M05:"Internal Link & Cannibalization",M06:"Fluff & Cliche Decoder",M07:"Citation & Source Verifier",M08:"Multimodal Asset Blueprint",M09:"GEO Tracker",M10:"CSR Simulator",M11:"RAG Tester",M12:"Brand Compliance Engine",M13:"Schema Payload Generator",M14:"Intent & Bounce Predictor",M15:"Content Decay Engine",M16:"CDN Edge Previewer",M17:"A/B Testing Engine",M18:"Indexing Sentinel",M19:"Localization Sync",M20:"Digital PR Engine",M21:"DOM Inspector"};
const TABS=["exec","edit","geo","tech","cdn","snt","m01","m02","m03","m04","m05","m06","m07","m08","m09","m10","m11","m12","m13","m14","m15","m16","m17","m18","m19","m20","m21","raw"];
const TAB_LABELS={exec:"Executive Summary",edit:"Editorial Blueprint",geo:"GEO Optimization",tech:"Technical Payload",cdn:"CDN Deployment",snt:"Sentinel Brief",raw:"Raw JSON"};
for(let i=1;i<=21;i++){const k="m"+(i<10?"0":"")+i;TAB_LABELS[k]=MN[k.toUpperCase()]||("Module "+i);}

function toggleTheme(){document.body.classList.toggle('light');localStorage.setItem('theme',document.body.classList.contains('light')?'light':'dark');}
(function(){const t=localStorage.getItem('theme');if(t==='light')document.body.classList.add('light');})();

async function runUrlAnalysis(){
const url=document.getElementById('iUrl').value.trim();
const brand=document.getElementById('iUrlBrand').value.trim();
if(!url){alert('Please enter a published blog or article URL.');return;}
if(!url.startsWith('http')){alert('Please enter a valid URL starting with http:// or https://');return;}
const btn=document.getElementById('urlBtn');
btn.disabled=true;btn.textContent='Fetching & Analyzing...';
document.getElementById('statusBox').innerHTML='<div class="progress"><div class="fill" id="pFill" style="width:0%"></div></div><p style="font-size:.82rem;color:var(--txt3);margin-top:4px">Fetching URL content and running 21-module analysis...</p><div class="mod-grid" id="modGrid"></div>';
Object.entries(MN).forEach(([k,v])=>{document.getElementById('modGrid').innerHTML+=`<div class="mod-i" id="m_${k}"><div class="d w"></div><span>${k}</span></div>`;});
let p=0;const iv=setInterval(()=>{if(p<90){p+=Math.random()*3;const f=document.getElementById('pFill');if(f)f.style.width=p+'%';}},200);
try{
const res=await fetch('/api/analyze-url',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url,brand:brand,locale:'en-US',device:'desktop'})});
const data=await res.json();
clearInterval(iv);
if(data.error){document.getElementById('statusBox').innerHTML='<p style="color:var(--red);font-size:.82rem">Error: '+JSON.stringify(data.error)+'</p>';btn.disabled=false;btn.textContent='\u25B6 Analyze This URL';return;}
const f=document.getElementById('pFill');if(f)f.style.width='100%';
Object.keys(MN).forEach(k=>{const el=document.getElementById('m_'+k);if(el){const d=el.querySelector('.d');d.className=data.module_results&&data.module_results[k]&&!data.module_results[k].error?'d ok':'d er';}});
setTimeout(()=>renderAll(data),400);
}catch(err){clearInterval(iv);document.getElementById('statusBox').innerHTML='<p style="color:var(--red)">'+err.message+'</p>';}
btn.disabled=false;btn.textContent='\u25B6 Analyze This URL';
}

function showToast(msg){const t=document.createElement('div');t.className='copy-toast';t.textContent=msg;document.body.appendChild(t);setTimeout(()=>t.remove(),2000);}
function copyText(txt){navigator.clipboard.writeText(txt).then(()=>showToast('Copied to clipboard!'));}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

function renderExportCard(){
return `<div class="card" style="border-color:var(--pri);margin-bottom:16px">
<h3>&#128228; Export &amp; Share Report</h3>
<div class="sg" style="grid-template-columns:1fr 1fr;gap:10px">
<button type="button" class="btn btn-go" onclick="downloadReportPdf(this)">&#11015; Download PDF Report</button>
<button type="button" class="btn btn-url" onclick="toggleMailBox()">&#9993; Email Me the PDF</button>
</div>
<div id="mailBox" class="hidden" style="margin-top:14px">
<div class="fg"><label>Your Email Address</label><input id="mailEmail" type="email" placeholder="you@example.com"></div>
<button type="button" class="btn btn-go" id="otpBtn" onclick="sendOtp()" style="width:auto;padding:9px 18px">Send OTP</button>
<div id="otpRow" class="hidden" style="margin-top:12px">
<div class="fg"><label>Enter the 6-Digit OTP from Your Email</label><input id="mailOtp" inputmode="numeric" maxlength="6" placeholder="000000"></div>
<button type="button" class="btn btn-go" id="verifyBtn" onclick="verifyAndSend()" style="width:auto;padding:9px 18px">Verify &amp; Send PDF</button>
</div>
<p id="mailMsg" style="font-size:.82rem;margin-top:10px"></p>
</div>
</div>`;
}
function setMailMsg(m,err){const el=document.getElementById('mailMsg');if(!el)return;el.innerHTML=esc(m);el.style.color=err?'var(--red)':'var(--grn)';}
function toggleMailBox(){const b=document.getElementById('mailBox');if(b)b.classList.toggle('hidden');}
async function downloadReportPdf(btn){
const data=window._lastResults;
if(!data){showToast('Run an analysis first.');return;}
btn.disabled=true;btn.textContent='Generating PDF...';
try{
const res=await fetch('/api/download_pdf',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report:data})});
if(!res.ok){const e=await res.json().catch(()=>({}));showToast((e.error||'PDF generation failed').slice(0,80));return;}
const blob=await res.blob();
const a=document.createElement('a');a.href=URL.createObjectURL(blob);
const cd=res.headers.get('Content-Disposition')||'';
const m=cd.match(/filename="?([^";]+)"?/);a.download=m?m[1]:'content_intelligence_report.pdf';
document.body.appendChild(a);a.click();a.remove();
setTimeout(()=>URL.revokeObjectURL(a.href),4000);
showToast('PDF downloaded!');
}catch(err){showToast('Failed: '+err.message.slice(0,80));}
finally{btn.disabled=false;btn.textContent='\u2B07 Download PDF Report';}
}
async function sendOtp(){
const email=document.getElementById('mailEmail').value.trim();
if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){setMailMsg('Please enter a valid email.',true);return;}
const btn=document.getElementById('otpBtn');btn.disabled=true;btn.textContent='Sending OTP...';
setMailMsg('Sending OTP to '+email+' ...',false);
try{
const res=await fetch('/api/send_otp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email})});
const d=await res.json();
if(d.error){setMailMsg(d.error,true);}
else{setMailMsg('OTP sent to '+email+'. Check your inbox (and spam).',false);const r=document.getElementById('otpRow');if(r)r.classList.remove('hidden');}
}catch(err){setMailMsg('Failed: '+err.message,true);}
finally{btn.disabled=false;btn.textContent='Send OTP';}
}
async function verifyAndSend(){
const email=document.getElementById('mailEmail').value.trim();
const otp=document.getElementById('mailOtp').value.trim();
if(!otp||otp.length!==6){setMailMsg('Enter the 6-digit OTP.',true);return;}
const btn=document.getElementById('verifyBtn');btn.disabled=true;btn.textContent='Sending Report...';
setMailMsg('Verifying OTP and sending the PDF report...',false);
try{
const res=await fetch('/api/verify_and_send_report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,otp:otp,report:window._lastResults})});
const d=await res.json();
if(d.error){setMailMsg(d.error,true);}
else{setMailMsg('Success! PDF report sent to '+email+'.',false);}
}catch(err){setMailMsg('Failed: '+err.message,true);}
finally{btn.disabled=false;btn.textContent='Verify & Send PDF';}
}

document.getElementById('fForm').addEventListener('submit',async e=>{
e.preventDefault();
const btn=document.getElementById('runBtn');
btn.disabled=true;btn.textContent='Running 21-Module Analysis...';
document.getElementById('statusBox').innerHTML='<div class="progress"><div class="fill" id="pFill" style="width:0%"></div></div><p style="font-size:.82rem;color:var(--txt3);margin-top:4px">Initializing modules...</p><div class="mod-grid" id="modGrid"></div>';
const mg=document.getElementById('modGrid');
Object.entries(MN).forEach(([k,v])=>{mg.innerHTML+=`<div class="mod-i" id="m_${k}"><div class="d w"></div><span>${k}</span></div>`;});
let p=0;const iv=setInterval(()=>{if(p<92){p+=Math.random()*4;const f=document.getElementById('pFill');if(f)f.style.width=p+'%';}},150);
try{
const body={seed:document.getElementById('iSeed').value,entity:document.getElementById('iEntity').value,brand:document.getElementById('iBrand').value,website:document.getElementById('iWebsite').value,locale:document.getElementById('iLocale').value,device:document.getElementById('iDevice').value,funnel:document.getElementById('iFunnel').value,knowledge:document.getElementById('iKnow').value,voice:document.getElementById('iVoice').value,secondary:document.getElementById('iSec').value,blacklist:document.getElementById('iBlack').value,sme:document.getElementById('iSME').value};
const res=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
const data=await res.json();
clearInterval(iv);
if(data.error){document.getElementById('statusBox').innerHTML='<p style="color:var(--red);font-size:.82rem">Error: '+JSON.stringify(data.error)+'</p>';btn.disabled=false;btn.textContent='Run 21-Module Analysis';return;}
const f=document.getElementById('pFill');if(f)f.style.width='100%';
Object.keys(MN).forEach(k=>{const el=document.getElementById('m_'+k);if(el){const d=el.querySelector('.d');d.className=data.module_results&&data.module_results[k]&&!data.module_results[k].error?'d ok':'d er';}});
setTimeout(()=>renderAll(data),400);
}catch(err){clearInterval(iv);document.getElementById('statusBox').innerHTML='<p style="color:var(--red)">'+err.message+'</p>';}
btn.disabled=false;btn.textContent='Run 21-Module Analysis';
});

function renderAll(data){
const ma=document.getElementById('mainArea');
const b=data.blueprint||{};
const mr=data.module_results||{};
const ud=data._url_data||null;
let urlBanner='';
if(ud){
urlBanner=`<div class="card" style="border-color:var(--acc);margin-bottom:16px">
<h3>&#128279; URL Analysis Results</h3>
<div class="sg">
<div class="sb b"><div class="v" style="font-size:1rem;word-break:break-all">${ud.url||''}</div><div class="l">Analyzed URL</div></div>
<div class="sb"><div class="v">${ud.title||'N/A'}</div><div class="l">Page Title</div></div>
<div class="sb p"><div class="v">${ud.word_count||0}</div><div class="l">Words</div></div>
<div class="sb g"><div class="v">${ud.link_count||0}</div><div class="l">Links</div></div>
<div class="sb"><div class="v">${ud.image_count||0}</div><div class="l">Images</div></div>
<div class="sb ${ud.has_schema?'g':'r'}"><div class="v">${ud.has_schema?'Yes':'No'}</div><div class="l">Schema Found</div></div>
</div>
${ud.h1?'<p style="font-size:.85rem;margin-top:8px"><strong>H1:</strong> '+esc(ud.h1)+'</p>':''}
${ud.meta_desc?'<p style="font-size:.82rem;color:var(--txt3)"><strong>Meta:</strong> '+esc(ud.meta_desc.substring(0,200))+'</p>':''}
${ud.h2s&&ud.h2s.length?'<p style="font-size:.82rem;color:var(--txt3)"><strong>H2s Found:</strong> '+ud.h2s.length+' headings</p>':''}
</div>`;
}
let tabs='<div class="tabs">';
TABS.forEach((t,i)=>{tabs+=`<button class="tab${i===0?' on':''}" onclick="showTab('${t}')">${TAB_LABELS[t]||t}</button>`;});
tabs+='</div>';
let panels='';
panels+=`<div class="panel on" id="p_exec">${urlBanner}${renderExportCard()}${renderExec(b.executive_summary||{})}</div>`;
panels+=`<div class="panel" id="p_edit">${renderEdit(b.output_1_editorial_blueprint||{})}</div>`;
panels+=`<div class="panel" id="p_geo">${renderGeo(b.output_2_geo_optimization||{})}</div>`;
panels+=`<div class="panel" id="p_tech">${renderTech(b.output_3_technical_payload||{})}</div>`;
panels+=`<div class="panel" id="p_cdn">${renderCDN(b.output_4_cdn_deployment||{})}</div>`;
panels+=`<div class="panel" id="p_snt">${renderSnt(b.output_5_sentinel_brief||{})}</div>`;
for(let i=1;i<=21;i++){const k="m"+(i<10?"0":"")+i;const mk="M"+(i<10?"0":"")+i;panels+=`<div class="panel" id="p_${k}">${renderModule(mk,mr[mk]||{})}</div>`;}
window._lastResults=data;window._rawB=b;window._rawMr=mr;
panels+=`<div class="panel" id="p_raw">
<div class="card"><h3>Full Blueprint JSON</h3>
<button class="json-toggle" onclick="this.nextElementSibling.classList.toggle('open');this.textContent=this.nextElementSibling.classList.contains('open')?'Hide Blueprint JSON':'Show Blueprint JSON'">&#128196; Show Blueprint JSON</button>
<div class="json-content"><pre><code id="rawBCode"></code></pre><button class="btn" style="margin-top:8px;background:var(--txt);color:var(--bg);width:auto;padding:7px 16px;font-size:.82rem" onclick="copyText(JSON.stringify(window._rawB,null,2))">Copy Blueprint JSON</button></div></div>
<div class="card"><h3>Full Module Results JSON</h3>
<button class="json-toggle" onclick="this.nextElementSibling.classList.toggle('open');this.textContent=this.nextElementSibling.classList.contains('open')?'Hide Module JSON':'Show Module JSON'">&#128196; Show Module Results JSON</button>
<div class="json-content"><pre><code id="rawMrCode"></code></pre><button class="btn" style="margin-top:8px;background:var(--txt);color:var(--bg);width:auto;padding:7px 16px;font-size:.82rem" onclick="copyText(JSON.stringify(window._rawMr,null,2))">Copy Module JSON</button></div></div></div>`;
ma.innerHTML=tabs+panels;
document.getElementById('rawBCode').innerHTML=hl(JSON.stringify(b,null,2));
document.getElementById('rawMrCode').innerHTML=hl(JSON.stringify(mr,null,2));
}

function showTab(id){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));const btn=event.currentTarget||event.target.closest('.tab');if(btn)btn.classList.add('on');const p=document.getElementById('p_'+id);if(p)p.classList.add('on');}

function renderExec(s){
let h=`<div class="card"><h3>&#127919; Executive Summary</h3>`;
h+=`<div class="sg"><div class="sb b"><div class="v">${s.total_modules_executed||21}</div><div class="l">Modules</div></div><div class="sb r"><div class="v">${s.critical_issues_count||0}</div><div class="l">Critical</div></div><div class="sb y"><div class="v">${s.high_priority_count||0}</div><div class="l">High Priority</div></div><div class="sb p"><div class="v">${s.total_recommendations||0}</div><div class="l">Recommendations</div></div></div>`;
if(s.critical_issues&&s.critical_issues.length){h+=`<h4>Critical Issues</h4><table><tr><th>Module</th><th>Action</th><th>Detail</th></tr>`;s.critical_issues.forEach(i=>{h+=`<tr class="issue"><td><span class="tag cr">CRITICAL</span> ${i.module||''}</td><td>${i.action||''}</td><td>${i.detail||''}</td></tr>`;});h+=`</table>`;}
if(s.high_priority_actions&&s.high_priority_actions.length){h+=`<h4>High Priority Actions</h4><table><tr><th>Module</th><th>Action</th><th>Detail</th></tr>`;s.high_priority_actions.forEach(i=>{h+=`<tr class="issue"><td><span class="tag hi">HIGH</span> ${i.module||''}</td><td>${i.action||''}</td><td>${i.detail||''}</td></tr>`;});h+=`</table>`;}
h+=`</div>`;return h;}

function renderEdit(e){
let h=`<div class="card"><h3>&#128221; Editorial & Writing Blueprint</h3>`;
const o=e.structural_outline||{};
h+=`<div class="sg"><div class="sb b"><div class="v">${o.total_estimated_words||'N/A'}</div><div class="l">Est. Words</div></div><div class="sb"><div class="v">${o.total_sections||0}</div><div class="l">H2 Sections</div></div><div class="sb p"><div class="v">${(e.direct_answer_blocks||[]).length}</div><div class="l">Answer Blocks</div></div><div class="sb g"><div class="v">${(e.smee_placement_markers||[]).length}</div><div class="l">SME Placements</div></div></div>`;
if(o.h1){h+=`<h4>H1 Title</h4><p style="font-size:.95rem;margin-bottom:12px"><strong>${o.h1.title||''}</strong></p><p style="margin-bottom:14px">${o.h1.purpose||''} | Target: ${o.h1.word_count_target||''}</p>`;}
if(o.h2_sections){h+=`<h4>Content Outline (${o.h2_sections.length} Sections)</h4><table><tr><th>#</th><th>Heading</th><th>Content Type</th><th>Word Target</th><th>Schema</th><th>Direct Answer</th></tr>`;o.h2_sections.forEach((s,i)=>{h+=`<tr><td>${i+1}</td><td><strong>${s.title||''}</strong></td><td>${s.content_type||''}</td><td>${s.word_count_target||''}</td><td>${s.schema_type||'none'}</td><td>${s.direct_answer_required?'&#10003;':'-'}</td></tr>`;if(s.h3_subsections){s.h3_subsections.forEach(j=>{h+=`<tr><td></td><td style="padding-left:20px;color:var(--txt3)">${j.title||''}</td><td>${j.content_type||''}</td><td>${j.word_count_target||''}</td><td></td><td></td></tr>`;});}});h+=`</table>`;}
const dab=e.direct_answer_blocks||[];
if(dab.length){h+=`<h4>Direct Answer Blocks (${dab.length})</h4><table><tr><th>ID</th><th>Heading Context</th><th>Word Count</th><th>Format</th><th>Citation Prob</th></tr>`;dab.forEach(d=>{h+=`<tr><td>${d.block_id||''}</td><td>${d.heading_context||''}</td><td>${d.target_word_count||''}</td><td>${d.extraction_format||''}</td><td>${d.citation_probability||''}</td></tr>`;});h+=`</table>`;}
const sm=e.smee_placement_markers||[];
if(sm.length){h+=`<h4>SME Quote Placements (${sm.length})</h4><table><tr><th>Expert</th><th>Title</th><th>Target Section</th><th>Priority</th><th>E-E-A-T Impact</th></tr>`;sm.forEach(s=>{h+=`<tr><td>${s.sme_name||''}</td><td>${s.sme_title||''}</td><td>${s.target_section||''}</td><td><span class="tag ${s.priority==='CRITICAL'?'cr':s.priority==='HIGH'?'hi':'md'}">${s.priority||''}</span></td><td>${s.eEat_enhancement||''}</td></tr>`;});h+=`</table>`;}
const ig=e.information_gain_checklist||[];
if(ig.length){h+=`<h4>Information Gain Checklist (${ig.length} Gaps)</h4><table><tr><th>Gap</th><th>Description</th><th>Opportunity</th><th>Action</th></tr>`;ig.forEach(g=>{h+=`<tr><td><span class="tag ${g.opportunity_level==='HIGH'?'cr':'hi'}">${g.opportunity_level||''}</span> ${g.category||''}</td><td>${g.description||''}</td><td>Competitor mentions: ${g.competitor_mention_count||0}</td><td>${g.recommended_action||''}</td></tr>`;});h+=`</table>`;}
const uv=e.unique_value_propositions||[];
if(uv.length){h+=`<h4>Unique Value Propositions (${uv.length})</h4><table><tr><th>UVP Type</th><th>Description</th><th>Differentiation Score</th><th>Recommendation</th></tr>`;uv.forEach(u=>{h+=`<tr><td>${u.uvp_type||''}</td><td>${u.description||''}</td><td>${u.differentiation_score||''}</td><td>${u.recommendation||''}</td></tr>`;});h+=`</table>`;}
const q=e.quality_targets||{};
if(Object.keys(q).length){h+=`<h4>Quality Targets</h4><table>`;Object.entries(q).forEach(([k,v])=>{h+=`<tr><td><strong>${k.replace(/_/g,' ')}</strong></td><td>${v}</td></tr>`;});h+=`</table>`;}
const fl=e.content_flow||{};
if(Object.keys(fl).length){h+=`<h4>Content Flow Strategy</h4><table>`;Object.entries(fl).forEach(([k,v])=>{h+=`<tr><td><strong>${k.replace(/_/g,' ')}</strong></td><td>${Array.isArray(v)?v.join(', '):v}</td></tr>`;});h+=`</table>`;}
h+=`</div>`;return h;}

function renderGeo(g){
let h=`<div class="card"><h3>&#127760; GEO & AEO Optimization</h3>`;
h+=`<div class="sg"><div class="sb ${(g.geo_readiness_score||0)>.6?'g':(g.geo_readiness_score||0)>.3?'y':'r'}"><div class="v">${(g.geo_readiness_score||0).toFixed(2)}</div><div class="l">GEO Readiness</div></div><div class="sb ${(g.rag_optimized_chunks||{}).rag_readiness_score>.6?'g':'y'}"><div class="v">${((g.rag_optimized_chunks||{}).rag_readiness_score||0).toFixed(3)}</div><div class="l">RAG Score</div></div><div class="sb b"><div class="v">${(g.rag_optimized_chunks||{}).total_chunks||0}</div><div class="l">RAG Chunks</div></div><div class="sb p"><div class="v">${(g.citation_triggers||[]).length}</div><div class="l">Citation Triggers</div></div></div>`;
const abs=g.answer_block_strategy||{};
if(Object.keys(abs).length){h+=`<h4>Answer Block Strategy</h4>`;Object.entries(abs).forEach(([type,cfg])=>{h+=`<h4 style="font-size:.84rem;margin-top:8px">${type.replace(/_/g,' ').toUpperCase()}</h4><table>`;if(typeof cfg==='object'&&!Array.isArray(cfg)){Object.entries(cfg).forEach(([k,v])=>{h+=`<tr><td><strong>${k.replace(/_/g,' ')}</strong></td><td>${typeof v==='object'?JSON.stringify(v):v}</td></tr>`;});}h+=`</table>`;});}
const ess=g.engine_specific_strategies||{};
if(Object.keys(ess).length){h+=`<h4>Engine-Specific Strategies</h4>`;Object.entries(ess).forEach(([eng,strats])=>{h+=`<h4 style="font-size:.84rem">${eng.replace(/_/g,' ').toUpperCase()}</h4><ul>`;strats.forEach(s=>{h+=`<li>${s}</li>`;});h+=`</ul>`;});}
const ct=g.citation_triggers||[];
if(ct.length){h+=`<h4>Citation Triggers (${ct.length})</h4><table><tr><th>Type</th><th>Probability</th><th>Position</th><th>Frequency</th><th>Recommendation</th></tr>`;ct.forEach(t=>{h+=`<tr><td>${t.trigger_type||''}</td><td>${t.citation_probability||''}</td><td>${t.optimal_position||''}</td><td>${t.frequency_in_competitors||0}</td><td>${t.recommendation||''}</td></tr>`;});h+=`</table>`;}
const cs=g.citation_source_targets||[];
if(cs.length){h+=`<h4>Required Citation Sources (${cs.length})</h4><table><tr><th>Type</th><th>Description</th><th>Priority</th></tr>`;cs.forEach(c=>{h+=`<tr><td>${c.type||''}</td><td>${c.description||''}</td><td><span class="tag ${c.priority==='CRITICAL'?'cr':c.priority==='HIGH'?'hi':'md'}">${c.priority||''}</span></td></tr>`;});h+=`</table>`;}
const imp=g.estimated_ai_visibility_improvement||{};
if(Object.keys(imp).length){h+=`<h4>Estimated Improvements</h4><table>`;Object.entries(imp).forEach(([k,v])=>{h+=`<tr><td><strong>${k.replace(/_/g,' ')}</strong></td><td>${v}</td></tr>`;});h+=`</table>`;}
h+=`</div>`;return h;}

function renderTech(t){
let h=`<div class="card"><h3>&#9881; Technical Payload</h3>`;
h+=`<div class="sg"><div class="sb b"><div class="v">${Object.keys(t.json_ld_schemas||{}).length}</div><div class="l">Schema Types</div></div><div class="sb ${(t.cannibalization_status||'')==='LOW'?'g':'r'}"><div class="v">${t.cannibalization_status||'N/A'}</div><div class="l">Cannibalization</div></div><div class="sb ${(t.hallucination_risk||'')==='MINIMAL'?'g':'r'}"><div class="v">${t.hallucination_risk||'N/A'}</div><div class="l">Hallucination Risk</div></div><div class="sb b"><div class="v">${t.dom_size||0}</div><div class="l">DOM Elements</div></div><div class="sb"><div class="v">${t.csr_rendering_status||'N/A'}</div><div class="l">Render Mode</div></div></div>`;
const schemas=t.json_ld_schemas||{};
if(Object.keys(schemas).length){h+=`<h4>JSON-LD Schemas (${Object.keys(schemas).length})</h4>`;Object.entries(schemas).forEach(([nm,sc])=>{const id='sch_'+nm.replace(/[^a-z0-9]/gi,'');h+=`<button class="json-toggle" onclick="document.getElementById('${id}').classList.toggle('open');this.textContent=document.getElementById('${id}').classList.contains('open')?'Hide ${nm.toUpperCase()} Schema':'Show ${nm.toUpperCase()} Schema'">&#128196; Show ${nm.toUpperCase()} Schema</button><div class="json-content" id="${id}"><pre><code>${hl(JSON.stringify(sc,null,2))}</code></pre></div>`;});}
const il=t.internal_linking_blueprint||{};
if(Object.keys(il).length){h+=`<h4>Internal Linking Blueprint</h4><table>`;Object.entries(il).forEach(([k,v])=>{if(typeof v!=='object')h+=`<tr><td><strong>${k.replace(/_/g,' ')}</strong></td><td>${v}</td></tr>`;});h+=`</table>`;}
const sv=t.schema_validation||{};
if(Object.keys(sv).length){h+=`<h4>Schema Validation</h4><table><tr><th>Schema</th><th>Valid</th><th>Errors</th></tr>`;Object.entries(sv).forEach(([k,v])=>{h+=`<tr${v.valid?'':' class="issue"'}><td>${k}</td><td><span class="tag ${v.valid?'lo':'cr'}">${v.valid?'VALID':'INVALID'}</span></td><td>${(v.errors||[]).join('; ')||'None'}</td></tr>`;});h+=`</table>`;}
const se=t.search_engine_coverage||{};
if(Object.keys(se).length){h+=`<h4>Search Engine Coverage</h4>`;if(se.engine_coverage){h+=`<table><tr><th>Engine</th><th>Coverage</th><th>Rich Results</th></tr>`;Object.entries(se.engine_coverage).forEach(([k,v])=>{h+=`<tr><td>${k}</td><td>${v.coverage}/${(v.supported_types||[]).length} types</td><td>${v.rich_results_eligible?'Yes':'No'}</td></tr>`;});h+=`</table>`;}}
h+=`</div>`;return h;}

function renderCDN(c){
let h=`<div class="card"><h3>&#128231; CDN & Edge Deployment</h3>`;
const ew=c.edge_worker_snippet||{};
if(ew.worker_code){h+=`<h4>Edge Worker Code (${ew.cdn_provider||'Cloudflare'})</h4><pre><code>${ew.worker_code}</code></pre>`;if(ew.testing_steps){h+=`<h4>Testing Steps</h4><ul>`;ew.testing_steps.forEach(s=>{h+=`<li>${s}</li>`;});h+=`</ul>`;}}
const sh=c.server_header_inspection||{};
if(sh.inspection_results){h+=`<h4>Server Header Inspection</h4><table><tr><th>Header</th><th>Expected</th><th>Current</th><th>Status</th></tr>`;sh.inspection_results.forEach(r=>{h+=`<tr class="${r.status==='CORRECT'?'':'issue'}"><td>${r.header}</td><td style="font-size:.8rem">${r.expected}</td><td>${r.current}</td><td><span class="tag ${r.status==='CORRECT'?'lo':'cr'}">${r.status}</span></td></tr>`;});h+=`</table>`;}
const pr=c.prerender_simulation||{};
if(Object.keys(pr).length){h+=`<h4>Pre-Render Simulation</h4><table>`;Object.entries(pr).forEach(([k,v])=>{if(typeof v!=='object')h+=`<tr><td><strong>${k.replace(/_/g,' ')}</strong></td><td>${v}</td></tr>`;else if(v&&typeof v==='object'){Object.entries(v).forEach(([k2,v2])=>{h+=`<tr><td style="padding-left:16px">${k2.replace(/_/g,' ')}</td><td>${v2}</td></tr>`;});}});h+=`</table>`;}
const cd=c.cdn_configuration||{};
if(Object.keys(cd).length){const id='cdn_cfg';h+=`<button class="json-toggle" onclick="document.getElementById('${id}').classList.toggle('open');this.textContent=document.getElementById('${id}').classList.contains('open')?'Hide CDN Config':'Show CDN Config'">&#128196; Show CDN Configuration</button><div class="json-content" id="${id}"><pre><code>${hl(JSON.stringify(cd,null,2))}</code></pre></div>`;}
const dg=c.deployment_guide||{};
if(dg.deployment_steps){h+=`<h4>Deployment Guide</h4><ul>`;dg.deployment_steps.forEach(s=>{h+=`<li>${s}</li>`;});h+=`</ul>`;}
h+=`</div>`;return h;}

function renderSnt(s){
let h=`<div class="card"><h3>&#128737; Post-Publish Sentinel Brief</h3>`;
const tc=s.tracking_configuration||{};
if(tc.monitoring_targets){h+=`<h4>Monitoring Targets</h4><table><tr><th>Engine</th><th>Frequency</th><th>Queries</th><th>Metrics</th></tr>`;Object.entries(tc.monitoring_targets).forEach(([k,v])=>{h+=`<tr><td>${k.replace(/_/g,' ')}</td><td>${v.check_frequency||''}</td><td>${(v.queries_to_monitor||[]).length}</td><td>${(v.metrics||[]).join(', ')}</td></tr>`;});h+=`</table>`;}
const at=s.alert_system||{};
if(at.alert_types){h+=`<h4>Alert Configuration (${at.alert_types.length})</h4><table><tr><th>Alert</th><th>Trigger</th><th>Severity</th><th>Notification</th><th>Response</th></tr>`;at.alert_types.forEach(a=>{const sv=a.severity||'';const rw=sv==='CRITICAL'||sv==='HIGH'?' class="issue"':'';h+=`<tr${rw}><td><strong>${a.alert||''}</strong></td><td style="font-size:.8rem">${a.trigger||''}</td><td><span class="tag ${sv==='CRITICAL'?'cr':sv==='HIGH'?'hi':sv==='POSITIVE'?'lo':'md'}">${sv}</span></td><td>${a.notification||''}</td><td style="font-size:.8rem">${a.response_protocol||''}</td></tr>`;});h+=`</table>`;}
const ib=s.indexing_status||{};
if(ib.indexing_checks){h+=`<h4>Indexing Status</h4><table><tr><th>Check</th><th>Status</th></tr>`;Object.entries(ib.indexing_checks).forEach(([k,v])=>{h+=`<tr${v===false?' class="issue"':''}><td>${k.replace(/_/g,' ')}</td><td><span class="tag ${v===true||v==='PASS'?'lo':v===false?'cr':'md'}">${v}</span></td></tr>`;});h+=`</table>`;}
const rb=s.refresh_brief||{};
if(rb.refresh_brief&&rb.refresh_brief.length){h+=`<h4>Content Refresh Brief (${rb.refresh_brief.length} items)</h4><table><tr><th>Section</th><th>Action</th><th>Priority</th><th>Effort</th></tr>`;rb.refresh_brief.forEach(r=>{const pv=r.priority||'';const rw=pv==='CRITICAL'||pv==='HIGH'?' class="issue"':'';h+=`<tr${rw}><td>${r.section||''}</td><td>${r.action||''}</td><td><span class="tag ${pv==='CRITICAL'?'cr':pv==='HIGH'?'hi':'md'}">${pv}</span></td><td>${r.estimated_effort||''}</td></tr>`;});h+=`</table>`;}
const rg=s.rollback_guards||{};
if(rg.auto_rollback_triggers){h+=`<h4>Rollback Guardrails</h4><table><tr><th>Trigger</th><th>Condition</th><th>Action</th></tr>`;rg.auto_rollback_triggers.forEach(r=>{h+=`<tr><td>${r.trigger||''}</td><td style="font-size:.8rem">${r.condition||''}</td><td style="font-size:.8rem">${r.action||''}</td></tr>`;});h+=`</table>`;}
h+=`</div>`;return h;}

function isIssue(v){
if(typeof v==='boolean')return v===false;
if(typeof v==='number')return false;
if(typeof v!=='string')return false;
const s=v.trim();const u=s.toUpperCase();
if(!s)return false;
if(/(NOT_?CONFIGURED|NOT_?SET|NO_?DATA|NO_?TEXT|NO_?URL|NO_?CONTENT|FAILED|MISSING|INCORRECT|INVALID|NEEDS_?WORK|BLOCKED|BROKEN|UNAVAILABLE|TIMED_?OUT|NOT_?DETECTED|REQUIRES_?JS|NOT_?FOUND|UNSAFE|PROBLEM|STOPPED)/.test(u))return true;
if(s.length>40)return false;
return /^(ERROR|HIGH|CRITICAL|POOR|NO|FALSE|BAD|ISSUE|WARNING|VERIFY|ATTENTION|REQUIRED)$/.test(u);
}
function renderModule(mk,mr){
if(!mr||typeof mr!=='object')return`<div class="card"><h3>${mk}: ${MN[mk]||''}</h3><p style="color:var(--txt3)">No data returned for this module.</p></div>`;
if(mr.error)return`<div class="card"><h3>${mk}: ${MN[mk]||''}</h3><p style="background:var(--issue-fill);color:var(--issue-ink);font-weight:700;padding:10px 14px;border-radius:8px">Error: ${esc(mr.error)}</p></div>`;
let h=`<div class="card"><h3>${mk}: ${MN[mk]||''}</h3>`;
try{
const SKIPKEYS=['module','module_name','recommendations','implementation_steps','where_to_add','detailed_analysis'];
const pretty=k=>esc(String(k).replace(/_/g,' '));
function cell(val,kk){
if(val==null)return'&mdash;';
if(typeof val==='object')return rv(val,kk);
const s=String(val);
return isIssue(val)?'<span class="issue">'+esc(s)+'</span>':esc(s);
}
function rv(v,k){
if(v==null)return'<span class="dash">&mdash;</span>';
if(typeof v==='boolean')return v?'<span class="ok">&#10003; Yes</span>':'<span class="no">&#10007; No</span>';
if(typeof v==='number')return'<span class="num">'+esc(String(v))+'</span>';
if(typeof v==='string')return isIssue(v)?'<span class="issue">'+esc(v)+'</span>':'<span class="str">'+esc(v)+'</span>';
if(Array.isArray(v)){
if(v.length===0)return'<span class="dash">&mdash;</span>';
if(typeof v[0]==='object'&&v[0]!==null){
let ks=[];try{ks=[...new Set(v.flatMap(i=>Object.keys(i)))];}catch(e){ks=Object.keys(v[0]||{});}
if(ks.length){
let t='<div style="overflow-x:auto"><table><tr>';ks.forEach(kk=>{t+='<th>'+pretty(kk)+'</th>';});t+='</tr>';
v.slice(0,25).forEach(item=>{let rowIss=false;const c=ks.map(kk=>{let val=item[kk];if(!rowIss&&isIssue(val))rowIss=true;return '<td style="font-size:.8rem">'+((typeof val==='object'&&val!==null)?rv(val,kk):cell(val,kk))+'</td>';}).join('');t+='<tr'+(rowIss?' class="issue"':'')+'>'+c+'</tr>';});
if(v.length>25)t+='<tr><td colspan="'+ks.length+'" class="more">+'+(v.length-25)+' more</td></tr>';
return t+'</table></div>';
}
}
return'<div class="chips">'+v.map(i=>'<span class="chip">'+esc(String(i))+'</span>').join('')+'</div>';
}
if(typeof v==='object'){
const entries=Object.entries(v);
if(!entries.length)return'<span class="dash">&mdash;</span>';
if(entries.some(([,val])=>val&&typeof val==='object')){
let s='<div class="subs">';
entries.forEach(([kk,val])=>{
s+='<div class="sub"><div class="subh">'+pretty(kk)+'</div><div class="subb">'+rv(val,kk)+'</div></div>';
});
return s+'</div>';
}
let t='<table class="kv2">';
entries.forEach(([kk,val])=>{
let rowIss=isIssue(val);
t+='<tr'+(rowIss?' class="issue"':'')+'><th>'+pretty(kk)+'</th><td>'+rv(val,kk)+'</td></tr>';
});
return t+'</table>';
}
return esc(String(v));
};
const statKeys=Object.keys(mr).filter(k=>!SKIPKEYS.includes(k)&&typeof mr[k]==='number'&&/score|count|total|ratio|percentage|probability|rate|density|strength|readiness|coverage|freshness|depth|breadth|size|elements|words|minutes|risk|penalty|estimate|frequency|number|priority|index|percent|health|quality/i.test(k));
const statShown=statKeys.slice(0,10);
if(statShown.length){
h+='<div class="sg">';
statShown.forEach(k=>{
const v=mr[k];
const pct=/ratio|percentage|probability|score|rate|density|strength|readiness|coverage|freshness|depth|breadth|penalty|index|percent|health|quality/i.test(k);
let disp=(pct&&v<=1.5)?(Math.round(v*100)+'%'):String(v);
const neg=/broken|error|issue|missing|invalid|critical|high_prio|problem|risk|fail|penalty/i.test(k);
let cls;
if(pct){cls=v>=0.7?'g':v>=0.4?'y':'r';}
else if(neg){cls=v>0?'r':'g';}
else{cls=v===0?'y':'b';}
h+=`<div class="sb ${cls}"><div class="v">${esc(disp)}</div><div class="l">${pretty(k)}</div></div>`;
});
h+='</div>';
}
if(mr.recommendations&&mr.recommendations.length){
h+='<div class="mblock"><div class="mh">&#9889; Recommendations</div>';
h+='<table><tr><th style="width:120px">Priority</th><th>Action</th><th>Detail</th></tr>';
mr.recommendations.forEach(r=>{
const p=r.priority||'MEDIUM';
const pc=p==='CRITICAL'?'cr':p==='HIGH'?'hi':p==='LOW'?'lo':'md';
const rw=p==='CRITICAL'||p==='HIGH'?' class="issue"':'';
h+='<tr'+rw+'><td><span class="tag '+pc+'">'+esc(p)+'</span></td><td><strong>'+esc(r.action||'')+'</strong></td><td style="font-size:.82rem">'+esc(r.detail||'')+'</td></tr>';
});
h+='</table></div>';
}
if(mr.implementation_steps&&mr.implementation_steps.length){
h+='<div class="mblock green"><div class="mh">&#9989; Implementation Steps</div><ol class="steps">';
mr.implementation_steps.forEach(s=>{h+='<li>'+esc(String(s))+'</li>';});
h+='</ol></div>';
}
if(mr.where_to_add&&mr.where_to_add.length){
h+='<div class="mblock cyan"><div class="mh">&#128205; Where To Add</div><ul class="where">';
mr.where_to_add.forEach(s=>{h+='<li>'+esc(String(s))+'</li>';});
h+='</ul></div>';
}
if(mr.detailed_analysis&&typeof mr.detailed_analysis==='object'){
h+='<div class="mblock"><div class="mh">&#128269; Detailed Analysis</div>';
Object.entries(mr.detailed_analysis).forEach(([k,v])=>{
h+='<div class="acc"><button class="accb" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">'+pretty(k)+' <span class="accarrow">&#9660;</span></button><div class="accp">'+rv(v,k)+'</div></div>';
});
h+='</div>';
}
Object.keys(mr).forEach(k=>{
if(SKIPKEYS.includes(k)||statShown.includes(k))return;
h+='<div class="mblock"><div class="mh">'+pretty(k)+'</div>'+rv(mr[k],k)+'</div>';
});
}catch(e){h+='<p style="background:var(--issue-fill);color:var(--issue-ink);padding:12px;border-radius:8px;font-weight:700">Render error: '+esc(e.message)+'</p>';}
h+=`</div>`;return h;}

function hl(j){return j.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"([^"]+)"(?=\s*:)/g,'<span class="jk">"$1"</span>').replace(/"([^"]*)"/g,'<span class="js">"$1"</span>').replace(/\b(-?\d+\.?\d*)\b/g,'<span class="jn">$1</span>').replace(/\b(true|false|null)\b/g,'<span class="jb">$1</span>');}
</script>
</body>
</html>"""

if __name__=='__main__':
    print("\n"+"="*60)
    print("  Intent, Entity & Semantic Intelligence Platform")
    print("  Web Interface: http://localhost:5000")
    print("="*60+"\n")
    app.run(host='0.0.0.0',port=5000,debug=False,threaded=True)
