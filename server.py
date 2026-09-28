"""
Full Web Server with all 22 module outputs + 5 blueprint outputs.
Real-time data integration. Run: python server.py
"""
import sys,os,json,traceback,urllib.request,urllib.parse,re,secrets,threading,logging
from pathlib import Path
from flask import Flask,request,jsonify,Response,g
from functools import wraps
sys.path.insert(0,str(Path(__file__).parent))
from intent_entity_platform.core.engine import PlatformEngine
from intent_entity_platform.core.input_framework import (
    InputFramework,SeedKeywordInput,FirstPartyData,SMEAsset,
    BrandConstraints,AudienceProfile,TechnicalCredentials
)
from intent_entity_platform.utils.web_data import web_search as _real_web_search
from intent_entity_platform.utils.web_data import extract_page as _extract_page_shared
from intent_entity_platform.utils.security import (
    is_url_allowed, safe_fetch, check_rate_limit, validate_json_dict)
from intent_entity_platform.utils.serp_provider import serp_fetch
from intent_entity_platform.utils.content_scorer import score_content
from intent_entity_platform.utils.gsc_quickwins import parse_gsc_csv, quick_wins
from intent_entity_platform.utils.brief_generator import generate_brief

APP_DEBUG = os.environ.get("APP_DEBUG", "false").lower() in ("1","true","yes")
APP_VERSION = "3.0.0-enterprise"
MAX_JSON_BYTES = 6 * 1024 * 1024

app = None  # created below (single Flask instance; see app=Flask(__name__))
try:
    app.config["MAX_CONTENT_LENGTH"] = MAX_JSON_BYTES
except Exception:
    pass

def _client_ip():
    try:
        fwd = request.headers.get("X-Forwarded-For", "")
        if fwd:
            return fwd.split(",")[0].strip()[:64]
    except Exception:
        pass
    try:
        return (request.remote_addr or "unknown")[:64]
    except Exception:
        return "unknown"

def _safe_error(public_msg, exc=None, code=500):
    try:
        logging.getLogger("content-platform").exception(
            "api_error: %s", str(exc)[:500] if exc else public_msg)
    except Exception:
        pass
    if APP_DEBUG and exc is not None:
        return jsonify({"error": public_msg, "trace": traceback.format_exc()}), code
    return jsonify({"error": public_msg}), code

def _apply_security_headers(resp):
    try:
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "SAMEORIGIN"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # Allow self + Google Fonts (used by UI) + inline styles/scripts the app ships.
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; "
            "connect-src 'self'; frame-ancestors 'self'; base-uri 'self'")
        if request.url.startswith("https://"):
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    except Exception:
        pass
    return resp

import time,smtplib,io,datetime
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

# ---------------------------------------------------------------------------
# Real-time analysis progress tracking (polled by the browser)
# ---------------------------------------------------------------------------
_PROGRESS_STORE={}
_PROGRESS_TTL=900   # 15 minutes; stale entries are garbage-collected
_TOTAL_MODULES=22

def _progress_gc():
    """Drop progress entries older than the TTL (bounded memory)."""
    now=time.time()
    stale=[k for k,v in _PROGRESS_STORE.items() if now-v.get('started_at',0)>_PROGRESS_TTL]
    for k in stale:
        _PROGRESS_STORE.pop(k,None)

def _make_progress_recorder(analysis_id):
    """Return a progress_callback wired to the shared progress store."""
    _progress_gc()
    _PROGRESS_STORE[analysis_id]={
        "analysis_id": analysis_id,
        "phase": "Starting",
        "phase_label": "Preparing analysis engine...",
        "current_module": None,
        "current_module_name": "",
        "module_status": {},      # M01..M22 -> running/completed/error
        "completed_modules": [],
        "errors": [],
        "phases_done": [],
        "percent": 0,
        "done": False,
        "started_at": time.time(),
        "updated_at": time.time(),
    }

    def _rec(step, name, status):
        rec=_PROGRESS_STORE.get(analysis_id)
        if rec is None:
            return
        now=time.time()
        rec["updated_at"]=now
        if step in ("SETUP","FETCH"):
            rec["phase"]=name
            rec["phase_label"]=name
            if status=="running":
                rec["phase_status"]="running"
            elif status=="completed":
                rec["phase_status"]="completed"
                if name not in rec["phases_done"]:
                    rec["phases_done"].append(name)
        elif step.startswith("M"):
            if status=="running":
                rec["current_module"]=step
                rec["current_module_name"]=name
                rec["module_status"][step]="running"
            elif status=="completed":
                rec["module_status"][step]="completed"
                if step not in rec["completed_modules"]:
                    rec["completed_modules"].append(step)
                if rec.get("current_module")==step:
                    rec["current_module"]=None
                    rec["current_module_name"]=""
            elif str(status).startswith("error"):
                rec["module_status"][step]="error"
                rec["errors"].append(f"{step} ({name}): {status}")
                if rec.get("current_module")==step:
                    rec["current_module"]=None
                    rec["current_module_name"]=""
        completed=len(rec.get("completed_modules",[]))
        base=round(completed/_TOTAL_MODULES*100)
        rec["percent"]=min(100, base)
        rec["done"]=rec.get("done",False) or completed>=_TOTAL_MODULES
        if rec["done"]:
            rec["percent"]=100
            rec["current_module"]=None
            rec["current_module_name"]=""
            rec["phase"]="Complete"
            rec["phase_label"]="All 22 modules completed"
        try:
            from intent_entity_platform.utils import persistence as _pstp
            _pstp.progress_put(analysis_id, rec)
        except Exception:
            pass
    return _rec

def _mark_progress_done(analysis_id, errors=None):
    rec=_PROGRESS_STORE.get(analysis_id)
    if not rec:
        return
    rec["done"]=True
    rec["percent"]=100
    rec["current_module"]=None
    rec["current_module_name"]=""
    rec["phase"]="Complete"
    rec["phase_label"]="All 22 modules completed"
    if errors:
        rec["errors"]=list(errors)
    rec["updated_at"]=time.time()
    try:
        from intent_entity_platform.utils import persistence as _pstq
        _pstq.progress_put(analysis_id, rec)
    except Exception:
        pass

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
    'M20':'Digital PR Engine','M21':'DOM Inspector','M22':'Live LLM Citation Tester'
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
        'title':ParagraphStyle('t',fontName=regb,fontSize=26,leading=32,textColor=HexColor('#ffffff'),spaceAfter=2),
        'tbrand':ParagraphStyle('tb',fontName=reg,fontSize=10,leading=14,textColor=HexColor('#c7d2fe'),spaceAfter=4),
        'cover_sub':ParagraphStyle('cs',fontName=reg,fontSize=11,leading=16,textColor=HexColor('#e0e7ff'),spaceAfter=4),
        'sub':ParagraphStyle('sub',fontName=reg,fontSize=9,leading=13,textColor=HexColor('#415070'),spaceAfter=2),
        'h2':ParagraphStyle('h2',fontName=regb,fontSize=16,leading=20,textColor=_INK,spaceBefore=8,spaceAfter=4),
        'h3':ParagraphStyle('h3',fontName=regb,fontSize=11.5,leading=15,textColor=_BRAND,spaceBefore=10,spaceAfter=3),
        'h4':ParagraphStyle('h4',fontName=regb,fontSize=9.5,leading=13,textColor=_ACCENT,spaceBefore=7,spaceAfter=2),
        'body':ParagraphStyle('body',fontName=reg,fontSize=9.2,leading=13.5,textColor=_TXT_DARK,spaceAfter=4,splitLongWords=1),
        'cell':ParagraphStyle('cell',fontName=reg,fontSize=8.2,leading=11.5,textColor=_TXT_DARK,splitLongWords=1),
        'cellb':ParagraphStyle('cellb',fontName=regb,fontSize=8.4,leading=11.5,textColor=_INK,splitLongWords=1),
        'th':ParagraphStyle('th',fontName=regb,fontSize=8,leading=11,textColor=HexColor('#ffffff'),splitLongWords=1),
        'note':ParagraphStyle('note',fontName=reg,fontSize=7.8,leading=10,textColor=_TXT_MUT,spaceBefore=3),
        'statlbl':ParagraphStyle('sl',fontName=reg,fontSize=7.5,leading=9.5,textColor=_TXT_MUT,alignment=1),
        'statval':ParagraphStyle('sv',fontName=regb,fontSize=17,leading=21,textColor=_BRAND,alignment=1),
        'raw':ParagraphStyle('raw',fontName=_PDF_MONO,fontSize=6,leading=7.5,textColor=HexColor('#374151'),splitLongWords=1),
        'toc':ParagraphStyle('toc',fontName=reg,fontSize=9.5,leading=16,textColor=_TXT_DARK,leftIndent=4),
        'tocc':ParagraphStyle('tocc',fontName=regb,fontSize=12,leading=18,textColor=_INK),
        'TOCHeading1':ParagraphStyle(name='TOCHeading1',fontName=regb,fontSize=12.5,leading=17,textColor=_BRAND),
    }

# ---- Professional design system (slate + indigo + refined accents) ----
_INK=HexColor('#0f172a')            # near-black slate for headings
_TXT_DARK=HexColor('#1e293b')       # body ink
_TXT_MUT=HexColor('#64748b')        # muted label text
_BRAND=HexColor('#4f46e5')          # indigo-600 primary
_BRAND_DARK=HexColor('#3730a3')     # indigo-700
_BRAND_LIGHT=HexColor('#eef2ff')    # indigo-50 panel fill
_ACCENT=HexColor('#0891b2')         # cyan-600 secondary
_OK_GREEN=HexColor('#16a34a')
_WARN_AMBER=HexColor('#d97706')
_ERR_RED=HexColor('#dc2626')
_NAVY=HexColor('#0f172a')           # cover hero navy
_NAVY2=HexColor('#1e293b')          # secondary navy band
_TBL_HEAD=HexColor('#4338ca')       # indigo-700 header
_TBL_LINE=HexColor('#e2e8f0')       # slate-200 hairline
_TBL_ALT=HexColor('#f8fafc')        # slate-50 zebra
_CARD_BG=HexColor('#ffffff')
_CARD_BORDER=HexColor('#e2e8f0')
_GOLD=HexColor('#f59e0b')           # accent highlight

def _status_color(val):
    s=str(val).upper()
    if 'CRITICAL' in s or 'ERROR' in s or 'FAILED' in s or 'INVALID' in s or 'BROKEN' in s or 'MISSING' in s or 'NOT' in s:
        return HexColor('#dc2626')
    if 'HIGH' in s or 'RISK' in s or 'POOR' in s:
        return HexColor('#d97706')
    if 'LOW' in s or 'OK' in s or 'PASS' in s or 'VALID' in s or 'MINIMAL' in s or 'GOOD' in s:
        return HexColor('#059669')
    if 'MEDIUM' in s or 'MODERATE' in s:
        return HexColor('#ca8a04')
    return HexColor('#1f2937')

def _priority_tag(val):
    s=str(val).upper()
    if s=='CRITICAL': return HexColor('#dc2626')
    if s=='HIGH': return HexColor('#d97706')
    if s=='MEDIUM': return HexColor('#ca8a04')
    if s=='LOW': return HexColor('#059669')
    return HexColor('#1f2937')

def _pdf_footer(canvas,doc):
    canvas.saveState()
    page_h=doc.pagesize[1]
    # top accent rule
    canvas.setStrokeColor(HexColor('#e2e8f0')); canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin,page_h-doc.topMargin-1,doc.width+doc.leftMargin,page_h-doc.topMargin-1)
    # footer band
    canvas.setFillColor(HexColor('#f1f5f9'))
    canvas.rect(doc.leftMargin-6,doc.bottomMargin-26,doc.width+12,26,stroke=0,fill=1)
    canvas.setStrokeColor(_BRAND); canvas.setLineWidth(1.6)
    canvas.line(doc.leftMargin-6,doc.bottomMargin-0,doc.width+doc.leftMargin+6,doc.bottomMargin-0)
    canvas.setFont(_F(False),7)
    canvas.setFillColor(_TXT_MUT)
    canvas.drawString(doc.leftMargin,doc.bottomMargin-16,'Intent, Entity & Semantic Intelligence Platform  \u00b7  Real-Time 22-Module Analysis')
    canvas.drawRightString(doc.width+doc.leftMargin,doc.bottomMargin-16,'Page %d'%(doc.page))
    canvas.restoreState()

def _cover_page(canvas,doc,title,mode,target,brand,now,exec_stats):
    canvas.saveState()
    w,h=doc.pagesize
    # ---- Full-bleed hero: layered navy bands with a clean angled accent ----
    canvas.setFillColor(_NAVY)
    canvas.rect(0,h-235,w,235,stroke=0,fill=1)
    canvas.setFillColor(_NAVY2)
    canvas.rect(0,h-235,w,235,stroke=0,fill=1)
    # diagonal indigo slash (modern geometric accent)
    p=canvas.beginPath()
    p.moveTo(0,h-235); p.lineTo(w,h-196); p.lineTo(w,h-226); p.lineTo(0,h-265); p.close()
    canvas.setFillColor(_BRAND_DARK); canvas.drawPath(p,stroke=0,fill=1)
    p2=canvas.beginPath()
    p2.moveTo(0,h-262); p2.lineTo(w,h-223); p2.lineTo(w,h-230); p2.lineTo(0,h-269); p2.close()
    canvas.setFillColor(_BRAND); canvas.drawPath(p2,stroke=0,fill=1)
    # subtle grid dots (professional texture, not childish circles)
    canvas.setFillColor(HexColor('#334155'))
    for gx in range(int(40),int(w-20),44):
        for gy in range(int(h-205),int(h-40),40):
            canvas.circle(gx,gy,1.1,stroke=0,fill=1)
    # gold accent line
    canvas.setFillColor(_GOLD)
    canvas.rect(40,h-198,w-80,3,stroke=0,fill=1)
    # Brand wordmark
    canvas.setFont(_F(True),8); canvas.setFillColor(HexColor('#a5b4fc'))
    canvas.drawString(40,h-150,'INTENT  \u00b7  ENTITY  \u00b7  SEMANTIC INTELLIGENCE PLATFORM')
    # Title block
    canvas.setFont(_F(True),30); canvas.setFillColor(HexColor('#ffffff'))
    canvas.drawString(40,h-178,'Content Intelligence Report')
    canvas.setFont(_F(False),12.5); canvas.setFillColor(HexColor('#c7d2fe'))
    canvas.drawString(40,h-198,'Real-Time 22-Module Analysis  \u00b7  Generated: %s'%now)
    # ---- Body metadata as clean label/value rows ----
    y=h-268
    def meta_line(label,val,yloc):
        canvas.setFillColor(_BRAND)
        canvas.rect(40,yloc-4,4,26,stroke=0,fill=1)
        canvas.setFont(_F(True),7); canvas.setFillColor(_TXT_MUT)
        canvas.drawString(54,yloc+13,label.upper())
        canvas.setFont(_F(False),11.5); canvas.setFillColor(_TXT_DARK)
        canvas.drawString(54,yloc-1,(val or 'N/A')[:90])
    meta_line('Analysis Mode',mode,y); y-=46
    meta_line('Target',target,y); y-=46
    meta_line('Brand',brand or 'N/A',y); y-=46
    meta_line('Modules Executed',str(exec_stats[0])+' of 22',y)
    # ---- Stat cards strip (clean white cards, colored top rule) ----
    cards=[('Modules',exec_stats[0],_BRAND),
           ('Critical',exec_stats[1],_ERR_RED),
           ('High Priority',exec_stats[2],_WARN_AMBER),
           ('Recommendations',exec_stats[3],_OK_GREEN)]
    cw=(w-80-3*16)/4
    for i,(lbl,val,col) in enumerate(cards):
        x=40+i*(cw+16)
        canvas.setFillColor(_CARD_BG)
        canvas.roundRect(x,56,cw,66,8,stroke=0,fill=1)
        canvas.setStrokeColor(_CARD_BORDER); canvas.setLineWidth(0.8)
        canvas.roundRect(x,56,cw,66,8,stroke=1,fill=0)
        canvas.setFillColor(col)
        canvas.roundRect(x,56,cw,4,2,stroke=0,fill=1)
        canvas.setFont(_F(True),22); canvas.setFillColor(_INK)
        canvas.drawCentredString(x+cw/2,92,str(val))
        canvas.setFont(_F(False),7.5); canvas.setFillColor(_TXT_MUT)
        canvas.drawCentredString(x+cw/2,76,lbl.upper())
    # Footnote
    canvas.setFillColor(_ACCENT)
    canvas.roundRect(40,22,w-80,22,5,stroke=0,fill=1)
    canvas.setFont(_F(False),7.0); canvas.setFillColor(HexColor('#ecfeff'))
    canvas.drawString(50,28,'All module outputs derive from live research: SERP, Wikidata, Wayback Machine, competitor analysis, HTTP, structured data & verified statistics.')
    canvas.restoreState()

def _section_banner(story,styles,no,title):
    nos=ParagraphStyle('n',fontName=_F(True),fontSize=12,textColor=HexColor('#ffffff'))
    tits=ParagraphStyle('t2',fontName=_F(True),fontSize=14,leading=18,textColor=HexColor('#ffffff'))
    t=Table([[Paragraph('<font color="#ffffff">%s</font>'%_esc_pdf(no),nos),
              Paragraph('<font color="#ffffff">%s</font>'%_esc_pdf(title),tits)]],
        colWidths=[34,None],hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(0,0),_BRAND_DARK),
                           ('BACKGROUND',(1,0),(1,0),_BRAND),
                           ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                           ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),
                           ('LEFTPADDING',(0,0),(0,0),0),('LEFTPADDING',(1,0),(1,0),12),
                           ('RIGHTPADDING',(0,0),(-1,-1),12),
                           ('BOX',(0,0),(-1,-1),0.5,HexColor('#312e81'))]))
    story.append(t)
    story.append(Spacer(1,8))

def _add_heading(story,styles,text,kind='h2'):
    story.append(KeepTogether([Paragraph(text,styles[kind])]))

def _add_table(story,rows,styles,width,maxrows=40):
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
    cell_texts={k:[] for k in keys}
    for r in rows[:maxrows]:
        rowcells=[]
        for k in keys:
            v=r.get(k,'')
            cell_texts[k].append(_txt(v))
            p=ParagraphStyle('c',fontName=_F(False),fontSize=8.2,leading=11.5,textColor=_status_color(v) if isinstance(v,str) and len(str(v))<40 else _TXT_DARK,splitLongWords=1)
            rowcells.append(Paragraph(_txt(v),p))
        data.append(rowcells)
    # Proportional column widths: weight by content length (min 15%, max 40%)
    lengths=[max(len(_pretty(keys[i])), max((len(t) for t in cell_texts[keys[i]]), default=0)) for i in range(len(keys))]
    total=sum(lengths) or 1
    col_widths=[max(width*0.12, min(width*0.42, width*(l/total))) for l in lengths]
    # Normalize so the total exactly equals the available width
    scale=width/sum(col_widths)
    col_widths=[w*scale for w in col_widths]
    t=Table(data,repeatRows=1,colWidths=col_widths,hAlign='LEFT')
    cmds=[
        ('GRID',(0,0),(-1,-1),0.4,_TBL_LINE),
        ('BACKGROUND',(0,0),(-1,0),_TBL_HEAD),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LINEBELOW',(0,0),(-1,0),1.2,_BRAND_DARK),
    ]
    for i in range(1,len(data)):
        if i%2==0:
            cmds.append(('BACKGROUND',(0,i),(-1,i),_TBL_ALT))
    t.setStyle(TableStyle(cmds))
    story.append(t)
    notes=[]
    if len(rows)>maxrows:
        notes.append('+ %d more rows (full data in appendix)'%(len(rows)-maxrows))
    if len(all_keys)>len(keys):
        notes.append('+ %d more fields (in appendix)'%(len(all_keys)-len(keys)))
    if notes:
        story.append(Paragraph(' &nbsp; '.join(notes),styles['note']))

def _add_kv(story,styles,items,width):
    rows=[]
    for k,v in items:
        lbl=Paragraph(_pretty(k),ParagraphStyle('l',fontName=_F(True),fontSize=8,leading=11,textColor=_TXT_DARK))
        valp=ParagraphStyle('v',fontName=_F(False),fontSize=8.4,leading=11.5,textColor=_status_color(v) if isinstance(v,str) and len(str(v))<40 else _TXT_DARK,splitLongWords=1)
        val=Paragraph(_txt(v),valp)
        rows.append([lbl,val])
    t=Table(rows,colWidths=[width*0.38,width*0.62],hAlign='LEFT')
    cmds=[('GRID',(0,0),(-1,-1),0.4,_TBL_LINE),
          ('VALIGN',(0,0),(-1,-1),'TOP'),
          ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
          ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
          ('BACKGROUND',(0,0),(0,-1),HexColor('#f8fafc'))]
    t.setStyle(TableStyle(cmds))
    story.append(t)

def _add_content(story,data,styles,depth=0,width=0):
    if depth>5: return
    if isinstance(data,dict):
        scalars=[];nested=[];lists=[];tail=[]
        for k,v in data.items():
            if k in ('raw_html','page_text','recommendation_playbook','score_benchmarks','live_verified_statistics'): continue
            if k in ('recommendations','implementation_steps','where_to_add'):
                tail.append((k,v)); continue
            if isinstance(v,dict): nested.append((k,v))
            elif isinstance(v,list): lists.append((k,v))
            else: scalars.append((k,v))
        if scalars:
            _add_kv(story,styles,scalars,width or _DEFAULT_PDF_WIDTH)
            story.append(Spacer(1,4))
        for k,v in lists:
            if v and all(isinstance(x,dict) for x in v):
                _add_heading(story,styles,_pretty(k),'h3')
                _add_table(story,v,styles,width or _DEFAULT_PDF_WIDTH)
            else:
                _add_heading(story,styles,_pretty(k),'h3')
                for item in v:
                    story.append(Paragraph('&#8226; '+_txt(item),styles['body']))
        for k,v in nested:
            if depth>=3:
                _add_heading(story,styles,_pretty(k),'h4')
                _add_kv(story,styles,list(v.items()),width or _DEFAULT_PDF_WIDTH)
            else:
                _add_heading(story,styles,_pretty(k),'h3')
                _add_content(story,v,styles,depth+1,width or _DEFAULT_PDF_WIDTH)
        for k,v in tail:
            if isinstance(v,list) and v and all(isinstance(x,dict) for x in v):
                _add_heading(story,styles,_pretty(k),'h3')
                _add_table(story,v,styles,width or _DEFAULT_PDF_WIDTH)
            elif isinstance(v,list):
                _add_heading(story,styles,_pretty(k),'h3')
                for item in v:
                    story.append(Paragraph('&#8226; '+_txt(item),styles['body']))
            else:
                _add_heading(story,styles,_pretty(k),'h3')
                _add_kv(story,styles,list(v.items()),width or _DEFAULT_PDF_WIDTH)
    elif isinstance(data,list):
        for item in data:
            if isinstance(item,dict):
                _add_kv(story,styles,list(item.items()),width or _DEFAULT_PDF_WIDTH)
            else:
                story.append(Paragraph('&#8226; '+_txt(item),styles['body']))
    else:
        story.append(Paragraph(_txt(data),styles['body']))

def _add_section(story,styles,title,data,width=0):
    story.append(KeepTogether([Paragraph(title,styles['h2']),
                               HRFlowable(width='100%',thickness=1.2,color=_BRAND,spaceBefore=2,spaceAfter=8)]))
    if isinstance(data,dict) and not data:
        story.append(Paragraph('<i>No data produced for this section.</i>',styles['note']))
    else:
        _add_content(story,data,styles,width=width or _DEFAULT_PDF_WIDTH)

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

_DEFAULT_PDF_WIDTH=440  # thread-safe fallback; real width passed explicitly per-report

from reportlab.platypus.tableofcontents import TableOfContents

class _TocDocTemplate(SimpleDocTemplate):
    """SimpleDocTemplate that registers headings into a TableOfContents."""
    def afterFlowable(self, flowable):
        if isinstance(flowable,Paragraph):
            style=flowable.style.name if flowable.style else ''
            if style=='TOCHeading1':
                self.notify('TOCEntry',(0,flowable.getPlainText(),self.page))

def _make_toc():
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle(name='TOCHeading1',fontName=_F(True),fontSize=10.5,leading=17,textColor=_TXT_DARK)]
    toc.dotsMinLevel=0
    return toc

def _bench_target(b):
    """Format a benchmark target for PDF display."""
    try:
        t=b.get('target')
        if t is None: return 'N/A'
        if b.get('scale')=='0-100':
            return '%g'%t
        return ('%g'%t) if t>1.5 else ('%d%%'%round(t*100))
    except Exception:
        return 'N/A'

def build_report_pdf(results, narrative_only=False):
    if not results: results={}
    try:
        narrative_only = bool(results.pop('_narrative_only', narrative_only))
    except Exception:
        pass
    buf=io.BytesIO()
    styles=_make_styles()
    doc=_TocDocTemplate(buf,pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=18*mm,bottomMargin=32*mm,
                        title='Content Intelligence Report',author='Intent, Entity & Semantic Intelligence Platform',
                         subject='22-Module Content Analysis Report')
    # thread-safe: local width only (no globals)
    # Reportlab's default frame applies 6pt left + 6pt right padding, so the
    # usable width for flowables is doc.width - 12. Sizing tables to doc.width
    # made every table 12pt too wide and overflow the right margin.
    usable_width=doc.width - 12
    story=[]
    blueprint=results.get('blueprint') or {}
    module_results=results.get('module_results') or {}
    url_data=results.get('_url_data') or {}
    now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mode='URL Analysis' if url_data else 'Keyword / Manual Analysis'
    target=url_data.get('url') or results.get('entity') or results.get('seed') or 'N/A'
    brand=results.get('brand') or ''
    es=(blueprint.get('executive_summary') or {})
    exec_stats=(es.get('total_modules_executed') or len(module_results),es.get('critical_issues_count') or 0,es.get('high_priority_count') or 0,es.get('total_recommendations') or 0)

    # ---- Cover page (drawn via canvas; story starts on page 2) ----
    def _first_page(canvas,doc):
        _cover_page(canvas,doc,'',mode,target,brand,now,exec_stats)

    # ---- Table of Contents page (page 2: page 1 is the canvas-drawn cover) ----
    story.append(PageBreak())
    story.append(Paragraph('Contents',styles['tocc']))
    story.append(HRFlowable(width='100%',thickness=1.6,color=_BRAND,spaceBefore=2,spaceAfter=10))
    toc=_make_toc()
    story.append(toc)
    story.append(Spacer(1,16))
    meta=results.get('blueprint',{}).get('blueprint_metadata',{})
    _add_kv(story,styles,[
        ('Generated',now),('Mode',mode),('Target',target),('Brand',brand or 'N/A'),
        ('Locale',meta.get('target_locale','en-US')),('Entity',meta.get('target_entity','')),
        ('Query',meta.get('target_query','')),('Competitors Analyzed',results.get('analysis_metadata',{}).get('competitors_analyzed',0)),
        ('SERP Results Fetched',results.get('analysis_metadata',{}).get('serp_results_fetched',0)),
        ('Modules Completed',es.get('total_modules_executed') or len(module_results)),
    ],usable_width)
    story.append(PageBreak())

    # ---- 1. Executive Summary ----
    story.append(Paragraph('1. Executive Summary',styles['TOCHeading1']))
    story.append(HRFlowable(width='100%',thickness=0.8,color=_BRAND,spaceBefore=1,spaceAfter=8))
    stats=[('Modules Executed',es.get('total_modules_executed') or len(module_results),_BRAND),
           ('Critical Issues',es.get('critical_issues_count') or 0,_ERR_RED),
           ('High Priority',es.get('high_priority_count') or 0,_WARN_AMBER),
           ('Recommendations',es.get('total_recommendations') or 0,_OK_GREEN)]
    tw=usable_width/len(stats)
    tdata=[]
    row1=[];row2=[]
    for lbl,val,col in stats:
        row1.append(Paragraph(_esc_pdf(lbl),styles['statlbl']))
        row2.append(Paragraph('<font color="#ffffff"><b>%s</b></font>'%_esc_pdf(str(val)),styles['statval']))
    tdata=[row1,row2]
    t=Table(tdata,colWidths=[tw]*len(stats),hAlign='LEFT')
    cmds=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),
          ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
          ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]
    for i,(lbl,val,col) in enumerate(stats):
        cmds.append(('BACKGROUND',(i,1),(i,1),col))
        cmds.append(('BACKGROUND',(i,0),(i,0),HexColor('#f1f5f9')))
        cmds.append(('LINEBELOW',(i,0),(i,0),3,col))
    t.setStyle(TableStyle(cmds))
    story.append(t)
    story.append(Spacer(1,10))
    _section_banner(story,styles,'1','Executive Summary')
    _add_section(story,styles,'',es,width=usable_width)
    story.append(PageBreak())

    # ---- 2-6 blueprint sections ----
    secs=[('output_1_editorial_blueprint','2','Editorial & Writing Blueprint'),
          ('output_2_geo_optimization','3','GEO & AEO Optimization'),
          ('output_3_technical_payload','4','Technical Payload'),
          ('output_4_cdn_deployment','5','CDN & Edge Deployment'),
          ('output_5_sentinel_brief','6','Post-Publish Sentinel Brief')]
    for key,no,title in secs:
        sec=blueprint.get(key)
        story.append(Paragraph('%s. %s'%(no,title),styles['TOCHeading1']))
        story.append(HRFlowable(width='100%',thickness=0.8,color=_BRAND,spaceBefore=1,spaceAfter=8))
        _section_banner(story,styles,no,title)
        if sec:
            _add_content(story,sec,styles,width=usable_width)
        else:
            story.append(Paragraph('<i>No data produced for this section.</i>',styles['note']))
        story.append(PageBreak())

    # ---- 7. Module Results ----
    story.append(Paragraph('7. Module Results (M01 - M22)',styles['TOCHeading1']))
    story.append(HRFlowable(width='100%',thickness=0.8,color=_BRAND,spaceBefore=1,spaceAfter=8))
    _section_banner(story,styles,'7','Module Results (M01 - M22)')
    story.append(Spacer(1,6))
    first_module=True
    for i in range(1,23):
        k='M%02d'%i
        mr=module_results.get(k)
        if not mr: continue
        if first_module:
            first_module=False
        else:
            story.append(PageBreak())
        hdr=Table([[Paragraph('<font color="#ffffff">MODULE %d</font>'%i,ParagraphStyle('n',fontName=_F(True),fontSize=8,textColor=HexColor('#ffffff'))),
                    Paragraph('<font color="#ffffff">%s</font>'%_esc_pdf(_MODULE_NAMES.get(k,k)),ParagraphStyle('t2',fontName=_F(True),fontSize=12,leading=16,textColor=HexColor('#ffffff')))]],
                   colWidths=[usable_width*0.18,usable_width*0.82],hAlign='LEFT')
        hdr.setStyle(TableStyle([('BACKGROUND',(0,0),(0,0),_BRAND_DARK),
                                 ('BACKGROUND',(1,0),(1,0),_BRAND),
                                 ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                 ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                                 ('LEFTPADDING',(0,0),(0,0),0),('LEFTPADDING',(1,0),(1,0),10),
                                 ('RIGHTPADDING',(0,0),(-1,-1),10),
                                 ('BOX',(0,0),(-1,-1),0.5,_BRAND_DARK)]))
        story.append(hdr)
        story.append(Spacer(1,4))
        if isinstance(mr,dict) and mr.get('error'):
            story.append(Paragraph('<font color="#dc2626"><b>Error:</b> %s</font>'%_esc_pdf(mr['error']),styles['body']))
        else:
            _add_content(story,mr,styles,depth=0,width=usable_width)
        if isinstance(mr,dict):
            sb=mr.get('score_benchmarks') or []
            if sb:
                story.append(Paragraph('Score Benchmarks - what to aim for',styles['h3']))
                rows=[{'Score':b.get('key',''),'Your Value':b.get('value'),'Target':_bench_target(b),'Level':str(b.get('level','')).upper(),'Rankings':b.get('rankings',''),'AI Overview':b.get('ai_overview',''),'AI Citations':b.get('ai_citation','')} for b in sb[:12]]
                _add_table(story,rows,styles,usable_width,maxrows=12)
                story.append(Paragraph('Benchmarks are standard industry guidance (heuristic, unverified), not measured ranking guarantees.',styles['note']))
            pb=mr.get('recommendation_playbook') or {}
            if pb:
                story.append(Paragraph('Recommendations & Action Plan (after analysis)',styles['h3']))
                story.append(Paragraph('<b>What To Do</b>',styles['h4']))
                for w in (pb.get('what_to_do') or []):
                    story.append(Paragraph('&#8226; '+_txt(w),styles['body']))
                story.append(Paragraph('<b>When To Do It</b>',styles['h4']))
                for w in (pb.get('when_to_do') or []):
                    story.append(Paragraph('&#8226; '+_txt(w),styles['body']))
                tools=pb.get('tools_to_use') or []
                if tools:
                    story.append(Paragraph('<b>Tools To Use</b>',styles['h4']))
                    _add_table(story,[{'Tool':t.get('tool',''),'How To Use':t.get('use','')} for t in tools],styles,usable_width)
                ab=pb.get('ab_test_plan') or {}
                if ab:
                    story.append(Paragraph('<b>A/B Test Plan - how to verify it works</b>',styles['h4']))
                    _add_kv(story,styles,[
                        ('Hypothesis',ab.get('hypothesis','')),('Variant A',ab.get('variant_a','')),
                        ('Variant B',ab.get('variant_b','')),('Metrics',', '.join(ab.get('metrics',[]) or [])),
                        ('Duration (days)',ab.get('duration_days','')),('How To Judge',ab.get('check',''))],usable_width)
        if isinstance(mr,dict):
            lvs=mr.get('live_verified_statistics') or {}
            if lvs.get('statistics'):
                story.append(Paragraph('Live Verified Statistics (real, sourced)',styles['h3']))
                _add_table(story,[{'#':i+1,'Statistic':s.get('stat',''),'Source':s.get('source_title','') or s.get('source_url','')} for i,s in enumerate(lvs['statistics'][:10])],styles,usable_width)

    # ---- 8. Appendix (skipped in narrative-only slim mode) ----
    if narrative_only:
        story.append(Paragraph('8. Full Data Appendix (slim mode)',styles['TOCHeading1']))
        story.append(HRFlowable(width='100%',thickness=0.8,color=_BRAND,spaceBefore=1,spaceAfter=8))
        story.append(Paragraph('Slim narrative PDF: full JSON available via /api/download_json or the Raw JSON tab (downloadable artifact).',styles['body']))
        story.append(Spacer(1,6))
    else:
        story.append(Paragraph('8. Full Data Appendix',styles['TOCHeading1']))
        story.append(HRFlowable(width='100%',thickness=0.8,color=_BRAND,spaceBefore=1,spaceAfter=8))
        _section_banner(story,styles,'8','Full Data Appendix')
        story.append(Paragraph('Complete raw data used to generate this report (programmatic use). For large reports prefer /api/download_json.',styles['body']))
        story.append(Spacer(1,6))
        export={k:v for k,v in results.items() if k!='_url_data'}
        if url_data:
            export['_url_data']={k:v for k,v in url_data.items() if k not in ('raw_html','page_text')}
        try:
            raw=json.dumps(export,ensure_ascii=False,indent=1,default=str)
        except Exception:
            raw=str(export)
        if len(raw)>200000:
            raw=raw[:200000]+'\n... [truncated — download full JSON via /api/download_json]'
        _add_raw_json(story,styles,raw)
    doc.multiBuild(story,onFirstPage=_first_page,onLaterPages=_pdf_footer)
    buf.seek(0)
    return buf.read()

app=Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept, X-API-Key'
    response.headers['Access-Control-Max-Age'] = '3600'
    try:
        return _apply_security_headers(response)
    except Exception:
        return response

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response

def web_search(query,num=5):
    """Real SERP retrieval (DuckDuckGo HTML). Returns list of result dicts."""
    res=_real_web_search(query,num)
    return res.get("results",[])

@app.route('/')
def index():
    return Response(INDEX_HTML,mimetype='text/html',headers={'Cache-Control':'public, max-age=60'})

@app.route('/api/progress/<analysis_id>',methods=['GET','OPTIONS'])
def api_progress(analysis_id):
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    rec=_PROGRESS_STORE.get(analysis_id)
    if not rec:
        try:
            from intent_entity_platform.utils import persistence as _pstg
            rec = _pstg.progress_get(analysis_id)
        except Exception:
            rec = None
    if not rec:
        return jsonify({'ok':False,'error':'Unknown or expired analysis session. Please run a new analysis.'}),404
    # Return a copy so callers can't mutate the live store
    return jsonify({
        'ok':True,
        'analysis_id':analysis_id,
        'phase':rec.get('phase',''),
        'phase_label':rec.get('phase_label',''),
        'current_module':rec.get('current_module'),
        'current_module_name':rec.get('current_module_name',''),
        'module_status':dict(rec.get('module_status',{})),
        'completed_modules':list(rec.get('completed_modules',[])),
        'errors':list(rec.get('errors',[])),
        'percent':rec.get('percent',0),
        'done':rec.get('done',False),
        'started_at':rec.get('started_at'),
        'updated_at':rec.get('updated_at'),
    })

@app.route('/api/analyze',methods=['POST','OPTIONS'])
def api_analyze():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "analyze", 20, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    try:
        data=request.get_json(silent=True)
        valid, vmsg = validate_json_dict(data)
        if not valid:
            return jsonify({"error": vmsg}),400
        analysis_id=str(data.get('analysis_id') or ('an_%06d' % secrets.randbelow(10**6)))
        progress=_make_progress_recorder(analysis_id)
        fw=InputFramework()
        fw.seed=SeedKeywordInput(
            seed_phrase=str(data.get('seed',''))[:200],
            primary_entity=str(data.get('entity',''))[:200],
            target_locale=data.get('locale','en-US'),
            target_device=data.get('device','desktop'),
            secondary_keywords=[k.strip()[:80] for k in str(data.get('secondary',''))[:1000].split(',') if k.strip()][:20],
        )
        fw.brand=BrandConstraints(
            brand_name=str(data.get('brand','Default'))[:120],
            voice_profile=data.get('voice','authoritative'),
            do_not_say_terms=[t.strip()[:80] for t in str(data.get('blacklist',''))[:1000].split(',') if t.strip()][:30],
        )
        fw.audience=AudienceProfile(
            funnel_stage=data.get('funnel','middle'),
            knowledge_floor=data.get('knowledge','intermediate'),
        )
        fw.technical=TechnicalCredentials(render_mode='ssr',js_framework='',cdn_provider='')
        fw.seed.brand_website=str(data.get('website',''))[:2048]
        if fw.seed.brand_website:
            allowed, reason = is_url_allowed(fw.seed.brand_website)
            if not allowed:
                return jsonify({"error": f"Brand website blocked: {reason}"}),400
        sme=str(data.get('sme',''))[:8000]
        if sme:
            for n in sme.split('|')[:10]:
                n=n.strip()[:2000]
                if n: fw.first_party.sme_assets.append(SMEAsset(content=n,expert_name="SME",expert_title="Expert"))
        errs=fw.validate_all()
        if errs: return jsonify({"error":errs}),400
        engine=PlatformEngine()
        results=engine.run_analysis(fw, progress_callback=progress)
        _mark_progress_done(analysis_id, results.get('errors',{}))
        results['analysis_id']=analysis_id
        results['server_version']=APP_VERSION
        try:
            from intent_entity_platform.utils import persistence as _psth
            _key = str(data.get('entity') or data.get('seed') or '')[:240].lower() or 'manual'
            _psth.history_add("tracker_snapshot", _key, {
                "analysis_id": analysis_id,
                "modules": len((results.get('module_results') or {})),
                "errors": len((results.get('errors') or {}))})
        except Exception:
            pass
        return jsonify(results)
    except Exception as e:
        if 'analysis_id' in locals():
            _mark_progress_done(analysis_id, {'server':str(e)[:300]})
        return _safe_error("Analysis failed", e, 500)

@app.route('/api/analyze-url',methods=['POST','OPTIONS'])
def api_analyze_url():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "analyze-url", 20, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    try:
        data=request.get_json(silent=True)
        valid, vmsg = validate_json_dict(data)
        if not valid:
            return jsonify({"error": vmsg}),400
        url=str(data.get('url',''))[:2048]
        brand=str(data.get('brand',''))[:120]
        if not url: return jsonify({"error":"URL is required"}),400
        allowed, reason = is_url_allowed(url)
        if not allowed:
            return jsonify({"error": f"URL blocked by SSRF guard: {reason}"}),400
        analysis_id=str(data.get('analysis_id') or ('url_%06d' % secrets.randbelow(10**6)))
        progress=_make_progress_recorder(analysis_id)
        # Deduplicated parser: single shared extractor (web_data.extract_page).
        fetched = safe_fetch(url, timeout=15, max_bytes=2000000)
        if not fetched.get("ok"):
            return jsonify({"error": f"Failed to fetch URL: {fetched.get('error','unknown')}"}),400
        html_content = fetched.get("html", "")
        meta = _extract_page_shared(html_content, url)
        page_text = meta.get("page_text", "") or ""
        if len(page_text)<100:
            page_text=page_text+' (Minimal content extracted from URL. Analysis based on available text.)'
        seed_words=(meta.get("title","") or "").split()[:5] if meta.get("title") else page_text.split()[:5]
        seed_phrase=' '.join(seed_words)[:200]
        entity=(meta.get("h1") or "") if meta.get("h1") else (meta.get("title") or 'the content')
        fw=InputFramework()
        fw.seed=SeedKeywordInput(
            seed_phrase=seed_phrase,
            primary_entity=str(entity)[:200],
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
        _links = meta.get("links", []) or []
        _link_strs = []
        for l in _links[:30]:
            if isinstance(l, dict):
                _link_strs.append((l.get("href") or "")[:200])
            elif isinstance(l, str):
                _link_strs.append(l[:200])
        fw._url_data={
            'url': url,
            'title': str(meta.get("title",""))[:300],
            'meta_description': str(meta.get("meta_description",""))[:500],
            'meta_keywords': str(meta.get("meta_keywords",""))[:300],
            'h1': str(meta.get("h1",""))[:300],
            'h2s': [str(x)[:200] for x in (meta.get("h2s") or [])[:20]],
            'word_count': meta.get("word_count", 0),
            'link_count': meta.get("link_count", 0),
            'image_count': meta.get("image_count", 0),
            'images': meta.get("images", [])[:20],
            'links': [x for x in _link_strs if x],
            'has_schema': bool(meta.get("has_schema")),
            'page_text': page_text[:5000],
            'raw_html': html_content[:200000],
            'fetched_status': fetched.get("status", 200),
            'fetched_final_url': (fetched.get("final_url") or url)[:500],
        }
        results=engine.run_analysis(fw, progress_callback=progress)
        _mark_progress_done(analysis_id, results.get('errors',{}))
        results['_url_mode']=True
        results['_url_data']=fw._url_data
        results['analysis_id']=analysis_id
        results['server_version']=APP_VERSION
        return jsonify(results)
    except Exception as e:
        if 'analysis_id' in locals():
            _mark_progress_done(analysis_id, {'server':str(e)[:300]})
        return _safe_error("URL analysis failed", e, 500)
@app.route('/api/send_otp',methods=['POST','OPTIONS'])
def api_send_otp():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "send_otp", 5, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
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
    otp='%06d' % secrets.randbelow(10**6)
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
        return _safe_error("Could not send the OTP email", e, 500)
    return jsonify({'ok':True,'message':'OTP sent to %s'%email})

@app.route('/api/verify_and_send_report',methods=['POST','OPTIONS'])
def api_verify_and_send_report():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
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
    if isinstance(results, dict) and len(json.dumps(results, default=str)) > 5_000_000:
        return jsonify({"error": "Report payload too large (max ~5MB)"}), 413
    try:
        pdf=build_report_pdf(results)
    except Exception as e:
        return _safe_error("Could not generate the PDF report", e, 500)
    ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    fname='content_intelligence_report_%s.pdf'%ts
    html=("<div style='font-family:Arial,sans-serif;padding:24px;background:#f5f7ff;border-radius:12px'>"
          "<h2 style='color:#1e1b4b'>Your Content Intelligence Report</h2>"
          "<p>Please find attached the full 22-module analysis report (PDF) you requested.</p>"
          "<p style='color:#6b7280;font-size:12px'>Generated by the Intent, Entity &amp; Semantic Intelligence Platform.</p></div>")
    try:
        _send_email(email,'Your Content Intelligence Report - %s'%ts,html,fname,pdf)
    except Exception as e:
        return _safe_error("Could not email the report", e, 500)
    return jsonify({'ok':True,'message':'Report sent to %s'%email})

@app.route('/api/download_pdf',methods=['POST','OPTIONS'])
def api_download_pdf():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "download_pdf", 10, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    data=request.get_json(silent=True) or {}
    results=data.get('report') or {}
    if isinstance(results, dict) and len(json.dumps(results, default=str)) > 5_000_000:
        return jsonify({"error": "Report payload too large (max ~5MB)"}), 413
    slim = bool(data.get('narrative_only') or request.args.get('narrative_only') == '1')
    try:
        pdf=build_report_pdf(results, narrative_only=slim)
    except Exception as e:
        return _safe_error("Could not generate the PDF report", e, 500)
    ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    fname='content_intelligence_report_%s.pdf'%ts
    return Response(pdf,mimetype='application/pdf',headers={'Content-Disposition':'attachment; filename=%s'%fname})

# ---------------------------------------------------------------------------
# Enterprise P0/P1 APIs: content score, brief, GSC quick wins, share links
# ---------------------------------------------------------------------------
_REPORT_STORE = {}
_REPORT_LOCK = threading.Lock()

@app.route('/api/score', methods=['POST', 'OPTIONS'])
def api_score():
    """Dual SEO+GEO content score (heuristic TF-IDF; no ML deps)."""
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "score", 60, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    data = request.get_json(silent=True) or {}
    draft = str(data.get("draft", ""))[:100000]
    competitors = data.get("competitor_texts", []) or []
    competitors = [str(c)[:50000] for c in competitors[:5]]
    terms = [str(t)[:80] for t in (data.get("must_include_terms", []) or [])[:60]]
    targets = data.get("targets", {}) or {}
    if not draft.strip():
        return jsonify({"error": "draft text is required"}), 400
    try:
        return jsonify(score_content(draft, competitors, terms, targets))
    except Exception as e:
        return _safe_error("Scoring failed", e, 500)

@app.route('/api/brief', methods=['POST', 'OPTIONS'])
def api_brief():
    """SERP-driven brief generator from a prior analysis result."""
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "brief", 60, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    data = request.get_json(silent=True) or {}
    seed = str(data.get("seed", ""))[:200]
    entity = str(data.get("entity", ""))[:200]
    mr = data.get("module_results", {}) or {}
    comp = data.get("competitive_intelligence", {}) or {}
    serp_results = comp.get("raw_serp_results", []) or (mr.get("M01", {}) or {}).get("serp_results", [])
    try:
        brief = generate_brief(seed, entity, serp_results,
                               comp.get("content_headings", {}),
                               comp.get("content_gaps", {}),
                               comp.get("competitor_entities", {}),
                               comp.get("serp_features", {}),
                               int(data.get("word_target", 0) or 0))
        return jsonify(brief)
    except Exception as e:
        return _safe_error("Brief generation failed", e, 500)

@app.route('/api/gsc_quick_wins', methods=['POST', 'OPTIONS'])
def api_gsc_quick_wins():
    """CSV-upload fallback for GSC Performance data -> striking distance/decay/cannibalization."""
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "gsc", 30, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    try:
        csv_text = ""
        if "file" in request.files:
            csv_text = request.files["file"].read(5_000_000).decode("utf-8", errors="ignore")
        else:
            data = request.get_json(silent=True) or {}
            csv_text = str(data.get("csv", ""))[:5_000_000]
        if not csv_text.strip():
            return jsonify({"error": "Upload a GSC Performance CSV (query,page,clicks,impressions,ctr,position)"}), 400
        rows = parse_gsc_csv(csv_text)
        if not rows:
            return jsonify({"error": "No parseable rows. Expected header: query,page,clicks,impressions,ctr,position"}), 400
        return jsonify(quick_wins(rows))
    except Exception as e:
        return _safe_error("GSC analysis failed", e, 500)

@app.route('/api/share', methods=['POST', 'OPTIONS'])
def api_share():
    """Versioned share-link store (replaces OTP-email delivery for enterprise sharing)."""
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    data = request.get_json(silent=True) or {}
    report = data.get("report") or {}
    if not isinstance(report, dict) or not report:
        return jsonify({"error": "report payload required"}), 400
    sid = secrets.token_urlsafe(12)
    with _REPORT_LOCK:
        _REPORT_STORE[sid] = {"report": report, "created": time.time(),
                              "label": str(data.get("label", ""))[:120]}
        if len(_REPORT_STORE) > 200:
            oldest = sorted(_REPORT_STORE.items(), key=lambda kv: kv[1]["created"])[:50]
            for k, _ in oldest:
                _REPORT_STORE.pop(k, None)
    try:
        from intent_entity_platform.utils import persistence as _pst2
        _pst2.share_put(sid, report, str(data.get("label", ""))[:120])
    except Exception:
        pass
    return jsonify({"ok": True, "share_id": sid, "share_url": f"/api/share/{sid}"})

@app.route('/api/share/<sid>', methods=['GET'])
def api_share_get(sid):
    rec = _REPORT_STORE.get(str(sid)[:32])
    if not rec:
        try:
            from intent_entity_platform.utils import persistence as _pst3
            srec = _pst3.share_get(str(sid)[:32])
            if srec:
                return jsonify({"ok": True, "label": srec.get("label", ""),
                                "report": srec.get("report")})
        except Exception:
            pass
        return jsonify({"error": "Unknown or expired share link"}), 404
    return jsonify({"ok": True, "label": rec.get("label", ""), "report": rec.get("report")})

@app.route('/api/health', methods=['GET'])
def api_health():
    import intent_entity_platform as _pkg
    return jsonify({"ok": True, "version": APP_VERSION, "debug": APP_DEBUG,
                    "serp_provider": os.environ.get("SERP_PROVIDER", "ddg_fallback"),
                    "modules": 22,
                    "time": datetime.datetime.now().isoformat()})

# ---------------------------------------------------------------------------
# v3.0.0-enterprise routes: persistence-backed shares, slim PDF/JSON, P0/P1 APIs
# In-memory _OTP/_PROGRESS/_REPORT stores kept for backward compat; every
# write is mirrored to SQLite (utils.persistence) so multi-worker prod works.
# ---------------------------------------------------------------------------
try:
    from intent_entity_platform.utils import persistence as _pst
    from intent_entity_platform.utils import auth as _auth
    from intent_entity_platform.utils.ai_crawler_audit import audit_ai_crawlers
    from intent_entity_platform.utils.pagespeed import full_vitals
    from intent_entity_platform.utils.gsc_oauth import oauth_status as _gsc_status
    from intent_entity_platform.utils.extractability import validate_extractability
    from intent_entity_platform.utils.offsite_authority import authority_graph
    from intent_entity_platform.utils.multimodal_video import audit_multimodal
    from intent_entity_platform.utils.action_center import (
        build_tasks as _build_tasks, to_csv as _tasks_csv,
        to_issue_tracker as _tasks_tracker, ga4_attribution_stub as _ga4)
    from intent_entity_platform.modules.module_22_llm_citation import LLMCitationTester
    _ENT_OK = True
except Exception as _ent_e:
    _ENT_OK = False
    _ENT_ERR = str(_ent_e)[:200]

def _ent_guard():
    if not _ENT_OK:
        return jsonify({"error": "Enterprise extensions failed to load"}), 500
    return None

@app.route('/api/download_json', methods=['POST', 'OPTIONS'])
def api_download_json():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    data = request.get_json(silent=True) or {}
    report = data.get('report') or {}
    if not isinstance(report, dict) or not report:
        return jsonify({"error": "report payload required"}), 400
    slim = dict(report)
    ud = slim.get('_url_data')
    if isinstance(ud, dict):
        slim['_url_data'] = {k: v for k, v in ud.items() if k not in ('raw_html', 'page_text')}
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return Response(json.dumps(slim, ensure_ascii=False, indent=1, default=str),
                    mimetype='application/json',
                    headers={'Content-Disposition': 'attachment; filename=content_report_%s.json' % ts})

@app.route('/api/gsc_oauth_status', methods=['GET'])
def api_gsc_oauth_status():
    err = _ent_guard()
    if err: return err
    return jsonify({"ok": True, **_gsc_status()})

@app.route('/api/pagespeed', methods=['POST', 'OPTIONS'])
def api_pagespeed():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "pagespeed", 30, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    data = request.get_json(silent=True) or {}
    url = str(data.get('url', ''))[:2048]
    if not url:
        return jsonify({"error": "url required"}), 400
    allowed, reason = is_url_allowed(url)
    if not allowed:
        return jsonify({"error": "URL blocked by SSRF policy: %s" % reason}), 400
    try:
        return jsonify({"ok": True, **full_vitals(url, str(data.get('strategy', 'mobile'))[:10])})
    except Exception as e:
        return _safe_error("PageSpeed lookup failed", e, 500)

@app.route('/api/ai_crawl_audit', methods=['POST', 'OPTIONS'])
def api_ai_crawl_audit():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, **audit_ai_crawlers(
            str(data.get('url', ''))[:2048],
            str(data.get('robots_text', ''))[:100000],
            str(data.get('html', ''))[:500000])})
    except Exception as e:
        return _safe_error("AI-crawler audit failed", e, 500)

@app.route('/api/extractability', methods=['POST', 'OPTIONS'])
def api_extractability():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, **validate_extractability(
            str(data.get('page_text', ''))[:200000],
            str(data.get('h1', ''))[:300],
            [str(h)[:300] for h in (data.get('h2s') or [])][:40],
            str(data.get('html', ''))[:500000],
            [str(s)[:60] for s in (data.get('schema_types') or [])][:20])})
    except Exception as e:
        return _safe_error("Extractability scoring failed", e, 500)

@app.route('/api/offsite_authority', methods=['POST', 'OPTIONS'])
def api_offsite_authority():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "offsite", 30, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, **authority_graph(
            str(data.get('entity', ''))[:200],
            str(data.get('seed', ''))[:200],
            str(data.get('brand', ''))[:200])})
    except Exception as e:
        return _safe_error("Off-site authority scan failed", e, 500)

@app.route('/api/multimodal_audit', methods=['POST', 'OPTIONS'])
def api_multimodal_audit():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, **audit_multimodal(
            str(data.get('html', ''))[:500000],
            str(data.get('page_text', ''))[:200000],
            int(data.get('image_count', 0) or 0),
            str(data.get('url', ''))[:2048])})
    except Exception as e:
        return _safe_error("Multimodal audit failed", e, 500)

@app.route('/api/llm_test', methods=['POST', 'OPTIONS'])
def api_llm_test():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    ok_rl, msg_rl = check_rate_limit(_client_ip(), "llm_test", 10, 3600)
    if not ok_rl:
        return jsonify({"error": msg_rl}), 429
    data = request.get_json(silent=True) or {}
    entity = str(data.get('entity') or data.get('primary_entity') or '')[:200]
    if not entity and not str(data.get('seed', '')):
        return jsonify({"error": "entity (or seed) required"}), 400
    try:
        t = LLMCitationTester()
        out = t.analyze({"primary_entity": entity,
                          "seed_phrase": str(data.get('seed', ''))[:200],
                          "brand": str(data.get('brand', ''))[:200],
                          "funnel_stage": str(data.get('funnel', ''))[:40],
                          "knowledge_floor": str(data.get('knowledge', ''))[:40],
                          "m22_prompts": int(data.get('prompts', 10) or 10)})
        return jsonify({"ok": True, **out})
    except Exception as e:
        return _safe_error("LLM citation test failed", e, 500)

@app.route('/api/llm_history', methods=['GET'])
def api_llm_history():
    err = _ent_guard()
    if err: return err
    key = str(request.args.get('key', ''))[:240].lower()
    if not key:
        return jsonify({"error": "key (entity) required"}), 400
    rows = _pst.history_list("m22", key, int(request.args.get('limit', 90) or 90))
    sov = [r.get('share_of_voice_pct') for r in rows if isinstance(r.get('share_of_voice_pct'), (int, float))]
    return jsonify({"ok": True, "key": key, "runs": len(rows), "history": rows,
                    "sov_trend": sov,
                    "sov_delta": round(sov[-1] - sov[0], 1) if len(sov) >= 2 else 0.0,
                    "method_note": "SQLite-persisted M22 runs (live vs honest_mock labeled per run)."})

@app.route('/api/tracker_history', methods=['GET'])
def api_tracker_history():
    err = _ent_guard()
    if err: return err
    key = str(request.args.get('key', ''))[:240].lower()
    if not key:
        return jsonify({"error": "key (entity) required"}), 400
    rows = _pst.history_list("tracker_snapshot", key, int(request.args.get('limit', 90) or 90))
    return jsonify({"ok": True, "key": key, "snapshots": len(rows), "history": rows})

@app.route('/api/tracker_record', methods=['POST', 'OPTIONS'])
def api_tracker_record():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    data = request.get_json(silent=True) or {}
    key = str(data.get('entity') or data.get('key') or '')[:240].lower()
    if not key:
        return jsonify({"error": "entity required"}), 400
    rid = _pst.history_add("tracker_snapshot", key, {
        "entity": data.get('entity'), "snapshot": data.get('snapshot', {}),
        "source": "api_tracker_record"})
    return jsonify({"ok": True, "id": rid})

@app.route('/api/action_center', methods=['POST', 'OPTIONS'])
def api_action_center():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    data = request.get_json(silent=True) or {}
    mr = data.get('module_results') or (data.get('report') or {}).get('module_results') or {}
    if not isinstance(mr, dict) or not mr:
        return jsonify({"error": "module_results (or report.module_results) required"}), 400
    fmt = str(data.get('format', 'json'))[:10].lower()
    tasks = _build_tasks(mr, int(data.get('max_tasks', 40) or 40))
    if fmt == 'csv':
        return Response(_tasks_csv(tasks), mimetype='text/csv',
                        headers={'Content-Disposition': 'attachment; filename=action_center.csv'})
    if fmt in ('jira', 'linear'):
        return jsonify({"ok": True, "system": fmt, "count": len(tasks),
                        "issues": _tasks_tracker(tasks, fmt), "ga4": _ga4()})
    return jsonify({"ok": True, "count": len(tasks), "tasks": tasks, "ga4": _ga4()})

@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    err = _ent_guard()
    if err: return err
    return jsonify({"ok": True, **_auth.auth_status()})

@app.route('/api/serp_status', methods=['GET'])
def api_serp_status():
    provider = os.environ.get("SERP_PROVIDER", "ddg_fallback")
    has_serper = bool(os.environ.get("SERPER_API_KEY"))
    has_dfd = bool(os.environ.get("DATAFORSEO_LOGIN") and os.environ.get("DATAFORSEO_PASSWORD"))
    effective = provider
    if provider == "serper" and not has_serper:
        effective = "ddg_fallback (SERPER_API_KEY missing)"
    if provider == "dataforseo" and not has_dfd:
        effective = "ddg_fallback (DATAFORSEO creds missing)"
    return jsonify({"ok": True, "configured": provider, "effective": effective,
                    "serper_key": "SET" if has_serper else "MISSING",
                    "dataforseo": "SET" if has_dfd else "MISSING",
                    "cost_guard": "$ per 1k queries is provider-billed; DDG fallback is free but brittle HTML scrape — Serper first-class when key set.",
                    "cache": "SQLite 30-day (serp_cache.sqlite3 + platform.sqlite3 history)"})

@app.route('/api/docs', methods=['GET'])
def api_docs():
    try:
        spec = open(Path(__file__).parent / "openapi.yaml", encoding="utf-8").read()
    except Exception:
        spec = "openapi: 3.0.3\ninfo:\n  title: Intent Entity Platform API\n  version: 3.0.0-enterprise\n"
    routes = sorted([str(r) for r in app.url_map.iter_rules()])
    return jsonify({"ok": True, "version": APP_VERSION, "routes": routes,
                    "openapi_path": "openapi.yaml", "openapi": spec[:20000]})

@app.route('/api/mcp', methods=['POST', 'OPTIONS'])
def api_mcp():
    if request.method == 'OPTIONS':
        return jsonify({'ok': True})
    err = _ent_guard()
    if err: return err
    data = request.get_json(silent=True) or {}
    method = str(data.get('method', '')) or str(data.get('jsonrpc_method', ''))
    if method in ('tools/list', 'list_tools', ''):
        return jsonify({"ok": True, "tools": [
            {"name": "analyze", "description": "Run 22-module analysis", "input": {"seed": "string", "entity": "string"}},
            {"name": "score", "description": "Dual SEO+GEO score", "input": {"draft": "string"}},
            {"name": "brief", "description": "SERP-driven brief", "input": {"seed": "string", "entity": "string"}},
            {"name": "llm_test", "description": "M22 citation test", "input": {"entity": "string"}},
            {"name": "ai_crawl_audit", "description": "llms.txt + AI-bot audit", "input": {"url": "string"}},
            {"name": "action_center", "description": "Tasks from results", "input": {"module_results": "object"}},
        ]})
    if method == 'tools/call':
        name = str((data.get('params') or {}).get('name') or data.get('tool') or '')
        args = (data.get('params') or {}).get('arguments') or data.get('args') or {}
        if name == 'ai_crawl_audit':
            return jsonify({"ok": True, "result": audit_ai_crawlers(str(args.get('url', '')))})
        if name == 'llm_test':
            t = LLMCitationTester()
            return jsonify({"ok": True, "result": t.analyze(
                {"primary_entity": str(args.get('entity', ''))})})
        return jsonify({"error": "Unknown tool: %s" % name[:80]}), 400
    return jsonify({"error": "Unsupported MCP method. Use tools/list or tools/call."}), 400

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
.card .toggle-h{display:flex;justify-content:space-between;align-items:center;cursor:pointer;user-select:none}
.card .toggle-h .caret{transition:transform .2s;font-size:.8rem;color:var(--txt3)}
.card.closed .toggle-h .caret{transform:rotate(-90deg)}
.card .toggle-body{transition:max-height .3s ease,opacity .3s ease;overflow:hidden}
.card.closed .toggle-body{max-height:0!important;opacity:0;padding-top:0;padding-bottom:0}
.clickable-block{cursor:pointer;transition:border-color .2s}
.clickable-block:hover{border-color:var(--pri)!important}
.clickable-block .cb-hint{display:none;font-size:.72rem;color:var(--txt3);font-style:italic}
.clickable-block:hover .cb-hint{display:inline}
.mod-head{display:flex;align-items:center;gap:8px;cursor:pointer;user-select:none;padding:14px 16px;border-radius:14px 14px 0 0;margin:-22px -22px 14px;background:linear-gradient(135deg,rgba(124,92,252,.14),rgba(34,211,238,.08));border-bottom:1px solid var(--bd);transition:background .2s}
.mod-head:hover{background:linear-gradient(135deg,rgba(124,92,252,.24),rgba(34,211,238,.12))}
.mod-head .mnum{font-size:.72rem;font-weight:800;color:var(--pri);letter-spacing:1px}
.mod-head .mname{font-weight:700;color:var(--txt)}
.mod-head .mcaret{margin-left:auto;font-size:.8rem;color:var(--txt3);transition:transform .2s}
.mod-card.closed .mod-head .mcaret{transform:rotate(-90deg)}
.mod-card .mod-body{transition:max-height .35s ease,opacity .3s ease;overflow:hidden}
.mod-card.closed .mod-body{max-height:0!important;opacity:0;padding:0}
.detail-modal{position:fixed;inset:0;background:rgba(2,6,23,.72);z-index:2000;display:flex;align-items:center;justify-content:center;padding:30px;animation:fadeIn .2s ease}
.detail-modal .dm-box{background:var(--s1);border:1px solid var(--bd2);border-radius:14px;max-width:860px;width:100%;max-height:86vh;overflow:auto;box-shadow:0 20px 60px rgba(0,0,0,.5);padding:22px}
.detail-modal .dm-close{float:right;background:var(--s3);border:1px solid var(--bd2);color:var(--txt);border-radius:8px;padding:6px 14px;cursor:pointer;font-weight:700}
.detail-modal .dm-title{font-size:1.1rem;font-weight:700;color:var(--acc2);margin-bottom:12px;padding-right:40px}
.kv-click{cursor:pointer;position:relative}
.kv-click:hover{background:var(--s3)!important}
.tbl-click td{cursor:pointer}
.tbl-click tr:hover td{background:var(--s3)!important}
.dm-click{cursor:pointer}
.dm-click:hover{outline:1px dashed var(--pri);outline-offset:1px;border-radius:3px}
tr.dm-click:hover td{background:var(--s3)!important}
.sub.dm-click:hover{border-color:var(--pri)}
.chip.dm-click:hover{border-color:var(--pri);background:var(--s2)}
.section-click{cursor:pointer}
.section-click:hover{color:var(--pri)!important}
.section-click .cb-hint{display:none;font-size:.7rem;color:var(--txt3);font-weight:400;font-style:italic}
.section-click:hover .cb-hint{display:inline}
.bench-excellent{color:var(--grn);font-weight:700}
.bench-good{color:var(--acc2);font-weight:700}
.bench-needs{color:var(--yel);font-weight:700}
.bench-fail{color:var(--red);font-weight:700}
.bench-target{font-size:.72rem;color:var(--txt3)}
.pop{position:absolute;background:var(--s3);border:1px solid var(--bd2);border-radius:8px;padding:10px 12px;font-size:.78rem;color:var(--txt2);box-shadow:0 8px 24px rgba(0,0,0,.4);z-index:3000;max-width:320px;pointer-events:none;white-space:pre-wrap;word-break:break-word}
</style>
</head>
<body>
<div class="app">
<div class="topbar">
<div class="brand">
<h1>Intent, Entity & Semantic Intelligence Platform</h1>
<div class="subtitle">22-Module Analysis for Search & Generative AI Optimization</div>
</div>
<div class="sep"></div>
<div class="status" id="topStatus">Ready - 22 modules loaded</div>
<div class="right">
<button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode"><div class="knob"></div></button>
</div>
</div>
<div class="sidebar">
<div class="mode-divider">&#9679; Analysis Mode</div>
<details class="url-section" open>
<summary>&#128279; Analyze Published URL</summary>
<p style="font-size:.82rem;color:var(--txt3);margin-bottom:10px">Paste a published blog/article URL. The tool will fetch and analyze its content across all 22 modules.</p>
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
<button type="submit" class="btn btn-go" id="runBtn">Run 22-Module Analysis</button>
</form>
<div id="statusBox" style="margin-top:12px"></div>
</div>
<div class="main" id="mainArea">
<div class="info-page" id="infoArea">
<h2>Welcome to the Intent, Entity & Semantic Intelligence Platform</h2>
<p>A comprehensive 22-module analysis engine that evaluates your content for both traditional search engines and generative AI engines (ChatGPT, Gemini, Perplexity, Claude). Every module runs on <strong>real, live, verified data</strong> - live SERP results, Wikidata entities, Wayback Machine archives, live competitor page analysis, HTTP/header inspection, structured-data validation, live LLM citation testing (M22 share-of-voice), and verified statistics pulled from the web. Every finding is tied to an actual source. No fabricated numbers.</p>
<h3>Why This Tool Exists</h3>
<p>Modern SEO requires optimizing for two audiences: traditional search engines (Google, Bing) and generative AI engines (ChatGPT, Gemini, Perplexity). Most tools only address one. This platform analyzes your content across 22 specialized dimensions to ensure maximum visibility in both ecosystems - and tells you exactly what score to hit to win rankings, AI Overview extraction, and AI citations.</p>
<h3>What This Tool Does</h3>
<p>Runs 22 specialized analysis modules covering SERP analysis, GEO/AEO simulation, semantic structuring, E-E-A-T profiling, content decay detection, CDN edge preview, live LLM citation testing, and more. Each module outputs three layers:</p>
<ol class="steps">
<li><strong>Full Analysis</strong> - every score, finding, live statistic, and competitor benchmark, color-coded (green/amber/red) against its target.</li>
<li><strong>Score Benchmarks</strong> - the exact target/good/excellent thresholds for each score, with what each level means for rankings, AI Overviews, and AI citations.</li>
<li><strong>Recommendations & Action Plan</strong> - what to do, when to do it, which tools to use, and a ready-made A/B test plan to prove the change works.</li>
</ol>
<h3>Modules Overview</h3>
<div class="feature-grid">
<div class="feature-card" onclick="showModuleInfo('M01')"><h4>M01: SERP & Knowledge Graph</h4><p>Analyze SERP features, entity graphs, and Knowledge Panel opportunities. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M02')"><h4>M02: GEO & AEO Simulator</h4><p>Simulate Generative Engine and Answer Engine optimization strategies. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M03')"><h4>M03: Semantic Structure</h4><p>Validate schema markup, heading hierarchy, semantic HTML, plus 40–60-word answer-block extractability. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M04')"><h4>M04: E-E-A-T Gap Profiler</h4><p>Profile Experience, Expertise, Authoritativeness, and Trustworthiness gaps. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M05')"><h4>M05: Internal Link & Cannibalization</h4><p>Detect keyword cannibalization and optimize internal link architecture. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M06')"><h4>M06: Fluff & Cliche Decoder</h4><p>Identify filler content, cliches, and non-original phrases. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M07')"><h4>M07: Citation & Source Verifier</h4><p>Verify citation accuracy and source credibility for E-E-A-T signals. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M08')"><h4>M08: Multimodal Asset Blueprint</h4><p>Plan images, videos, infographics, and interactive assets — with video/transcript and WebP/AVIF audit. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M09')"><h4>M09: GEO Tracker</h4><p>Track GEO performance with live snapshots, longitudinal history, and M22 citation share-of-voice. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M10')"><h4>M10: CSR Simulator</h4><p>Simulate Client-Side Rendering impact on search engine indexing. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M11')"><h4>M11: RAG Tester</h4><p>Test content for Retrieval-Augmented Generation compatibility. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M12')"><h4>M12: Brand Compliance Engine</h4><p>Enforce brand voice, terminology, and style guidelines. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M13')"><h4>M13: Schema Payload Generator</h4><p>Generate complete JSON-LD schema payloads for rich results. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M14')"><h4>M14: Intent & Bounce Predictor</h4><p>Predict bounce risk and align content with user intent signals. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M15')"><h4>M15: Content Decay Engine</h4><p>Detect content freshness decay and generate refresh briefs. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M16')"><h4>M16: CDN Edge Previewer</h4><p>Preview edge-injected schema, headers, and pre-rendered HTML. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M17')"><h4>M17: A/B Testing Engine</h4><p>Design statistical A/B tests for content experiments. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M18')"><h4>M18: Indexing Sentinel</h4><p>Monitor indexing status, AI-crawler access (llms.txt + 9-bot audit), and crawl budget health. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M19')"><h4>M19: Localization Sync</h4><p>Manage hreflang, localized schema, and entity mapping. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M20')"><h4>M20: Digital PR Engine</h4><p>Plan PR outreach plus off-site authority: Wikipedia gap, Reddit/YouTube mentions, tier-1 likelihood. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M21')"><h4>M21: DOM Inspector</h4><p>Analyze DOM structure, layout shifts, and performance impact. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
<div class="feature-card" onclick="showModuleInfo('M22')"><h4>M22: Live LLM Citation Tester</h4><p>Prompt ChatGPT, Gemini, Perplexity &amp; Claude live — transcripts, citations, sentiment, share-of-voice. <b style="color:var(--acc2)">Click for details &rarr;</b></p></div>
</div>
<h3>What You Need</h3>
<ul>
<li><strong>Seed Keyword</strong> - Your primary target keyword or phrase</li>
<li><strong>Primary Entity</strong> - The main entity/topic your content covers</li>
<li><strong>Brand Name</strong> - Your brand for compliance and authority checks</li>
<li><strong>Audience Profile</strong> - Funnel stage, knowledge level, and voice preference</li>
<li><strong>Page URL (optional)</strong> - Paste a URL for real DOM, schema, header, link, and page-content analysis (recommended for maximum depth)</li>
</ul>
<h3>What You Get</h3>
<ul>
<li><strong>Executive Summary</strong> - High-level overview with critical issues and priorities</li>
<li><strong>Editorial Blueprint</strong> - Content outline, H1/H2/H3 structure, SME placements, answer blocks</li>
<li><strong>GEO Optimization</strong> - AI engine strategies, citation triggers, RAG chunking</li>
<li><strong>Technical Payload</strong> - JSON-LD schemas, validation, internal linking, DOM analysis</li>
<li><strong>CDN Deployment</strong> - Edge workers, headers, pre-render simulation</li>
<li><strong>Sentinel Brief</strong> - Monitoring config, alerts, A/B test design, rollback guards</li>
<li><strong>22 Module Results</strong> - Analysis first, then color-coded score benchmarks with targets, then a full action plan (what / when / tools / A/B test) for every module</li>
<li><strong>Live Verified Statistics</strong> - Real, sourced statistics extracted from live search, attached to every module</li>
<li><strong>Competitive Benchmarking</strong> - Your content measured against real, live competitors from actual SERP results</li>
<li><strong>Professional PDF Report</strong> - A polished, aligned report with cover page, table of contents, and all 22 modules — or a slim narrative-only PDF without the raw-JSON appendix</li>
<li><strong>Raw JSON</strong> - Complete data export for programmatic use, plus downloadable JSON artifact and versioned share links</li>
<li><strong>Action Center</strong> - Every recommendation as an assignable task (priority / effort / owner) with CSV, Jira, and Linear export</li>
</ul>
<p style="margin-top:24px;color:var(--pri2);font-weight:600;font-size:.95rem">Enter your seed keyword and entity in the sidebar, then click <strong>Run 22-Module Analysis</strong> to begin. Every result is generated from real-time research - click any number, row, or value for the full underlying detail.</p>
</div>
</div>
</div>

<script>
const MN={M01:"SERP & Knowledge Graph",M02:"GEO & AEO Simulator",M03:"Semantic Structure & Schema",M04:"E-E-A-T Gap Profiler",M05:"Internal Link & Cannibalization",M06:"Fluff & Cliche Decoder",M07:"Citation & Source Verifier",M08:"Multimodal Asset Blueprint",M09:"GEO Tracker",M10:"CSR Simulator",M11:"RAG Tester",M12:"Brand Compliance Engine",M13:"Schema Payload Generator",M14:"Intent & Bounce Predictor",M15:"Content Decay Engine",M16:"CDN Edge Previewer",M17:"A/B Testing Engine",M18:"Indexing Sentinel",M19:"Localization Sync",M20:"Digital PR Engine",M21:"DOM Inspector",M22:"Live LLM Citation Tester"};
const TABS=["exec","edit","geo","tech","cdn","snt","m01","m02","m03","m04","m05","m06","m07","m08","m09","m10","m11","m12","m13","m14","m15","m16","m17","m18","m19","m20","m21","m22","raw"];
const TAB_LABELS={exec:"Executive Summary",edit:"Editorial Blueprint",geo:"GEO Optimization",tech:"Technical Payload",cdn:"CDN Deployment",snt:"Sentinel Brief",raw:"Raw JSON"};
for(let i=1;i<=22;i++){const k="m"+(i<10?"0":"")+i;TAB_LABELS[k]=MN[k.toUpperCase()]||("Module "+i);}

function toggleTheme(){document.body.classList.toggle('light');localStorage.setItem('theme',document.body.classList.contains('light')?'light':'dark');}
(function(){const t=localStorage.getItem('theme');if(t==='light')document.body.classList.add('light');})();

function fetchWithTimeout(url,options={},timeoutMs=120000){
return new Promise((resolve,reject)=>{
const controller=new AbortController();
const timer=setTimeout(()=>controller.abort(),timeoutMs);
fetch(url,{...options,signal:controller.signal}).then(res=>{clearTimeout(timer);resolve(res);}).catch(err=>{clearTimeout(timer);if(err.name==='AbortError'){reject(new Error('Request timed out after '+(timeoutMs/1000)+' seconds. The analysis is taking longer than expected.'));}else{reject(err);}});
});
}

async function runUrlAnalysis(){
const url=document.getElementById('iUrl').value.trim();
const brand=document.getElementById('iUrlBrand').value.trim();
if(!url){alert('Please enter a published blog or article URL.');return;}
if(!url.startsWith('http')){alert('Please enter a valid URL starting with http:// or https://');return;}
const btn=document.getElementById('urlBtn');
btn.disabled=true;btn.textContent='Fetching & Analyzing...';
const aid='url_'+Date.now()+'_'+Math.floor(Math.random()*1e6);
showProgress('Fetching URL content & analyzing competitors...');
buildModGrid();
const poll=startProgressPolling(aid);
try{
const res=await fetchWithTimeout('/api/analyze-url',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url,brand:brand,locale:'en-US',device:'desktop',analysis_id:aid})},300000);
if(!res.ok){const errText=await res.text();stopProgressPolling(poll);document.getElementById('statusBox').innerHTML='<p style="color:var(--red);font-size:.82rem">Server error ('+res.status+'): '+esc(errText.slice(0,200))+'</p>';btn.disabled=false;btn.textContent='\u25B6 Analyze This URL';return;}
const data=await res.json();
stopProgressPolling(poll);
if(data.error){document.getElementById('statusBox').innerHTML='<p style="color:var(--red);font-size:.82rem">Error: '+esc(JSON.stringify(data.error).slice(0,500))+'</p>';btn.disabled=false;btn.textContent='\u25B6 Analyze This URL';return;}
markModuleDots(data);
showComplete(data);
setTimeout(()=>renderAll(data),400);
}catch(err){stopProgressPolling(poll);document.getElementById('statusBox').innerHTML='<p style="color:var(--red);font-weight:600">'+err.message+'</p><p style="font-size:.82rem;color:var(--txt3);margin-top:8px">If this persists, try using the keyword-based analysis instead, or check the browser console (F12) for details.</p>';}
btn.disabled=false;btn.textContent='\u25B6 Analyze This URL';
}
function showProgress(label){
const el=document.getElementById('statusBox');
el.innerHTML='<div class="progress"><div class="fill" id="pFill" style="width:0%"></div></div><p id="pText" style="font-size:.82rem;color:var(--txt3);margin-top:4px">'+esc(label)+'</p><div class="mod-grid" id="modGrid"></div>';
}
function buildModGrid(){
const mg=document.getElementById('modGrid');
if(!mg)return;
mg.innerHTML='';
Object.entries(MN).forEach(([k,v])=>{mg.innerHTML+=`<div class="mod-i" id="m_${k}" title="${esc(v)}"><div class="d w"></div><span>${k}</span></div>`;});
}
function startProgressPolling(analysisId){
if(window._progTimer)clearInterval(window._progTimer);
const timer=setInterval(async()=>{
try{
const r=await fetch('/api/progress/'+analysisId,{cache:'no-store'});
if(!r.ok)return;
const d=await r.json();
if(!d.ok)return;
const f=document.getElementById('pFill');if(f)f.style.width=(d.percent||0)+'%';
const t=document.getElementById('pText');
if(t){
if(d.current_module&&d.current_module_name)t.textContent='Running '+d.current_module+' - '+d.current_module_name+'...';
else if(d.phase_label)t.textContent=d.phase_label;
}
applyProgressDots(d);
}catch(e){}
},600);
window._progTimer=timer;
return timer;
}
function stopProgressPolling(timer){
if(window._progTimer){clearInterval(window._progTimer);window._progTimer=null;}
}
function applyProgressDots(d){
if(!d.module_status)return;
Object.keys(MN).forEach(k=>{
const st=d.module_status[k];
const el=document.getElementById('m_'+k);
if(!el)return;
const dot=el.querySelector('.d');
if(st==='completed')dot.className='d ok';
else if(st==='error')dot.className='d er';
else if(st==='running')dot.className='d r';
});
}
function markModuleDots(data){
Object.keys(MN).forEach(k=>{const el=document.getElementById('m_'+k);if(el){const d=el.querySelector('.d');d.className=data.module_results&&data.module_results[k]&&!data.module_results[k].error?'d ok':'d er';}});
}
function showComplete(data){
const mods=data.module_results||{};const ok=Object.keys(MN).filter(k=>mods[k]&&!mods[k].error).length;const fail=Object.keys(MN).length-ok;
const meta=data.analysis_metadata||{};
const elapsed=(meta.started_at&&meta.completed_at)?Math.round((new Date(meta.completed_at)-new Date(meta.started_at))/1000)+'s':'';
document.getElementById('topStatus').textContent='Analysis complete - '+ok+'/'+Object.keys(MN).length+' modules';
const errList=Object.keys(mods).filter(k=>mods[k]&&mods[k].error);
document.getElementById('statusBox').innerHTML='<div style="background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.4);border-radius:10px;padding:12px;margin-bottom:10px"><p style="color:var(--grn);font-weight:700;font-size:.9rem">&#10003; Analysis Complete</p><p style="font-size:.8rem;color:var(--txt2);margin-top:4px">'+ok+'/'+Object.keys(MN).length+' modules completed'+(fail?' &middot; '+fail+' failed':'')+(elapsed?' &middot; took '+elapsed:'')+'</p></div>'+(errList.length?'<p style="font-size:.78rem;color:var(--red);margin-bottom:8px">Failed modules: '+errList.join(', ')+'</p>':'');
const f=document.getElementById('pFill');if(f)f.style.width='100%';
}

function showToast(msg){const t=document.createElement('div');t.className='copy-toast';t.textContent=msg;document.body.appendChild(t);setTimeout(()=>t.remove(),2000);}
function copyText(txt){navigator.clipboard.writeText(txt).then(()=>showToast('Copied to clipboard!'));}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function showModuleInfo(mk){
const desc={
M01:"Analyzes the live SERP (DuckDuckGo), real SERP features (featured snippets, PAA, knowledge panels), and verifies Knowledge Graph entities against Wikidata (including Wikipedia sitelinks).",
M02:"Simulates how generative engines (Gemini, ChatGPT, Perplexity) and answer engines would treat your content. Uses real competitor pages to benchmark GEO readiness, citation triggers, and RAG-friendliness.",
M03:"Validates heading hierarchy, semantic HTML, schema markup and content flow. Compares your structure against real competitor headings from fetched pages.",
M04:"Profiles E-E-A-T gaps using live competitor entities, content gaps from fetched competitor pages, SME placement and unique value proposition analysis.",
M05:"Detects keyword cannibalization and builds internal link plans. Analyzes the actual link structure of the submitted URL (internal/external ratio, anchor text, real link health via HTTP verification).",
M06:"Scores fluff, cliches and AI-style patterns in your text using real competitor readability and fluff comparison.",
M07:"Verifies citations and sources in your content. Assesses hallucination risk and source credibility.",
M08:"Plans multimodal assets (images, video, infographics) benchmarked against real competitor media usage counts from fetched pages.",
M09:"Designs GEO/AEO tracking configuration, monitoring dashboards and alert systems, plus real related-query SERP landscape research.",
M10:"Simulates client-side rendering impact on indexing and content availability using the actual fetched HTML.",
M11:"Chunks your text and scores RAG-readiness, self-containedness and answer-extractability. Benchmarks against real competitor content depth.",
M12:"Enforces brand voice, terminology, regulated words and blacklisted terms across your content.",
M13:"Generates validated JSON-LD schemas (Article, FAQ, HowTo, Breadcrumb, Organization) from real entity and brand data with search-engine coverage analysis.",
M14:"Predicts bounce risk and intent alignment. Uses real competitor heading patterns and readability to benchmark your content's depth.",
M15:"Detects content decay using real Wayback Machine snapshots, HTTP status/headers and freshness scoring. Generates a refresh brief.",
M16:"Generates CDN edge worker snippets, server-header inspection and pre-render simulation for edge deployment.",
M17:"Designs statistical A/B tests for content experiments with sample-size, duration and rollback guardrails.",
M18:"Monitors indexing status and crawl budget health using real robots.txt, headers, sitemap and SERP presence.",
M19:"Builds hreflang configuration and localization sync using real related-query SERP research across locales.",
M20:"Creates a digital PR plan with real outlet discovery from live search, verified Wikidata entities and real competitor backlink/entity themes.",
M21:"Inspects the actual DOM from the fetched HTML: total elements, depth, layout-shift risk, script/style weight and rendering complexity.",
M22:"Prompts ChatGPT, Gemini, Perplexity and Claude with a fixed question set and captures transcripts, cited sources, sentiment and share-of-voice. Runs honest-mock without provider API keys."
};
openDetail(ev=null,null,mk,'key');
const m=document.getElementById('detailModal');
if(m){const t=m.querySelector('.dm-title');if(t)t.textContent=mk+': '+(MN[mk]||'');const box=m.querySelector('.dm-box');if(box){const p=document.createElement('p');p.style.cssText='margin:0 0 14px;padding:12px 14px;background:var(--s3);border-radius:8px;font-size:.9rem;color:var(--txt2);line-height:1.6';p.innerHTML=esc(desc[mk]||'');const title=m.querySelector('.dm-title');if(title)title.insertAdjacentElement('afterend',p);}}
}

function renderExportCard(){
return `<div class="card" style="border-color:var(--pri);margin-bottom:16px">
<h3>&#128228; Export &amp; Share Report</h3>
<div class="sg" style="grid-template-columns:1fr 1fr;gap:10px">
<button type="button" class="btn btn-go" onclick="downloadReportPdf(this)">&#11015; Download PDF Report</button>
<button type="button" class="btn btn-url" onclick="toggleMailBox()">&#9993; Email Me the PDF</button>
</div>
<div class="sg" style="grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
<button type="button" class="btn btn-url" onclick="downloadReportJson(this)">&#11015; Download JSON</button>
<button type="button" class="btn btn-url" onclick="shareReport(this)">&#128279; Copy Share Link</button>
</div>
<label style="display:flex;align-items:center;gap:8px;margin-top:12px;font-size:.82rem;color:var(--txt2);cursor:pointer"><input type="checkbox" id="slimPdf" style="width:auto"> Slim narrative PDF (skips the raw-JSON appendix — smaller &amp; faster)</label>
<p id="shareMsg" style="font-size:.82rem;margin-top:10px"></p>
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
const res=await fetchWithTimeout('/api/download_pdf',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report:data,narrative_only:!!(document.getElementById('slimPdf')||{}).checked})},60000);
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
async function downloadReportJson(btn){
const data=window._lastResults;
if(!data){showToast('Run an analysis first.');return;}
btn.disabled=true;const old=btn.textContent;btn.textContent='Generating JSON...';
try{
const res=await fetchWithTimeout('/api/download_json',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report:data})},60000);
if(!res.ok){const e=await res.json().catch(()=>({}));showToast((e.error||'JSON export failed').slice(0,80));return;}
const blob=await res.blob();
const a=document.createElement('a');a.href=URL.createObjectURL(blob);
const cd=res.headers.get('Content-Disposition')||'';
const m=cd.match(/filename="?([^";]+)"?/);a.download=m?m[1]:'content_report.json';
document.body.appendChild(a);a.click();a.remove();
setTimeout(()=>URL.revokeObjectURL(a.href),4000);
showToast('JSON downloaded!');
}catch(err){showToast('Failed: '+err.message.slice(0,80));}
finally{btn.disabled=false;btn.textContent=old;}
}
function setShareMsg(m,err){const el=document.getElementById('shareMsg');if(!el)return;el.innerHTML=esc(m);el.style.color=err?'var(--red)':'var(--grn)';}
async function shareReport(btn){
const data=window._lastResults;
if(!data){showToast('Run an analysis first.');return;}
btn.disabled=true;const old=btn.textContent;btn.textContent='Creating link...';
setShareMsg('Creating versioned share link...',false);
try{
const res=await fetchWithTimeout('/api/share',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({report:data})},30000);
const d=await res.json();
if(d.error){setShareMsg(d.error,true);}
else{
const url=(d.share_url||('/api/share/'+d.share_id));
const full=new URL(url,window.location.origin).href;
try{await navigator.clipboard.writeText(full);setShareMsg('Share link copied: '+full,false);}
catch(e){setShareMsg('Share link: '+full,false);}
}
}catch(err){setShareMsg('Failed: '+err.message,true);}
finally{btn.disabled=false;btn.textContent=old;}
}
async function sendOtp(){
const email=document.getElementById('mailEmail').value.trim();
if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){setMailMsg('Please enter a valid email.',true);return;}
const btn=document.getElementById('otpBtn');btn.disabled=true;btn.textContent='Sending OTP...';
setMailMsg('Sending OTP to '+email+' ...',false);
try{
const res=await fetchWithTimeout('/api/send_otp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email})},30000);
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
const res=await fetchWithTimeout('/api/verify_and_send_report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,otp:otp,report:window._lastResults})},60000);
const d=await res.json();
if(d.error){setMailMsg(d.error,true);}
else{setMailMsg('Success! PDF report sent to '+email+'.',false);}
}catch(err){setMailMsg('Failed: '+err.message,true);}
finally{btn.disabled=false;btn.textContent='Verify & Send PDF';}
}

document.getElementById('fForm').addEventListener('submit',async e=>{
e.preventDefault();
const btn=document.getElementById('runBtn');
btn.disabled=true;btn.textContent='Running 22-Module Analysis...';
const aid='an_'+Date.now()+'_'+Math.floor(Math.random()*1e6);
showProgress('Fetching live SERP data & analyzing competitors...');
buildModGrid();
const poll=startProgressPolling(aid);
try{
const body={seed:document.getElementById('iSeed').value,entity:document.getElementById('iEntity').value,brand:document.getElementById('iBrand').value,website:document.getElementById('iWebsite').value,locale:document.getElementById('iLocale').value,device:document.getElementById('iDevice').value,funnel:document.getElementById('iFunnel').value,knowledge:document.getElementById('iKnow').value,voice:document.getElementById('iVoice').value,secondary:document.getElementById('iSec').value,blacklist:document.getElementById('iBlack').value,sme:document.getElementById('iSME').value,analysis_id:aid};
const res=await fetchWithTimeout('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)},300000);
if(!res.ok){const errText=await res.text();stopProgressPolling(poll);document.getElementById('statusBox').innerHTML='<p style="color:var(--red);font-size:.82rem">Server error ('+res.status+'): '+esc(errText.slice(0,200))+'</p>';btn.disabled=false;btn.textContent='Run 22-Module Analysis';return;}
const data=await res.json();
stopProgressPolling(poll);
window._lastResults=data;
if(data.error){document.getElementById('statusBox').innerHTML='<p style="color:var(--red);font-size:.82rem">Error: '+esc(JSON.stringify(data.error).slice(0,500))+'</p>';btn.disabled=false;btn.textContent='Run 22-Module Analysis';return;}
markModuleDots(data);
showComplete(data);
setTimeout(()=>renderAll(data),400);
}catch(err){stopProgressPolling(poll);document.getElementById('statusBox').innerHTML='<p style="color:var(--red);font-weight:600">'+err.message+'</p><p style="font-size:.82rem;color:var(--txt3);margin-top:8px">If this persists, check the browser console (F12) for details, or try refreshing the page.</p>';}
btn.disabled=false;btn.textContent='Run 22-Module Analysis';
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
<div class="sb b"><div class="v" style="font-size:1rem;word-break:break-all">${esc(ud.url||'')}</div><div class="l">Analyzed URL</div></div>
<div class="sb"><div class="v">${esc(ud.title||'N/A')}</div><div class="l">Page Title</div></div>
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
TABS.forEach((t,i)=>{tabs+=`<button class="tab${i===0?' on':''}" onclick="showTab('${t}',this)">${TAB_LABELS[t]||t}</button>`;});
tabs+='</div>';
let panels='';
panels+=`<div class="panel on" id="p_exec">${urlBanner}${renderExportCard()}${renderExec(b.executive_summary||{})}</div>`;
panels+=`<div class="panel" id="p_edit">${renderEdit(b.output_1_editorial_blueprint||{})}</div>`;
panels+=`<div class="panel" id="p_geo">${renderGeo(b.output_2_geo_optimization||{})}</div>`;
panels+=`<div class="panel" id="p_tech">${renderTech(b.output_3_technical_payload||{})}</div>`;
panels+=`<div class="panel" id="p_cdn">${renderCDN(b.output_4_cdn_deployment||{})}</div>`;
panels+=`<div class="panel" id="p_snt">${renderSnt(b.output_5_sentinel_brief||{})}</div>`;
for(let i=1;i<=22;i++){const k="m"+(i<10?"0":"")+i;const mk="M"+(i<10?"0":"")+i;panels+=`<div class="panel" id="p_${k}">${renderModule(mk,mr[mk]||{})}</div>`;}
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

function showTab(id,el){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));const btn=el||(typeof event!=='undefined'&&event?(event.currentTarget||(event.target&&event.target.closest?event.target.closest('.tab'):null)):null);if(btn)btn.classList.add('on');const p=document.getElementById('p_'+id);if(p)p.classList.add('on');}

function renderExec(s){
let h=`<div class="card"><h3 class="section-click" onclick="openDetailValue('Executive Summary',window._rawB.executive_summary||window._rawB&&{})" title="Click for full raw data">&#127919; Executive Summary <span class="cb-hint">(click for full detail)</span></h3>`;
h+=`<div class="sg"><div class="sb b"><div class="v">${s.total_modules_executed||22}</div><div class="l">Modules</div></div><div class="sb r"><div class="v">${s.critical_issues_count||0}</div><div class="l">Critical</div></div><div class="sb y"><div class="v">${s.high_priority_count||0}</div><div class="l">High Priority</div></div><div class="sb p"><div class="v">${s.total_recommendations||0}</div><div class="l">Recommendations</div></div></div>`;
const cl=s.competitive_landscape||{};
if(cl.competitors_analyzed){
h+=`<div class="mblock cyan" style="margin-top:16px"><div class="mh">&#128202; Live Competitive Landscape</div>`;
h+=`<div class="sg" style="grid-template-columns:repeat(auto-fit,minmax(140px,1fr))"><div class="sb b"><div class="v">${cl.competitors_analyzed}</div><div class="l">Competitors Analyzed</div></div><div class="sb"><div class="v">${cl.serp_results_reviewed||0}</div><div class="l">SERP Results</div></div><div class="sb g"><div class="v">${(cl.content_gaps_vs_competitors||[]).length}</div><div class="l">Content Gaps</div></div><div class="sb p"><div class="v">${(cl.competitor_entity_themes||[]).length}</div><div class="l">Entity Themes</div></div></div>`;
const yvc=cl.your_content_vs_competitors||{};
if(yvc.word_count_yours){
h+=`<table><tr><th>Metric</th><th>Your Content</th><th>Competitor Avg</th><th>Delta</th><th>Position</th></tr>`;
if(yvc.word_count_yours!==undefined)h+=`<tr><td><strong>Word Count</strong></td><td>${yvc.word_count_yours||'N/A'}</td><td>${yvc.word_count_competitor_average||0}</td><td>${yvc.word_count_delta_percent!==null&&yvc.word_count_delta_percent!==undefined?(yvc.word_count_delta_percent>0?'<span class="ok">+':'<span class="no">')+yvc.word_count_delta_percent+'%</span>':'N/A'}</td><td>${yvc.word_count_position||''}</td></tr>`;
if(yvc.link_count_yours!==undefined)h+=`<tr><td><strong>Links</strong></td><td>${yvc.link_count_yours||'N/A'}</td><td>${yvc.link_count_competitor_average||0}</td><td colspan="2">&nbsp;</td></tr>`;
if(yvc.image_count_yours!==undefined)h+=`<tr><td><strong>Images</strong></td><td>${yvc.image_count_yours||'N/A'}</td><td>${yvc.image_count_competitor_average||0}</td><td colspan="2">&nbsp;</td></tr>`;
h+=`<tr><td><strong>Schema</strong></td><td>${yvc.schema_present_yours?'<span class="ok">Yes</span>':'<span class="no">No</span>'}</td><td>${yvc.schema_competitor_percentage||0}% adoption</td><td colspan="2">&nbsp;</td></tr>`;
h+=`</table>`;
}
const ccb=cl.competitor_content_benchmarks||{};
if(ccb.average_word_count){
h+=`<h4>Competitor Content Benchmarks (real, from N=${cl.competitors_analyzed} live pages)</h4><table><tr><th>Benchmark</th><th>Avg</th><th>Median</th><th>Max</th><th>P75</th></tr>`;
h+=`<tr><td>Word Count</td><td>${ccb.average_word_count||0}</td><td>${ccb.median_word_count||0}</td><td>${ccb.max_word_count||0}</td><td>${ccb.percentile_75_word_count||0}</td></tr>`;
h+=`<tr><td>H2 Headings</td><td>${ccb.average_h2_count||0}</td><td colspan="3">&nbsp;</td></tr>`;
h+=`<tr><td>H3 Headings</td><td>${ccb.average_h3_count||0}</td><td colspan="3">&nbsp;</td></tr>`;
h+=`<tr><td>Images</td><td>${ccb.average_image_count||0}</td><td colspan="3">&nbsp;</td></tr>`;
h+=`<tr><td>Internal Links</td><td>${ccb.average_internal_links||0}</td><td colspan="3">&nbsp;</td></tr>`;
h+=`<tr><td>External Links</td><td>${ccb.average_external_links||0}</td><td colspan="3">&nbsp;</td></tr>`;
h+=`<tr><td>Schema Adoption</td><td>${ccb.schema_adoption_percentage||0}%</td><td colspan="3">&nbsp;</td></tr>`;
h+=`</table>`;
}
const gaps=cl.content_gaps_vs_competitors||[];
if(gaps.length){h+=`<h4>Content Gaps vs Competitors (${gaps.length})</h4><div class="chips">${gaps.slice(0,15).map(g=>'<span class="chip">'+esc(String(g))+'</span>').join('')}</div>`;}
const ent=cl.competitor_entity_themes||[];
if(ent.length){h+=`<h4>Competitor Entity Themes</h4><div class="chips">${ent.slice(0,10).map(e=>'<span class="chip">'+esc(typeof e==='object'?JSON.stringify(e):String(e))+'</span>').join('')}</div>`;}
h+=`</div>`;
}
if(s.critical_issues&&s.critical_issues.length){h+=`<h4>Critical Issues</h4><table><tr><th>Module</th><th>Action</th><th>Detail</th></tr>`;s.critical_issues.forEach(i=>{h+=`<tr class="issue"><td><span class="tag cr">CRITICAL</span> ${esc(i.module||'')}</td><td>${esc(i.action||'')}</td><td>${esc(i.detail||'')}</td></tr>`;});h+=`</table>`;}
if(s.high_priority_actions&&s.high_priority_actions.length){h+=`<h4>High Priority Actions</h4><table><tr><th>Module</th><th>Action</th><th>Detail</th></tr>`;s.high_priority_actions.forEach(i=>{h+=`<tr class="issue"><td><span class="tag hi">HIGH</span> ${esc(i.module||'')}</td><td>${esc(i.action||'')}</td><td>${esc(i.detail||'')}</td></tr>`;});h+=`</table>`;}
h+=`</div>`;return h;}

function renderEdit(e){
let h=`<div class="card"><h3 class="section-click" onclick="openDetailValue('Editorial Blueprint',window._rawB.output_1_editorial_blueprint||{})" title="Click for full raw data">&#128221; Editorial &amp; Writing Blueprint <span class="cb-hint">(click for full detail)</span></h3>`;
const o=e.structural_outline||{};
h+=`<div class="sg"><div class="sb b"><div class="v">${o.total_estimated_words||'N/A'}</div><div class="l">Est. Words</div></div><div class="sb"><div class="v">${o.total_sections||0}</div><div class="l">H2 Sections</div></div><div class="sb p"><div class="v">${(e.direct_answer_blocks||[]).length}</div><div class="l">Answer Blocks</div></div><div class="sb g"><div class="v">${(e.smee_placement_markers||[]).length}</div><div class="l">SME Placements</div></div></div>`;
if(o.h1){h+=`<h4>H1 Title</h4><p style="font-size:.95rem;margin-bottom:12px"><strong>${esc(o.h1.title||'')}</strong></p><p style="margin-bottom:14px">${esc(o.h1.purpose||'')} | Target: ${o.h1.word_count_target||''}</p>`;}
if(o.h2_sections){h+=`<h4>Content Outline (${o.h2_sections.length} Sections)</h4><table><tr><th>#</th><th>Heading</th><th>Content Type</th><th>Word Target</th><th>Schema</th><th>Direct Answer</th></tr>`;o.h2_sections.forEach((s,i)=>{h+=`<tr><td>${i+1}</td><td><strong>${esc(s.title||'')}</strong></td><td>${esc(s.content_type||'')}</td><td>${s.word_count_target||''}</td><td>${s.schema_type||'none'}</td><td>${s.direct_answer_required?'&#10003;':'-'}</td></tr>`;if(s.h3_subsections){s.h3_subsections.forEach(j=>{h+=`<tr><td></td><td style="padding-left:20px;color:var(--txt3)">${esc(j.title||'')}</td><td>${esc(j.content_type||'')}</td><td>${j.word_count_target||''}</td><td></td><td></td></tr>`;});}});h+=`</table>`;}
const dab=e.direct_answer_blocks||[];
if(dab.length){h+=`<h4>Direct Answer Blocks (${dab.length})</h4><table><tr><th>ID</th><th>Heading Context</th><th>Word Count</th><th>Format</th><th>Citation Prob</th></tr>`;dab.forEach(d=>{h+=`<tr><td>${d.block_id||''}</td><td>${esc(d.heading_context||'')}</td><td>${d.target_word_count||''}</td><td>${esc(d.extraction_format||'')}</td><td>${d.citation_probability||''}</td></tr>`;});h+=`</table>`;}
const sm=e.smee_placement_markers||[];
if(sm.length){h+=`<h4>SME Quote Placements (${sm.length})</h4><table><tr><th>Expert</th><th>Title</th><th>Target Section</th><th>Priority</th><th>E-E-A-T Impact</th></tr>`;sm.forEach(s=>{h+=`<tr><td>${esc(s.sme_name||'')}</td><td>${esc(s.sme_title||'')}</td><td>${esc(s.target_section||'')}</td><td><span class="tag ${s.priority==='CRITICAL'?'cr':s.priority==='HIGH'?'hi':'md'}">${s.priority||''}</span></td><td>${s.eEat_enhancement||''}</td></tr>`;});h+=`</table>`;}
const ig=e.information_gain_checklist||[];
if(ig.length){h+=`<h4>Information Gain Checklist (${ig.length} Gaps)</h4><table><tr><th>Gap</th><th>Description</th><th>Opportunity</th><th>Action</th></tr>`;ig.forEach(g=>{h+=`<tr><td><span class="tag ${g.opportunity_level==='HIGH'?'cr':'hi'}">${g.opportunity_level||''}</span> ${g.category||''}</td><td>${g.description||''}</td><td>Competitor mentions: ${g.competitor_mention_count||0}</td><td>${g.recommended_action||''}</td></tr>`;});h+=`</table>`;}
const uv=e.unique_value_propositions||[];
if(uv.length){h+=`<h4>Unique Value Propositions (${uv.length})</h4><table><tr><th>UVP Type</th><th>Description</th><th>Differentiation Score</th><th>Recommendation</th></tr>`;uv.forEach(u=>{h+=`<tr><td>${u.uvp_type||''}</td><td>${u.description||''}</td><td>${u.differentiation_score||''}</td><td>${u.recommendation||''}</td></tr>`;});h+=`</table>`;}
const q=e.quality_targets||{};
if(Object.keys(q).length){h+=`<h4>Quality Targets</h4><table>`;Object.entries(q).forEach(([k,v])=>{h+=`<tr><td><strong>${esc(k.replace(/_/g,' '))}</strong></td><td>${esc(String(v))}</td></tr>`;});h+=`</table>`;}
const fl=e.content_flow||{};
if(Object.keys(fl).length){h+=`<h4>Content Flow Strategy</h4><table>`;Object.entries(fl).forEach(([k,v])=>{h+=`<tr><td><strong>${k.replace(/_/g,' ')}</strong></td><td>${Array.isArray(v)?v.join(', '):v}</td></tr>`;});h+=`</table>`;}
h+=`</div>`;return h;}

function renderGeo(g){
let h=`<div class="card"><h3 class="section-click" onclick="openDetailValue('GEO & AEO Optimization',window._rawB.output_2_geo_optimization||{})" title="Click for full raw data">&#127760; GEO &amp; AEO Optimization <span class="cb-hint">(click for full detail)</span></h3>`;
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
if(Object.keys(imp).length){h+=`<h4>Estimated Improvements</h4><table>`;Object.entries(imp).forEach(([k,v])=>{h+=`<tr><td><strong>${esc(k.replace(/_/g,' '))}</strong></td><td>${esc(String(v))}</td></tr>`;});h+=`</table>`;}
h+=`</div>`;return h;}

function renderTech(t){
let h=`<div class="card"><h3 class="section-click" onclick="openDetailValue('Technical Payload',window._rawB.output_3_technical_payload||{})" title="Click for full raw data">&#9881; Technical Payload <span class="cb-hint">(click for full detail)</span></h3>`;
h+=`<div class="sg"><div class="sb b"><div class="v">${Object.keys(t.json_ld_schemas||{}).length}</div><div class="l">Schema Types</div></div><div class="sb ${(t.cannibalization_status||'')==='LOW'?'g':'r'}"><div class="v">${t.cannibalization_status||'N/A'}</div><div class="l">Cannibalization</div></div><div class="sb ${(t.hallucination_risk||'')==='MINIMAL'?'g':'r'}"><div class="v">${t.hallucination_risk||'N/A'}</div><div class="l">Hallucination Risk</div></div><div class="sb b"><div class="v">${t.dom_size||0}</div><div class="l">DOM Elements</div></div><div class="sb"><div class="v">${t.csr_rendering_status||'N/A'}</div><div class="l">Render Mode</div></div></div>`;
const schemas=t.json_ld_schemas||{};
if(Object.keys(schemas).length){h+=`<h4>JSON-LD Schemas (${Object.keys(schemas).length})</h4>`;Object.entries(schemas).forEach(([nm,sc])=>{const id='sch_'+nm.replace(/[^a-z0-9]/gi,'');h+=`<button class="json-toggle" onclick="document.getElementById('${id}').classList.toggle('open');this.textContent=document.getElementById('${id}').classList.contains('open')?'Hide ${nm.toUpperCase()} Schema':'Show ${nm.toUpperCase()} Schema'">&#128196; Show ${nm.toUpperCase()} Schema</button><div class="json-content" id="${id}"><pre><code>${hl(JSON.stringify(sc,null,2))}</code></pre></div>`;});}
const il=t.internal_linking_blueprint||{};
if(Object.keys(il).length){h+=`<h4>Internal Linking Blueprint</h4><table>`;Object.entries(il).forEach(([k,v])=>{if(typeof v!=='object')h+=`<tr><td><strong>${esc(k.replace(/_/g,' '))}</strong></td><td>${esc(String(v))}</td></tr>`;});h+=`</table>`;}
const sv=t.schema_validation||{};
if(Object.keys(sv).length){h+=`<h4>Schema Validation</h4><table><tr><th>Schema</th><th>Valid</th><th>Errors</th></tr>`;Object.entries(sv).forEach(([k,v])=>{h+=`<tr${v.valid?'':' class="issue"'}><td>${k}</td><td><span class="tag ${v.valid?'lo':'cr'}">${v.valid?'VALID':'INVALID'}</span></td><td>${(v.errors||[]).join('; ')||'None'}</td></tr>`;});h+=`</table>`;}
const se=t.search_engine_coverage||{};
if(Object.keys(se).length){h+=`<h4>Search Engine Coverage</h4>`;if(se.engine_coverage){h+=`<table><tr><th>Engine</th><th>Coverage</th><th>Rich Results</th></tr>`;Object.entries(se.engine_coverage).forEach(([k,v])=>{h+=`<tr><td>${k}</td><td>${v.coverage}/${(v.supported_types||[]).length} types</td><td>${v.rich_results_eligible?'Yes':'No'}</td></tr>`;});h+=`</table>`;}}
h+=`</div>`;return h;}

function renderCDN(c){
let h=`<div class="card"><h3 class="section-click" onclick="openDetailValue('CDN & Edge Deployment',window._rawB.output_4_cdn_deployment||{})" title="Click for full raw data">&#128231; CDN &amp; Edge Deployment <span class="cb-hint">(click for full detail)</span></h3>`;
const ew=c.edge_worker_snippet||{};
if(ew.worker_code){h+=`<h4>Edge Worker Code (${ew.cdn_provider||'Cloudflare'})</h4><pre><code>${ew.worker_code}</code></pre>`;if(ew.testing_steps){h+=`<h4>Testing Steps</h4><ul>`;ew.testing_steps.forEach(s=>{h+=`<li>${s}</li>`;});h+=`</ul>`;}}
const sh=c.server_header_inspection||{};
if(sh.inspection_results){h+=`<h4>Server Header Inspection</h4><table><tr><th>Header</th><th>Expected</th><th>Current</th><th>Status</th></tr>`;sh.inspection_results.forEach(r=>{h+=`<tr class="${r.status==='CORRECT'?'':'issue'}"><td>${r.header}</td><td style="font-size:.8rem">${r.expected}</td><td>${r.current}</td><td><span class="tag ${r.status==='CORRECT'?'lo':'cr'}">${r.status}</span></td></tr>`;});h+=`</table>`;}
const pr=c.prerender_simulation||{};
if(Object.keys(pr).length){h+=`<h4>Pre-Render Simulation</h4><table>`;Object.entries(pr).forEach(([k,v])=>{if(typeof v!=='object')h+=`<tr><td><strong>${esc(k.replace(/_/g,' '))}</strong></td><td>${esc(String(v))}</td></tr>`;else if(v&&typeof v==='object'){Object.entries(v).forEach(([k2,v2])=>{h+=`<tr><td style="padding-left:16px">${k2.replace(/_/g,' ')}</td><td>${v2}</td></tr>`;});}});h+=`</table>`;}
const cd=c.cdn_configuration||{};
if(Object.keys(cd).length){const id='cdn_cfg';h+=`<button class="json-toggle" onclick="document.getElementById('${id}').classList.toggle('open');this.textContent=document.getElementById('${id}').classList.contains('open')?'Hide CDN Config':'Show CDN Config'">&#128196; Show CDN Configuration</button><div class="json-content" id="${id}"><pre><code>${hl(JSON.stringify(cd,null,2))}</code></pre></div>`;}
const dg=c.deployment_guide||{};
if(dg.deployment_steps){h+=`<h4>Deployment Guide</h4><ul>`;dg.deployment_steps.forEach(s=>{h+=`<li>${s}</li>`;});h+=`</ul>`;}
h+=`</div>`;return h;}

function renderSnt(s){
let h=`<div class="card"><h3 class="section-click" onclick="openDetailValue('Sentinel Brief',window._rawB.output_5_sentinel_brief||{})" title="Click for full raw data">&#128737; Post-Publish Sentinel Brief <span class="cb-hint">(click for full detail)</span></h3>`;
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
let h=`<div class="card mod-card" id="mc_${mk}">
<div class="mod-head" onclick="toggleMod('${mk}')" title="Click to collapse / expand this module">
<span class="mnum">${mk}</span><span class="mname">${MN[mk]||''}</span><span class="mcaret">&#9660;</span>
</div>
<div class="mod-body">`;
try{
const SKIPKEYS=['module','module_name','recommendations','implementation_steps','where_to_add','detailed_analysis','live_verified_statistics','competitive_benchmarking','score_benchmarks','recommendation_playbook'];
const pretty=k=>esc(String(k).replace(/_/g,' '));
function cell(val,kk){
if(val==null)return'&mdash;';
if(typeof val==='object')return rv(val,kk);
const s=String(val);
return isIssue(val)?'<span class="issue">'+esc(s)+'</span>':esc(s);
}
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
h+=`<div class="sb ${cls} clickable-block" onclick="openDetail(event,null,'${mk}','key',${JSON.stringify(k)})" title="Click for full detail"><div class="v">${esc(disp)}</div><div class="l">${pretty(k)}</div></div>`;
});
h+='</div>';
}
/* ===========================  ANALYSIS FIRST  =========================== */
h+='<div class="mblock" style="border-color:rgba(124,92,252,.45);background:linear-gradient(135deg,rgba(124,92,252,.07),rgba(34,211,238,.04))"><div class="mh">&#128270; Full Analysis <span class="cb-hint">all findings for this module</span></div>';
if(mr.score_benchmarks&&Array.isArray(mr.score_benchmarks)&&mr.score_benchmarks.length){
h+='<div class="mblock cyan"><div class="mh">&#127942; Score Benchmarks <span class="cb-hint">what to aim for</span></div>';
h+='<table class="tbl-click"><tr><th>Score</th><th>Your Value</th><th>Target</th><th>Status</th><th>What It Means For Rankings / AI Overview / AI Citations</th></tr>';
mr.score_benchmarks.slice(0,12).forEach(b=>{
const sc=b.scale==='0-100'?esc(String(b.value)):((b.value||0)<=1.5?Math.round((b.value||0)*100)+'%':esc(String(b.value)));
const lvl=b.level||'unknown';
const lc=lvl==='excellent'?'lo':lvl==='good'?'md':lvl==='needs_work'?'hi':'cr';
const lt=lvl==='excellent'?'EXCELLENT':lvl==='good'?'GOOD':lvl==='needs_work'?'NEEDS WORK':'FAIL';
const tg=b.scale==='0-100'?(b.target!==undefined?b.target+'%':'N/A'):((b.target||0)<=1.5?Math.round((b.target||0)*100)+'%':'N/A');
h+='<tr class="dm-click" data-dm="'+dmRef(b,pretty(b.key))+'"><td><strong>'+pretty(b.key)+'</strong></td><td><strong class="'+(lvl==='excellent'?'ok':lvl==='good'?'num':lvl==='needs_work'?'no':'no')+'">'+sc+'</strong></td><td>'+tg+'</td><td><span class="tag '+lc+'">'+lt+'</span></td><td style="font-size:.78rem">R: '+esc(b.rankings||'')+'<br>A: '+esc(b.ai_overview||'')+'<br>C: '+esc(b.ai_citation||'')+'</td></tr>';
});
h+='</table><p style="font-size:.72rem;color:var(--txt3);margin-top:6px">Benchmarks are standard industry guidance (heuristic, unverified) - not measured ranking guarantees. Click any row for full detail.</p></div>';
}
if(mr.detailed_analysis&&typeof mr.detailed_analysis==='object'){
h+='<div class="acc"><button class="accb open" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">Detailed Analysis <span class="accarrow">&#9660;</span></button><div class="accp open">';
Object.entries(mr.detailed_analysis).forEach(([k,v])=>{
if(k==='score_benchmarks'||k==='live_verified_statistics')return;
h+='<div class="acc"><button class="accb" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">'+pretty(k)+' <span class="accarrow">&#9660;</span></button><div class="accp">'+rv(v,k)+'</div></div>';
});
h+='</div></div>';
}
if(mr.live_verified_statistics&&typeof mr.live_verified_statistics==='object'){
const lvs=mr.live_verified_statistics;
if(lvs.total_statistics){
h+='<div class="acc"><button class="accb open" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">Live Verified Statistics ('+lvs.total_statistics+') <span class="accarrow">&#9660;</span></button><div class="accp open"><table class="tbl-click"><tr><th style="width:8px">#</th><th>Statistic</th><th>Source</th></tr>';
(lvs.statistics||[]).forEach((st,i)=>{
const src=st.source_url||'';
h+='<tr onclick="openDetail(event,null,\''+mk+'\',\'obj\',\'live_verified_statistics\')" title="Click for full detail"><td>'+(i+1)+'</td><td style="font-size:.8rem">'+esc(st.stat||'')+'</td><td style="font-size:.72rem;word-break:break-all">'+(src?'<a href="'+esc(src)+'" target="_blank" rel="noopener" onclick="event.stopPropagation()">'+esc(st.source_title||src.slice(0,60))+'</a>':'&mdash;')+'</td></tr>';
});
h+='</table></div></div>';
}
}
if(mr.competitive_benchmarking&&typeof mr.competitive_benchmarking==='object'){
h+='<div class="acc"><button class="accb open" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">Competitive Benchmarking <span class="accarrow">&#9660;</span></button><div class="accp open">';
h+='<p style="font-size:.78rem;color:var(--txt3);margin-bottom:8px">'+esc(mr.competitive_benchmarking.methodology||'')+'</p>';
h+='<div class="sg">';
if(mr.competitive_benchmarking.competitors_analyzed!==undefined)h+='<div class="sb b clickable-block" onclick="openDetail(event,null,\''+mk+'\',\'obj\',\'competitive_benchmarking\')" title="Click for full detail"><div class="v">'+mr.competitive_benchmarking.competitors_analyzed+'</div><div class="l">Competitors Analyzed</div></div>';
const ccb=mr.competitive_benchmarking.competitor_content_benchmarks||{};
if(ccb.average_word_count!==undefined)h+='<div class="sb"><div class="v">'+ccb.average_word_count+'</div><div class="l">Competitor Avg Words</div></div>';
const yvc=mr.competitive_benchmarking.your_content_vs_competitors||{};
if(yvc.word_count_delta_percent!==undefined&&yvc.word_count_delta_percent!==null)h+='<div class="sb '+(yvc.word_count_delta_percent>=0?'g':'r')+'"><div class="v">'+(yvc.word_count_delta_percent>0?'+':'')+yvc.word_count_delta_percent+'%</div><div class="l">Word Count Delta vs Avg</div></div>';
h+='</div>';
h+='<div class="acc"><button class="accb" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">Full Benchmarking Data <span class="accarrow">&#9660;</span></button><div class="accp">'+rv(mr.competitive_benchmarking,'competitive_benchmarking')+'</div></div>';
h+='</div></div>';
}
Object.keys(mr).forEach(k=>{
if(SKIPKEYS.includes(k)||statShown.includes(k))return;
h+='<div class="mblock clickable-block" onclick="openDetail(event,null,\''+mk+'\',\'key\',\''+k+'\')" title="Click for full detail"><div class="mh">'+pretty(k)+' <span class="cb-hint">(click for full detail)</span></div>'+rv(mr[k],k)+'</div>';
});
h+='</div>';
/* ===========================  RECOMMENDATIONS AFTER ANALYSIS  =========================== */
if(mr.recommendation_playbook&&typeof mr.recommendation_playbook==='object'){
const pb=mr.recommendation_playbook;
h+='<div class="mblock" style="border-color:rgba(52,211,153,.5);background:linear-gradient(135deg,rgba(52,211,153,.06),rgba(251,191,36,.04))"><div class="mh">&#9889; Recommendations &amp; Action Plan <span class="cb-hint">after analysis above</span></div>';
h+='<div class="acc"><button class="accb open" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">What To Do <span class="accarrow">&#9660;</span></button><div class="accp open"><ol class="steps">';
(pb.what_to_do||[]).forEach(w=>{h+='<li>'+esc(String(w))+'</li>';});
h+='</ol></div></div>';
h+='<div class="acc"><button class="accb" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">When To Do It <span class="accarrow">&#9660;</span></button><div class="accp"><ul class="where">';
(pb.when_to_do||[]).forEach(w=>{h+='<li>'+esc(String(w))+'</li>';});
h+='</ul></div></div>';
h+='<div class="acc"><button class="accb" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">Tools To Use <span class="accarrow">&#9660;</span></button><div class="accp"><table class="tbl-click"><tr><th>Tool</th><th>How To Use It</th></tr>';
(pb.tools_to_use||[]).forEach(t=>{
const rid=dmRef(t,'tool');
h+='<tr class="dm-click" data-dm="'+rid+'"><td><strong>'+esc(t.tool||'')+'</strong></td><td style="font-size:.82rem">'+esc(t.use||'')+'</td></tr>';
});
h+='</table></div></div>';
const ab=pb.ab_test_plan||{};
if(Object.keys(ab).length){
h+='<div class="acc"><button class="accb" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">A/B Test Plan - How To Verify It Works <span class="accarrow">&#9660;</span></button><div class="accp">';
h+='<table class="kv2 tbl-click">';
[['Hypothesis',ab.hypothesis],['Variant A',ab.variant_a],['Variant B',ab.variant_b],['Metrics',(ab.metrics||[]).join(', ')],['Duration',(ab.duration_days||'')+' days'],['How To Judge',ab.check]].forEach(([k2,v2])=>{
const rid=dmRef(ab,k2);
h+='<tr class="dm-click" data-dm="'+rid+'" data-dml="'+esc('A/B test > '+k2)+'"><th>'+esc(k2)+'</th><td>'+esc(String(v2||''))+'</td></tr>';
});
h+='</table></div></div>';
}
h+='</div>';
} else {
if(mr.recommendations&&mr.recommendations.length){
h+='<div class="mblock"><div class="mh">&#9889; Recommendations</div>';
h+='<table class="tbl-click"><tr><th style="width:120px">Priority</th><th>Action</th><th>Detail</th></tr>';
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
}
}catch(e){h+='<p style="background:var(--issue-fill);color:var(--issue-ink);padding:12px;border-radius:8px;font-weight:700">Render error: '+esc(e.message)+'</p>';}
h+=`</div></div>`;return h;}
function prettyK(k){return esc(String(k).replace(/_/g,' '));}
window._dmSeq=0;window._dmCache={};
function dmRef(value,label){
const id='dm_'+(++window._dmSeq);
try{window._dmCache[id]=(typeof value==='string')?value:JSON.parse(JSON.stringify(value));}catch(e){window._dmCache[id]=String(value);}
return id;
}
function dmHtml(value,label,extraClass){
const id=dmRef(value,label);
return `<span class="dm-click ${extraClass||''}" data-dm="${id}" data-dml="${esc(label||'')}" title="Click for full detail">${esc(label!=null?label:'')}</span>`;
}
document.addEventListener('click',function(ev){
const t=ev.target.closest('.dm-click');
if(!t)return;
ev.stopPropagation();
const id=t.getAttribute('data-dm');
const lbl=t.getAttribute('data-dml');
let val=window._dmCache[id];
if(val===undefined){if(t.textContent!=='')val=t.textContent;}
openDetailValue(lbl||'Detail',val);
});
function openDetailValue(title,dataVal){
const body=document.createElement('div');
body.className='detail-modal';
body.id='detailModal';
body.innerHTML='<div class="dm-box"><button class="dm-close" onclick="document.getElementById(\'detailModal\').remove()">&#10005; Close</button><div class="dm-title">'+title+'</div><div>'+rv(dataVal,'detail')+'</div><div style="margin-top:14px"><button class="btn" style="width:auto;padding:8px 16px;font-size:.82rem;background:var(--txt);color:var(--bg)" onclick="copyText(window._detailJson)">Copy JSON</button></div></div>';
window._detailJson=JSON.stringify(dataVal);
body.onclick=e=>{if(e.target===body)body.remove();};
document.body.appendChild(body);
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
let t='<div style="overflow-x:auto"><table class="tbl-click">';ks.forEach(kk=>{t+='<th>'+prettyK(kk)+'</th>';});t+='</tr>';
v.slice(0,25).forEach((item,idx)=>{
const rid=dmRef(item,k+' item '+(idx+1));
let rowIss=false;const c=ks.map(kk=>{let val=item[kk];if(!rowIss&&isIssue(val))rowIss=true;return '<td style="font-size:.8rem">'+((typeof val==='object'&&val!==null)?rv(val,kk):cellGlobal(val,kk))+'</td>';}).join('');
t+='<tr class="dm-click" data-dm="'+rid+'" data-dml="'+esc(k)+' item '+(idx+1)+'" title="Click for full detail"'+(rowIss?' data-iss="1"':'')+'>'+c+'</tr>';
});
if(v.length>25)t+='<tr><td colspan="'+ks.length+'" class="more">+'+(v.length-25)+' more</td></tr>';
return t+'</table></div>';
}
}
const chipIds=v.map(i=>dmRef(i,k));
return'<div class="chips">'+v.map((i,idx)=>'<span class="chip dm-click" data-dm="'+chipIds[idx]+'" data-dml="'+esc(k)+'" title="Click for full detail">'+esc(String(i))+'</span>').join('')+'</div>';
}
if(typeof v==='object'){
const entries=Object.entries(v);
if(!entries.length)return'<span class="dash">&mdash;</span>';
if(entries.some(([,val])=>val&&typeof val==='object')){
let s='<div class="subs">';
entries.forEach(([kk,val])=>{
const rid=dmRef({[kk]:val},k+' > '+kk);
s+='<div class="sub dm-click" data-dm="'+rid+'" data-dml="'+esc(k+' > '+kk)+'" title="Click for full detail"><div class="subh">'+prettyK(kk)+'</div><div class="subb">'+rv(val,kk)+'</div></div>';
});
return s+'</div>';
}
let t='<table class="kv2 tbl-click">';
entries.forEach(([kk,val])=>{
const rid=dmRef({[kk]:val},k+' > '+kk);
let rowIss=isIssue(val);
t+='<tr class="dm-click" data-dm="'+rid+'" data-dml="'+esc(k+' > '+kk)+'" title="Click for full detail"'+(rowIss?' data-iss="1"':'')+'><th>'+prettyK(kk)+'</th><td>'+rv(val,kk)+'</td></tr>';
});
return t+'</table>';
}
return esc(String(v));
}
function cellGlobal(val,kk){
if(val==null)return'&mdash;';
if(typeof val==='object')return rv(val,kk);
const s=String(val);
return isIssue(val)?'<span class="issue">'+esc(s)+'</span>':esc(s);
}
function toggleMod(mk){const c=document.getElementById('mc_'+mk);if(c)c.classList.toggle('closed');}
function openDetail(ev,el,mk,type,key){
if(ev)ev.stopPropagation();
if(ev&&ev.target&&ev.target.closest&&ev.target.closest('.dm-click'))return;
const mr=(window._rawMr||{})[mk]||{};
let title=mk+': '+(MN[mk]||'');
let dataVal;
if(type==='key'&&key!==undefined){dataVal=mr[key];title+=' &rarr; '+prettyK(key);}
else if(type==='obj'&&key!==undefined){dataVal=mr[key];title+=' &rarr; '+prettyK(key);}
else dataVal=mr;
const body=document.createElement('div');
body.className='detail-modal';
body.id='detailModal';
body.innerHTML='<div class="dm-box"><button class="dm-close" onclick="document.getElementById(\'detailModal\').remove()">&#10005; Close</button><div class="dm-title">'+title+'</div><div>'+rv(dataVal,'detail')+'</div><div style="margin-top:14px"><button class="btn" style="width:auto;padding:8px 16px;font-size:.82rem;background:var(--txt);color:var(--bg)" onclick="copyText(window._detailJson)">Copy JSON</button></div></div>';
window._detailJson=JSON.stringify(dataVal);
body.onclick=e=>{if(e.target===body)body.remove();};
document.body.appendChild(body);
}

function hl(j){return j.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"([^"]+)"(?=\s*:)/g,'<span class="jk">"$1"</span>').replace(/"([^"]*)"/g,'<span class="js">"$1"</span>').replace(/\b(-?\d+\.?\d*)\b/g,'<span class="jn">$1</span>').replace(/\b(true|false|null)\b/g,'<span class="jb">$1</span>');}
</script>
</body>
</html>"""

if __name__=='__main__':
    print("\n"+"="*60)
    print("  Intent, Entity & Semantic Intelligence Platform")
    print("  Web Interface: http://localhost:5000")
    print("  DEPLOYMENT: localhost only. For LAN/prod use gunicorn/waitress + nginx")
    print("    reverse proxy (TLS, HSTS, rate-limit at edge). Never expose Flask dev")
    print("    server directly. Set APP_DEBUG=false (default) so 500s never leak traces.")
    print("    SERP_PROVIDER=serper|dataforseo|ddg_fallback (default ddg_fallback).")
    print("="*60+"\n")
    host=os.environ.get("HOST","127.0.0.1")
    port=int(os.environ.get("PORT","5000"))
    app.run(host=host,port=port,debug=False,threaded=True)
