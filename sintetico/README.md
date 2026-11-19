# Sets de casos

| Carpeta / archivos | Quién lo escribió | Rol |
|---|---|---|
| `casos_sinteticos.jsonl`, `clave_sinteticos.csv`, `notas.csv` (S001–S102) | Agente Claude ciego al código, con la spec | Desarrollo |
| `holdout_*` (H001–H050) | El mismo agente, en una segunda tanda | Retenido de v0, medido una vez (90%); hoy es regresión |
| `revision_codex/oculto*` (X01–X40) | Codex, ciego al código **y a la spec** | Retenido de v1, medido una vez (60%); hoy es regresión |
| `revision_codex/repros_fase2.jsonl` (R01–R30) | Codex, después de leer el código | Contraejemplos. `repros_clave.csv` es el resultado esperado según su informe |
| `revision_codex/REVIEW_codex.md` | Codex | Su informe completo, sin editar. Las rutas `C:\review-codex\` son de su entorno |
| `revision_codex/ronda3/` (Z01–Z50) | Codex en otra sesión nueva, con la clave sellada por SHA-256 | Retenido de v3, medido una vez (90%); hoy es regresión |
| `revision_codex/ronda2/` (Y01–Y50) | Codex en una sesión nueva, ciego al código, a la spec y a los sets previos | Retenido de v2, medido una vez (74%); hoy es regresión. `MEDICION_codex.md` es su informe |

Etiquetas cambiadas en la adjudicación, con su motivo en `docs/proceso-ia.md`:
- S074: string frente a número.
- H033: cuenta trazable.
- X18: en `oculto_clave_adjudicada.csv` queda como falla y se conserva la clave original de Codex.
