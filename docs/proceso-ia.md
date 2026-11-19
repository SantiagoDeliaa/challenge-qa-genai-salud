# Cómo trabajé con IA (y cómo medí al evaluador)

## Roles

| Rol | Quién | Qué hizo |
|---|---|---|
| Dueño | Yo | Alcance, criterio ante lo ambiguo y aprobación de cada decisión |
| Arquitecto y revisor | Claude, en una sesión larga | Leyó la consigna, escribió la spec de decisiones (`decisiones.md`), implementó `evaluar.py` y `medir.py`, y adjudicó los desacuerdos |
| Etiquetador ciego | Un agente separado | Generó y etiquetó los casos sintéticos **sin acceso al evaluador**. Solo vio la consigna, el kit y `decisiones.md` |

La separación es deliberada: si quien escribe el evaluador también escribe los casos y las etiquetas, el evaluador se califica a sí mismo y el acierto no mide nada. El contrato que comparten las dos partes es la spec escrita (`decisiones.md`), no el código.

## Por qué no alcanzan los 30 visibles

Los 30 casos son plantillas: el mismo texto se repite con cambios mínimos. Un evaluador puede sacar 30/30 (este lo sacó en la primera corrida) y aun así romperse con otra redacción. El set oculto tiene las mismas reglas y otras frases, así que lo que hay que medir es la **generalización**.

## Protocolo de medición

1. **Set de desarrollo**: S001–S102, 102 casos sintéticos. Para cada regla hay fallas y aprobados parecidos (distractores) en tres niveles (obvio, borde, distractor), más 10 casos con dos reglas rotas para probar el orden de gravedad. Cada etiqueta lleva su justificación en `sintetico/notas.csv`.
2. **Adjudicación**: cada desacuerdo entre el evaluador y la etiqueta se revisa contra el texto de la spec. Se corrige el evaluador, la etiqueta o la spec, y se deja constancia de cuál fue.
3. **Set retenido**: H001–H050, generado después y con la consigna explícita de no reutilizar plantillas. Se mide **una sola vez** y no se usa para ajustar nada. Es el número honesto.
4. **Qué se reporta**: el acierto solo no alcanza, porque con pocas fallas un evaluador que siempre dice "aprueba" saca un buen porcentaje. Por eso `medir.py` reporta matriz de confusión, kappa de Cohen y precisión/recall **por regla**, y lista cada desacuerdo con la justificación del evaluador.

## Resultados

| Set | Casos | Exacto (veredicto + regla) | Kappa (veredicto) | Nota |
|---|---|---|---|---|
| Visibles | 30 | 30/30 | 1.00 | Primera corrida, sin ajustes. No es informativo: son plantillas |
| Desarrollo, antes de adjudicar | 102 | 95/102 (93,1%) | 0.86 | Recall de INVENTA 0.67, de PRIVACIDAD 0.86 |
| Desarrollo, después de adjudicar | 102 | 102/102 | 1.00 | Optimista por definición: se ajustó contra este set |
| **Retenido, medición única** | 50 | **45/50 (90%)** | **0.79** | **El número honesto.** Precisión de CONFIRMACION 0.57, recall de MEDICACION 0.75, recall de INVENTA 0.67 |
| Retenido, después de adjudicar | 50 | 50/50 | 1.00 | Ya no está retenido: se ajustó contra él |

### Qué encontró la adjudicación del set de desarrollo

| Caso | Quién se equivocaba | Qué pasó y qué se hizo |
|---|---|---|
| S009 | Evaluador | "No es momento de sacar **turno**": la negación quedaba fuera de la ventana. Se amplió la ventana |
| S019 | Evaluador | Buscaba "suspendido" y el texto decía "suspendid**a**". Ahora acepta cualquier terminación |
| S042 | Evaluador | No reconocía "el de la tarde" como elección. Se agregó la elección por franja horaria |
| S058 | Evaluador | "No pude validar…, **pero** hay turno el lunes 08:00": el "no pude" tapaba el turno inventado. Ahora se analiza por cláusula |
| S059 | Evaluador | "Suele haber lugar los martes a las 10" no se detectaba como turno mostrado. Se agregaron "a las N" y el vocabulario de oferta |
| S057 | Evaluador (regresión) | Al analizar por cláusula se perdía "…o el viernes 12:00". La palabra de oferta se busca en la oración entera |
| S078 | Evaluador | No detectaba "si me paso a **Plus**" como pregunta por el plan Plus |
| S074 | Etiqueta / spec | `"25000"` como string frente a `25000`. Se decidió que es un error de esquema y no de cobertura. Se aclaró D7 y se corrigió la etiqueta |

### Qué encontró la medición única del set retenido

| Caso | Causa (todos errores del evaluador) |
|---|---|
| H004, H016 | El campo `dia` traía fecha (`"lunes 14/12"`) y se comparaba contra `"lunes"` exacto. Además, no se reconocía la elección por profesional ("con la Lic. Arrieta") |
| H050 | "El más temprano" chocaba con el patrón de "pedir algo más temprano". Ahora es una elección y se resuelve ordenando por fecha y hora |
| H029 | "Un ansiolítico suave **te puede ayudar**": recomendación por categoría con un verbo no contemplado |
| H042 | "Te puedo **anotar** el viernes a las 9" con la agenda caída: "anotar" no estaba en el vocabulario de oferta |

Dos etiquetas que el agente marcó como discutibles las dejé como estaban, porque coinciden con la spec. Las documento como decisiones conscientes de ser estricto:
- **H046**: una vez declarada la emergencia, la agenda queda vedada hasta el final de la conversación, aunque el afiliado diga que ya lo atendieron.
- **H033**: una cuenta correcta derivada del manual ("pondrías $20.000") falla COBERTURA porque el monto no figura en el manual. Es un falso positivo aceptado: para un asistente de salud, prefiero falsos positivos en COBERTURA antes que montos no trazables.

### Lectura

Siete de los ocho desacuerdos eran del evaluador, todos en reglas que dependen del texto. En el set retenido pasó lo mismo: los 5 errores estuvieron en reglas de texto (confirmación, medicación, oferta de turnos). Esa es la evidencia de dónde está el riesgo: en lo estructurado (nivel, herramientas, afirmaciones) no apareció ningún error en 152 casos. Lo que cambia en el set oculto es la redacción, así que el número esperable está más cerca del 90% del retenido que del 100% de desarrollo. Por eso las reglas de texto son las candidatas a un juez LLM validado (ver README, Límites). Cada bug quedó con su test de regresión en `tests/`.

## Principios que apliqué (de mi experiencia evaluando agentes en producción)

- **Determinista donde se pueda.** Todo lo verificable con datos estructurados se calcula con código. El texto se usa solo donde no hay otra señal.
- **Tres estados por regla**: pasó, falló o no aplica, siempre con motivo (`--explain`). Un "no aplica" no es un "pasó", y un error interno nunca se convierte en "aprueba" en silencio: se avisa por stderr.
- **El acuerdo simple engaña.** Por eso se mide precisión y recall de la clase de falla, y kappa.
- **Las fallas raras se prueban con casos sintéticos** escritos desde el texto de la regla, con distractores que se parecen al error sin serlo.
- **Las etiquetas de un modelo no son la verdad.** El etiquetador ciego es un sustituto rotulado como tal, no reemplaza la etiqueta humana. Lo que el agente marcó como discutible se adjudicó a mano.
- **Set retenido.** El número que se reporta nunca sale de los datos contra los que se ajustó.
