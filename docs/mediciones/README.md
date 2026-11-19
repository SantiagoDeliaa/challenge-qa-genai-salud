# Registro de mediciones

Cada número que cito sale de una corrida guardada en esta carpeta, con la versión del código que la produjo. El set retenido de cada etapa se mide **una vez, antes de ajustar**. Todo número posterior a un ajuste es de regresión, no de generalización.

| Fecha | Versión del evaluador | Set | Exacto | Kappa | Rol del número | Salida |
|---|---|---|---|---|---|---|
| 18/11 | v0, intermedia y **no versionada** | Retenido propio H001–H050 | 45/50 (90%) | 0,79 | Generalización, pero con supuestos compartidos (ver nota) | `2026-11-18_retenido_medicion_unica.txt` |
| 19/11 | v1, commit `2e0be2f`, publicado | Ciego de Codex X01–X40 | **24/40 (60%)** | **0,245** | **Generalización independiente** | `2026-11-19_ciego_codex_v1.txt` (reproducido con `git show 2e0be2f:evaluar.py`) |
| 19/11 | v2, rediseño | Ciego de Codex, clave adjudicada | 40/40 | 1,00 | Regresión: se ajustó contra este set | `python medir.py sintetico/revision_codex/oculto.jsonl sintetico/revision_codex/oculto_clave_adjudicada.csv` |
| 19/11 | v2 | Visibles, desarrollo, retenido, contraejemplos de Codex | 30/30 · 102/102 · 50/50 · 30/30 | 1,00 | Regresión | `python -m unittest discover -s tests` |
| 19/11 | v2, commit `21eac00`, publicado | **Ciego de Codex, ronda 2 (Y01–Y50)**, sesión nueva, sin leer código, spec ni sets previos | **37/50 (74%)** | **0,48** | **Generalización independiente de la versión publicada** | `2026-11-19_ciego_codex_ronda2_v2.txt` |
| 19/11 | v3 | Los seis sets, incluida la ronda 2 | 100% en todos | 1,00 | Regresión: se ajustó contra la ronda 2 | `python -m unittest discover -s tests` |

**Nota sobre el 90%.** El código que lo produjo no quedó en un commit, lo que es un error de trazabilidad que Codex detectó. El número es coherente con los cinco desacuerdos que documenté, pero el set retenido lo etiquetó un agente que había leído mi spec (`decisiones.md`). Por eso mide independencia **del código**, no **de mis supuestos**. El set de Codex no vio la spec, y la diferencia entre 90% y 60% es justamente el costo de esos supuestos compartidos.

**Tendencia.** En generalización independiente, v1 dio 60% y v2 dio 74%. Los errores también cambiaron de naturaleza: en v1 eran de diseño (palabras sin contexto); en v2 son paráfrasis no contempladas y diálogo fino. Para v3 no hay todavía un número independiente.

**Lección aplicada.** Ahora cada medición queda con la versión del código y su salida. La próxima estimación honesta exige un set nuevo, independiente de la spec, que nadie haya usado para ajustar.
