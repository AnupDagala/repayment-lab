"""Repayment Lab: reproducible synthetic installment analytics. Standard library only."""
import argparse
import calendar
import csv
import hashlib
import html
import json
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUCKETS = ['Current', '1–30', '31–60', '61–90', '90+']

def bucket(dpd):
    return BUCKETS[0 if dpd == 0 else 1 if dpd <= 30 else 2 if dpd <= 60 else 3 if dpd <= 90 else 4]

def month_add(d, n):
    m = d.year * 12 + d.month - 1 + n
    y, m = divmod(m, 12)
    return date(y, m+1, min(d.day, calendar.monthrange(y, m+1)[1]))

def connect():
    c = sqlite3.connect(':memory:')
    c.row_factory = sqlite3.Row
    c.executescript((ROOT/'sql/schema.sql').read_text())
    return c

def seed(c, n=600, seed_value=42):
    r = random.Random(seed_value)
    for k in range(n):
        origin = date(2026, 1 + k % 6, r.randint(1, 28))
        segment = ['Salaried', 'Self-employed', 'New-to-credit'][k % 3]
        # Explicit simulation assumptions, not estimates of any lender's performance.
        due = r.choice([400000, 600000, 800000, 1000000])
        c.execute('INSERT INTO loans VALUES(?,?,?,?)', (f'L{k:04}', origin.isoformat(), segment, due*6))
        chronic = r.random() < (0.08 if segment == 'Salaried' else 0.15)
        for j in range(1, 7):
            iid = f'I{k:04}-{j}'
            day = month_add(origin, j)
            c.execute('INSERT INTO installments VALUES(?,?,?,?)', (iid, f'L{k:04}', day.isoformat(), due))
            if chronic and j >= 2:
                continue
            late = r.choice([0, 0, 0, 4, 12, 35, 65])
            if segment == 'New-to-credit' and origin.month >= 5:
                late += 20
            # Split payments exercise one-to-many aggregation and partial repayment.
            for part, amount, offset in [(1, due//2, late), (2, due-due//2, late+3)]:
                c.execute('INSERT INTO payments VALUES(?,?,?,?)', (f'P{iid}-{part}', iid, (day+timedelta(days=offset)).isoformat(), amount))
    c.commit()

def snapshot(c, as_of, segment='All'):
    date.fromisoformat(as_of)
    rows = [dict(x) for x in c.execute((ROOT/'sql/snapshot.sql').read_text(), {'as_of': as_of})]
    for row in rows:
        row['bucket'] = bucket(row['dpd'])
    return [x for x in rows if segment == 'All' or x['segment'] == segment]

def metrics(rows):
    result = {key: sum(x[key] for x in rows) for key in ['outstanding_paise','overdue_paise','due_paise','collected_paise','excess_paise']}
    result['loans'] = len(rows)
    result['collection_pct'] = round(100*result['collected_paise']/result['due_paise'], 2) if result['due_paise'] else None
    result['dpd30_balance_pct'] = round(100*sum(x['outstanding_paise'] for x in rows if x['dpd']>=30)/result['outstanding_paise'],2) if result['outstanding_paise'] else None
    return result

def quality(c, as_of):
    due = c.execute('SELECT SUM(due_paise) FROM installments i JOIN loans l USING(loan_id) WHERE l.originated<=?', (as_of,)).fetchone()[0] or 0
    rows = snapshot(c, as_of)
    paid = c.execute('SELECT SUM(amount_paise) FROM payments p JOIN installments i USING(installment_id) JOIN loans l USING(loan_id) WHERE paid_date<=? AND l.originated<=?', (as_of,as_of)).fetchone()[0] or 0
    remaining = sum(x['outstanding_paise'] for x in rows)
    excess = sum(x['excess_paise'] for x in rows)
    delta = due - (remaining+paid-excess)
    chronology = c.execute('SELECT COUNT(*) FROM installments i JOIN loans l USING(loan_id) WHERE i.due_date<l.originated').fetchone()[0]
    early_payments = c.execute('SELECT COUNT(*) FROM payments p JOIN installments i USING(installment_id) JOIN loans l USING(loan_id) WHERE p.paid_date<l.originated').fetchone()[0]
    return {'reconciliation_delta_paise':delta,'excess_payment_paise':excess,'installments_before_origination':chronology,'payments_before_origination':early_payments,'foreign_key_errors':len(list(c.execute('PRAGMA foreign_key_check'))),'passed':delta==0 and excess==0 and chronology==0 and early_payments==0}

def transitions(c, start, end, segment='All'):
    if start >= end:
        raise ValueError('Transition start must be before end')
    before = {x['loan_id']:x for x in snapshot(c,start,segment)}
    after = {x['loan_id']:x for x in snapshot(c,end,segment)}
    counts = [[0]*5 for _ in range(5)]
    for lid in before.keys() & after.keys():
        counts[BUCKETS.index(before[lid]['bucket'])][BUCKETS.index(after[lid]['bucket'])] += 1
    return {'start':start,'end':end,'matched_loans':sum(map(sum,counts)),'counts':counts}

def cohort_mob(c):
    # Same month-on-book across cohorts; never compare differently aged loans.
    out=[]
    for cohort in [f'2026-{m:02}' for m in range(1,7)]:
        for mob in [1,2,3]:
            d=month_add(date.fromisoformat(cohort+'-01'),mob)
            cutoff=date(d.year,d.month,calendar.monthrange(d.year,d.month)[1]).isoformat()
            rows=[x for x in snapshot(c,cutoff) if x['cohort']==cohort]
            out.append({'cohort':cohort,'mob':mob,'cutoff':cutoff,**metrics(rows)})
    return out

def write_csv(path, rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['no_data'])
        w.writeheader(); w.writerows(rows)

def table(headers, rows):
    return '<table><thead><tr>'+''.join('<th>'+html.escape(str(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'

def money(paise):
    return '₹'+format(paise/100,',.0f')

def build(out):
    out.mkdir(parents=True,exist_ok=True)
    c=connect(); seed(c)
    months=['2026-07-31','2026-08-31','2026-09-30']
    payload={'data_type':'SYNTHETIC — no real customer or Navi data','snapshots':{},'mob':cohort_mob(c)}
    for d in months:
        rows=snapshot(c,d)
        payload['snapshots'][d]={'rows':rows,'metrics':metrics(rows),'quality':quality(c,d)}
    payload['transitions']=transitions(c,months[-2],months[-1])
    write_csv(out/'loan_snapshot.csv',payload['snapshots'][months[-1]]['rows'])
    write_csv(out/'cohort_mob.csv',payload['mob'])
    for t in ['loans','installments','payments']:
        write_csv(out/(t+'.csv'),[dict(x) for x in c.execute('SELECT * FROM '+t)])
    (out/'data.json').write_text(json.dumps(payload,indent=2))
    c.backup(sqlite3.connect(out/'repayment.db'))
    # Self-contained dashboard: no CDN, service, login, or network required.
    template=(ROOT/'dashboard.html').read_text()
    (out/'index.html').write_text(template.replace('/*PAYLOAD*/',json.dumps(payload)))
    sums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='manifest.json'}
    (out/'manifest.json').write_text(json.dumps(sums,indent=2))
    return payload

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,default=ROOT/'demo')
    args=parser.parse_args(); p=build(args.out)
    print(json.dumps(p['snapshots']['2026-09-30']['metrics'],indent=2))
    print('Quality:',p['snapshots']['2026-09-30']['quality'])
    print('Open',args.out/'index.html')
