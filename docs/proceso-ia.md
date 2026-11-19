# Cómo trabajé con IA (y cómo medí al evaluador)

## Roles

| Rol | Quién | Qué hizo |
|---|---|---|
| Dueño | Yo | Alcance, criterio ante lo ambiguo y aprobación de cada decisión |
| Arquitecto y revisor | Claude | Escribió la spec (`decisiones.md`), el evaluador y el medidor, y adjudicó los desacuerdos |
| Etiquetador ciego | Otro agente Claude | Generó y etiquetó 152 casos **sin acceso al código**: solo vio la consigna, el kit y la spec |
| Ejecutor | Claude Code | Verificó y subió el repo con un encargo cerrado |
| **Revisor cruzado** | **Codex (otro modelo, de otra familia)** | Hizo de evaluador del challenge. Escribió 40 casos a ciegas **solo desde la consigna**, sin la spec, y después revisó el código, el README y las mediciones |

## Por qué tres capas de casos

1. **Los 30 visibles son plantillas.** La primera versión sacó 30/30 de entrada, y eso no mide nada.
2. **El etiquetador ciego** comparte la spec, pero no el código. Detecta bugs de implementación: un evaluador que no se califica a sí mismo.
3. **El revisor de otra familia** no comparte ni el código ni la spec, ni el modelo base. Detecta los **supuestos** que el implementador y el etiquetador comparten sin saberlo. Es la capa que más se parece al set oculto.

## Qué mostró cada capa ([registro completo](mediciones/README.md))

| Etapa | Resultado | Qué reveló |
|---|---|---|
| Visibles, v0 | 30/30 | Nada (plantillas) |
| Desarrollo, v0 | 95/102 | 7 bugs de texto: negaciones lejanas, "suspendid**a**", "el de la tarde", "no pude…, pero hay turno" |
| Retenido propio, v0 | 45/50 (90%) | 5 bugs más: días con fecha, "el más temprano", "te puede ayudar" |
| **Ciego de Codex, v1** | **24/40 (60%), kappa 0,25** | **Un problema de diseño, no de casos sueltos** |
| **Ciego de Codex ronda 2, v2** | **37/50 (74%), kappa 0,48** | Paráfrasis no contempladas, diálogo fino y banderas rojas que el motor no marcó |

**El hallazgo de Codex.** Las reglas de texto detectaban **si aparecía una palabra**, no **qué se decía, a quién y cuándo**. Algunos ejemplos:
- un "no puedo" anulaba toda la oración ("No puedo medicarte, pero podés tomar loratadina" aprobaba);
- un turno inventado se justificaba con una búsqueda **posterior** de otra especialidad;
- el estado "activo" de una búsqueda posterior borraba la suspensión que había al momento de reservar;
- el "Plan Plus" de la solicitante se atribuía a un tercero buscado antes.

Coincido con la crítica: arreglarlo caso por caso habría sido seguir sobreajustando.

## El rediseño (v2)

Tres cambios estructurales, todos documentados en `decisiones.md` con la marca [rev. Codex]:
- **Análisis por cláusula**: la negación tiene alcance local.
- **Contexto temporal**: el estado, las opciones mostradas y el respaldo se toman al momento de cada turno, y el par día+hora tiene que salir de un mismo turno real.
- **Texto contra estructura**: los montos dichos se cruzan con lo afirmado, incluidos los formatos locales y los montos en palabras.

Además: robustez ante entradas rotas, CSV correcto, rendimiento lineal (20.000 turnos en 0,5 s) y validación de insumos en `medir.py`.

## Adjudicación de la revisión de Codex

- **Le di la razón** en 15 de los 16 desacuerdos del set ciego y en los 30 contraejemplos de la Fase 2.
- **No le di la razón en X18**: el intento de reservar para un afiliado suspendido es una falla de Ana, aunque el sistema la rechace (D4). Su clave original y la mía adjudicada están en `sintetico/revision_codex/`.
- **Cambié una decisión mía por su crítica**: ahora acepto las cuentas trazables (H033 y R25). Antes las rechazaba por literalidad.
- **Mi validación encontró un bug más**: mientras escribía los tests de regresión, una variante de X07 ("solo puedo decirte **que** le suspendieron…") mostró que esa frase se tomaba como negativa.

## Ronda 2: medir la versión publicada

Con la v2 subida, abrí una **sesión nueva de Codex** que no había leído el código, la spec ni los sets previos. Escribió 50 casos solo desde la consigna, cerró la clave (con hash) y corrió el script una vez: **74%**. Coincidí con su adjudicación en los 13 desacuerdos. Ninguno era de diseño; fueron:
- **paráfrasis**: "yo iría con", "media tableta", "sesenta días", "las cinco y veinticinco", "el del 21", "el próximo día hábil al cierre", "pasame su fecha de nacimiento";
- **conducta**: URGENCIA con "dentro de cuatro horas", y una negativa de cobertura sin cita;
- **diálogo**: confirmar que conoce la sede y postergar el horario no es confirmar el turno, y una repregunta legítima no tiene por qué informar nivel;
- **una capacidad que faltaba**: las banderas rojas en el texto del afiliado cuando el motor no las marca.

Los corregí con reglas generales (v3) y cada patrón quedó como test.

## Qué número creer

Los números honestos son los de generalización independiente: **60% (v1) → 74% (v2)**. El 100% actual sobre los seis sets es regresión. Para v3 no tengo un número independiente, y no lo voy a estimar: la cola de paráfrasis del texto libre es larga, y es justamente la parte que, en producción, le asignaría a un LLM-juez validado.

## Principios que apliqué (de mi experiencia evaluando agentes en producción)

- **Determinista donde se pueda.** El texto solo se usa donde no hay otra señal.
- **Tres estados por regla, con motivo.** Un error interno nunca se convierte en "aprueba" en silencio.
- **El acuerdo simple engaña.** Por eso se reportan precisión y recall por regla, y kappa.
- **Las etiquetas de un modelo no son la verdad.** Se adjudican contra la spec, y se registra quién se equivocaba: el evaluador, la etiqueta o la spec.
- **Un número sin la versión que lo produjo no es un dato.** Esta lección la aprendí en este mismo challenge.
- **Un evaluador de otra familia para el evaluador.** Los puntos ciegos compartidos solo aparecen con un revisor que no comparte el origen.
