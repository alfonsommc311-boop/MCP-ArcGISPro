import csv, datetime, os

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, "Tareas.csv")

def parse_date(s):
    return datetime.date.fromisoformat(s.strip())

# Spread each task's cost evenly across its calendar days, aggregate by month.
monthly = {}  # 'YYYY-MM' -> cost
with open(src, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        try:
            cost = float(row["Costo"] or 0)
        except ValueError:
            cost = 0.0
        if cost <= 0:
            continue
        ini = parse_date(row["Inicio"])
        fin = parse_date(row["Fin"])
        # Distribuir el costo solo entre dias habiles (lun-vie) del tramo
        workdays = []
        d = ini
        while d <= fin:
            if d.weekday() < 5:
                workdays.append(d)
            d += datetime.timedelta(days=1)
        if not workdays:
            workdays = [ini]
        per_day = cost / len(workdays)
        for wd in workdays:
            key = f"{wd.year:04d}-{wd.month:02d}"
            monthly[key] = monthly.get(key, 0.0) + per_day

total = sum(monthly.values())
rows = []
acc = 0.0
for key in sorted(monthly):
    m = monthly[key]
    acc += m
    y, mo = key.split("-")
    first = f"{y}-{mo}-01"
    rows.append((first, round(m, 2), round(acc, 2), round(acc / total * 100, 2)))

out = os.path.join(base, "CurvaS.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Mes", "CostoMensual", "CostoAcumulado", "PctAcumulado"])
    w.writerows(rows)

print(f"Filas: {len(rows)}  Total distribuido: {round(total,2)}")
print(f"Salida: {out}")
