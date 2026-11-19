# Sets sintéticos

Los generó y etiquetó **a ciegas** un agente separado, a partir de la consigna, el kit y `docs/decisiones.md`, sin acceso a `evaluar.py`.

| Archivos | Rol |
|---|---|
| `casos_sinteticos.jsonl`, `clave_sinteticos.csv`, `notas.csv` | Desarrollo (S001–S102). Se ajustó el evaluador contra este set |
| `holdout_casos.jsonl`, `holdout_clave.csv`, `holdout_notas.csv` | Retenido (H001–H050). Medido una sola vez antes de ajustar: 90% exacto, kappa 0,79 |

`notas*.csv` trae, para cada caso, la regla objetivo, la dificultad (obvio, borde o distractor) y la razón de la etiqueta. Única etiqueta cambiada en la adjudicación: S074 (ver `docs/proceso-ia.md`).
