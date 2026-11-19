"""Mide evaluar.py contra una clave etiquetada.

Uso:  python medir.py casos.jsonl clave.csv [manual.json]

Reporta (no solo el % de acierto, que con pocas fallas engaña):
- acierto exacto (veredicto + regla) y acierto de veredicto;
- matriz de confusión del veredicto y kappa de Cohen;
- precisión / recall por regla (la clase de falla es la que importa);
- cada desacuerdo con la justificación del evaluador, para adjudicarlo a mano.
"""
import csv
import json
import sys
from collections import Counter

from evaluar import REGLAS, evaluar, evaluar_detalle


def kappa(pares):
    n = len(pares)
    if not n:
        return float("nan")
    po = sum(a == b for a, b in pares) / n
    ca, cb = Counter(a for a, _ in pares), Counter(b for _, b in pares)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def fmt(x):
    return "n/c" if x is None else f"{x:.2f}"


def main(casos_path, clave_path, manual_path="kit/manual.json"):
    with open(manual_path, encoding="utf-8-sig") as f:
        manual = json.load(f)
    with open(casos_path, encoding="utf-8-sig") as f:
        lista = [json.loads(l) for l in f if l.strip()]
    with open(clave_path, encoding="utf-8-sig") as f:
        filas = list(csv.DictReader(f))
    casos = {c.get("id"): c for c in lista}
    clave = {r["id"]: (r["veredicto"], r.get("regla") or "") for r in filas}
    # Insumos: un id duplicado o sin par invalida la medición; se informa antes de dividir.
    problemas = []
    if len(casos) != len(lista):
        problemas.append("ids duplicados en los casos")
    if len(clave) != len(filas):
        problemas.append("ids duplicados en la clave")
    if set(casos) - set(clave):
        problemas.append(f"casos sin clave: {sorted(map(str, set(casos) - set(clave)))}")
    if set(clave) - set(casos):
        problemas.append(f"clave sin casos: {sorted(map(str, set(clave) - set(casos)))}")
    if problemas:
        print("ERROR de insumos: " + "; ".join(problemas), file=sys.stderr)
        sys.exit(2)
    ids = list(casos)
    pred = {i: evaluar(casos[i], manual) for i in ids}

    exacto = sum(pred[i] == clave[i] for i in ids)
    ver = [(clave[i][0], pred[i][0]) for i in ids]
    print(f"Casos: {len(ids)}")
    print(f"Acierto exacto (veredicto+regla): {exacto}/{len(ids)} = {exacto/len(ids):.1%}")
    print(f"Acierto de veredicto: {sum(a == b for a, b in ver)}/{len(ids)}   kappa = {kappa(ver):.3f}")
    m = Counter(ver)
    print("\nVeredicto      pred=falla  pred=aprueba")
    print(f"real=falla     {m[('falla','falla')]:>10}  {m[('falla','aprueba')]:>12}")
    print(f"real=aprueba   {m[('aprueba','falla')]:>10}  {m[('aprueba','aprueba')]:>12}")

    print("\nRegla          soporte  TP  FP  FN  precisión  recall")
    for r in REGLAS:
        tp = sum(clave[i][1] == r and pred[i][1] == r for i in ids)
        fp = sum(clave[i][1] != r and pred[i][1] == r for i in ids)
        fn = sum(clave[i][1] == r and pred[i][1] != r for i in ids)
        sop = tp + fn
        p = tp / (tp + fp) if tp + fp else None
        rc = tp / sop if sop else None
        print(f"{r:<14} {sop:>7} {tp:>3} {fp:>3} {fn:>3}  {fmt(p):>9}  {fmt(rc):>6}")

    malos = [i for i in ids if pred[i] != clave[i]]
    if malos:
        print("\nDesacuerdos:")
        for i in malos:
            det = evaluar_detalle(casos[i], manual)
            motivos = "; ".join(f"{r}: {d}" for r, (e, d) in det.items() if e == "falla")
            print(f"  {i}: clave={clave[i]} pred={pred[i]}  [{motivos or 'sin fallas detectadas'}]")


if __name__ == "__main__":
    main(*sys.argv[1:])
