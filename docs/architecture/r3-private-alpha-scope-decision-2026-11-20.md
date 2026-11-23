# DECISIÓN ARQUITECTÓNICA Y DE ALCANCE: ALPHA PRIVADA DE RUTA SISTEMAS
## Recalibración del Alcance, Criterios de Aceptación y Gobernanza de Producto

**Identificador:** `R3-02-PRIVATE-ALPHA-01`
**Fecha:** 20 de noviembre de 2026
**Autores/Roles:** Principal Software Architect, Technical Product Manager, Senior Software Engineer, Technical Auditor
**Rama objetivo:** `integration/r1-02c`
**Estado de gobernanza:** Aprobado para gobernanza de Alpha privada. R3-02 formal permanece `NOT_STARTED` / `PENDING_HUMAN`. R3-03 a R3-05 y R4 continúan estrictamente `BLOCKED`.

---

## 1. Objetivo y Premisa Fundamental de la Alpha Privada

La presente decisión recalibra la trayectoria inmediata del proyecto conforme a la intención estratégica del propietario:

> **Premisa de Producto:**
> **Ruta Sistemas será inicialmente una herramienta de uso personal del propietario y, de forma secundaria, para un grupo reducido de amigos y colegas cercanos. No está destinada todavía a un lanzamiento comercial abierto, operación como servicio SaaS multiusuario ni despliegue masivo en producción.**

El propósito de esta recalibración es evitar la **sobreingeniería prematura** (desarrollo de infraestructura, autenticación, persistencia compleja o automatizaciones desatendidas sin demanda comprobada), concentrando los esfuerzos en maximizar el valor práctico cotidiano: **encontrar, evaluar y verificar oportunidades laborales y formativas reales y confiables de Ingeniería de Sistemas en el Perú.**

---

## 2. Usuarios Previstos y Perfil de Uso

| Dimensión | Usuario Principal (Propietario) | Usuarios Secundarios (Círculo Cercano) | Audiencia Excluida en Esta Etapa |
|---|---|---|---|
| **Población** | 1 persona (propietario del repositorio). | 2 a 5 amigos, compañeros universitarios o colegas de TI. | Público general, postulantes anónimos masivos, reclutadores corporativos. |
| **Modalidad de acceso** | Ejecución local nativa (`python server.py`) en máquina propia. | Presencial (pantalla compartida) o clonado Git de rama `integration/r1-02c`. | Acceso web público vía dominio de producción o túneles de red. |
| **Objetivo de uso** | Descubrir vacantes reales verificadas, comparar condiciones objetivas y acceder al enlace oficial del empleador. | Exploración libre, retroalimentación cualitativa informal y prueba presencial. | Registro de cuentas, subida de currículums, postulaciones automáticas. |
| **Relación con el sistema** | Control total del código, entorno y base de datos local. | Confianza interpersonal, sin acuerdos de nivel de servicio (SLA). | Usuarios bajo contrato de términos y condiciones de servicio público. |

---

## 3. Alcance Funcional Actual de la Versión de Evaluación

La versión actual consolidada en la rama `integration/r1-02c` (commits `b3e69e9`, `4c88753`, `b27e418`) cuenta con:
1. **Catálogo normalizado Schema 2:** 6 registros gobernados (1 vacante real activa y 5 demostrativas).
2. **Oportunidad real verificada (`OP-005`):** *Supply Chain Analyst* en CookUnity (Lima, Perú), con enlace verificado al ATS Greenhouse y 21 campos de evidencia desglosada.
3. **Búsqueda y filtros multifaceta:** Búsqueda textual por tokens con atajo `/` y 7 filtros funcionales (modalidad, tipo de oportunidad, familia profesional, sector, nivel, salario publicado, condiciones temporales).
4. **Ficha de detalle en dos modalidades:** Modal accesible para consulta rápida y vista de página completa independiente (`/?id=OP-005` o `/#/oportunidad/OP-005`) con botón de retorno al catálogo.
5. **Transparencia y omisión estricta:** Erradicación del triaje especulativo; omisión estricta de salarios, modalidades o plazos no publicados; eliminación de frases predictivas subjetivas.
6. **Comparador lado a lado:** Evaluación tabular de 14 dimensiones objetivas entre dos oportunidades seleccionadas, sin puntuaciones globales sintéticas ni calificaciones arbitrarias.
7. **Servidor local nativo (`server.py`):** Servidor HTTP loopback en Python 3 estándar, seguro por diseño, con aislamiento de archivos privados y endpoint `/api/health`.
8. **Diseño responsivo:** Construido con Tailwind CSS v4.3.3 (`styles.css` minificado), sin dependencias en tiempo de ejecución ni desbordamiento horizontal en resoluciones de 360px a 1440px.

---

## 4. Dos Niveles de Madurez Independientes

Para evitar confusiones entre el uso informal personal y la validación de producto, se establecen dos niveles desacoplados:

```
┌────────────────────────────────────────────────────────────────────────┐
│ NIVEL 1: ALPHA PRIVADA (Uso personal y círculo cercano)                │
│ • Criterios técnicos de estabilidad, seguridad local y utilidad real. │
│ • Evaluación cualitativa informal mediante pruebas presenciales.      │
│ • Estado actual: OPERATIVA Y SEGURA (Validada en PREVIEW-02/03).      │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ Desbloqueo condicionado a
                                     │ evidencia formal y decisión
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│ NIVEL 2: PRODUCTO VALIDADO (Audiencia amplia / Producción pública)     │
│ • Sesiones formales R3-02 con 5-8 usuarios (P-EST, P-EGR, P-JUN).      │
│ • Consentimiento informado firmado, rúbricas QA y hallazgos R3-03.     │
│ • Estado actual: ESTRICTAMENTE BLOQUEADO (NOT_STARTED / PENDING_HUMAN) │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Criterios de Aceptación del Nivel 1 (Alpha Privada)

| Criterio de Alpha Privada | Estado Actual | Evidencia Técnica que lo Respalda |
|---|:---:|---|
| **1. Ejecución local reproducible** | **SATISFECHO** | `python server.py` arranca en <1s sin dependencias externas en Python 3.10+. |
| **2. Catálogo y funciones principales operativas** | **SATISFECHO** | 193 pruebas Python y 14 pruebas Playwright aprueban sin fallos. |
| **3. Distinción transparente real vs. demo** | **SATISFECHO** | Switch `#include-demonstrations` y badges claros (`Oportunidad activa · Verificada` vs `Demostración`). |
| **4. Procedencia verificable de datos** | **SATISFECHO** | Hero de fuente oficial + acordeón con 21 evidencias desglosadas en `OP-005`. |
| **5. Sin invención de datos desconocidos** | **SATISFECHO** | Omisión visual estricta de compensación, modalidad y deadline cuando no están publicados. |
| **6. Canal oficial de postulación operativo** | **SATISFECHO** | Botón directo a ATS Greenhouse (`https://boards.greenhouse.io/cookunity/jobs/8039990003`). |
| **7. Comparador objetivo sin puntajes inventados** | **SATISFECHO** | Comparador de 14 dimensiones con leyenda explícita «SIN PUNTUACIÓN». |
| **8. Protección de datos personales y archivos** | **SATISFECHO** | Sin almacenamiento de CVs ni datos privados. Servidor responde 404 a `/.git/config`. |
| **9. Servidor confinado a loopback** | **SATISFECHO** | Enlazado únicamente a `127.0.0.1:4173`. Validación de encabezado `Host`. |
| **10. Desarrollo aislado sin alterar producción** | **SATISFECHO** | Todo el trabajo avanza en `integration/r1-02c`; `main` y GitHub Pages permanecen intactos. |
| **11. Volumen útil de ofertas reales activas** | **PENDIENTE (LIMITACIÓN)** | **Actualmente existe solo 1 vacante real publicada (`OP-005`). Se requiere un segundo lote de 3 a 5 vacantes.** |

---

## 5. Evaluación Crítica de Funcionalidades y Matriz de Priorización

Se evalúa la cartera funcional frente a las necesidades reales del propietario:

| Funcionalidad Analizada | Clasificación para Alpha Privada | Justificación Técnica y de Producto |
|---|:---:|---|
| **1. Más oportunidades reales verificadas** | **NECESARIA PARA ALPHA PRIVADA (PRIORIDAD 1)** | Es la principal limitación actual. Con 1 sola oferta el catálogo no permite una búsqueda cotidiana útil. Ampliar a 4-6 vacantes reales de diversas subáreas de Sistemas transforma la herramienta en un producto de consulta genuino. |
| **2. Actualización y vigencia (TTL 7 días)** | **NECESARIA PARA ALPHA PRIVADA** | Ya implementada en `catalog_quality.py` y `server.py`. Evita que el usuario postule a convocatorias vencidas. |
| **3. Filtros y búsqueda multifaceta** | **ÚTIL, YA SATISFECHA** | Ya cubre texto, modalidad, nivel, tipo, sector y salario. No requiere más complejidad en esta etapa. |
| **4. Ficha de detalle y evidencias** | **ÚTIL, YA SATISFECHA** | Rediseñada y consolidada en UX-EXP-05/06 y PREVIEW-02. Satisface plenamente las necesidades de consulta. |
| **5. Comparador side-by-side** | **ÚTIL, YA SATISFECHA** | Funcional para 2 alternativas. Se mantiene sin alteraciones. |
| **6. Guardados y preferencias de usuario** | **REQUIERE EVIDENCIA DE USO / POSPONER** | Para un catálogo de escala Alpha, el usuario puede marcar la URL en su navegador (`?id=OP-005`). No justifica implementar almacenamiento local ni preferencias en esta etapa. |
| **7. Evaluación explicable de señales (R5)** | **POSPONER** | R5 está formalmente aplazada. Requiere un corpus de datos amplio y patrones longitudinales que aún no existen. |
| **8. Alertas por correo o notificaciones** | **NO JUSTIFICADA ACTUALMENTE** | Requiere servidores SMTP, colas de mensajería y persistencia de suscriptores. Innecesaria para uso personal. |
| **9. Automatización de fuentes (R4)** | **POSPONER / BLOQUEADA** | La ingesta asistida mediante el CLI offline existente (`collector/` y `scripts/editorial_cli.py`) es suficiente para el volumen de la Alpha. La automatización desatendida sin autorización institucional está bloqueada. |
| **10. Persistencia y almacenamiento** | **YA SATISFECHA** | El esquema híbrido actual (`data/opportunities.json` estático + `opportunities.sqlite3` en servidor local) es óptimo y soporta cientos de vacantes sin tocar código. |
| **11. Autenticación y multiusuario** | **NO JUSTIFICADA ACTUALMENTE** | Introducir login, contraseñas, tokens JWT y roles para uso de 1 persona y amigos es sobreingeniería pura y eleva el riesgo de vulnerabilidades. |
| **12. Recomendaciones personalizadas / IA** | **NO JUSTIFICADA ACTUALMENTE** | Un catálogo transparente no debe ocultar vacantes tras algoritmos opacos. La ordenación cronológica y por relevancia textual es superior y auditable. |

> [!IMPORTANT]
> **Conclusión de Prioridad:**
> La interfaz actual es suficiente y sólida. **El cuello de botella de valor de Ruta Sistemas hoy no es de código ni de diseño: es de inventario de vacantes reales.**

---

## 6. Arquitectura Suficiente para la Alpha Privada

La arquitectura actual es técnicamente adecuada para el uso previsto y no presenta bloqueos técnicos reales:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA ALPHA PRIVADA                      │
├────────────────────────────────────────────────────────────────────────┤
│ • Cliente Web: HTML5 Semántico + Tailwind CSS v4.3.3 + JS Vainilla.    │
│ • Servidor: Python 3.10+ ThreadingHTTPServer (Biblioteca Estándar).    │
│ • Enlace de Red: Loopback exclusivo 127.0.0.1:4173 (Seguro por diseño) │
│ • Almacenamiento Primario: data/opportunities.seed.json (Canónico).    │
│ • Cache / Búsqueda: SQLite FTS5 local (data/opportunities.sqlite3).     │
│ • Pipeline de Ingesta: scripts/editorial_cli.py (Offline / Asistido).  │
│ • Dependencias Runtime Nuevas: 0. Servicios SaaS Externos: 0.          │
└────────────────────────────────────────────────────────────────────────┘
```

### Decisiones de Arquitectura Confirmadas:
1. **Conservar `data/opportunities.seed.json` como fuente canónica:** Garantiza inmutabilidad y versionado Git puro.
2. **Conservar Schema 2 sin cambios:** El esquema actual modela adecuadamente fuentes, evidencias, estados de publicación y metadatos sin requerir migraciones.
3. **Mantener `server.py` como único runtime:** Desacoplado de frameworks pesados (Django, FastAPI, Express), minimizando superficie de ataque y mantenimiento.
4. **Mantener GitHub Pages desacoplado:** La versión pública en producción se conserva en el commit `28b7a9e` mientras la Alpha evoluciona de forma segura en `integration/r1-02c`.

---

## 7. Estrategia OSS-First y Control de Dependencias

- **No se requieren nuevas bibliotecas ni paquetes externos.**
- Las herramientas actuales (Python estándar, SQLite nativo, Tailwind CSS precompilado, Playwright para QA) cubren el 100% de los requerimientos de la Alpha privada.
- No se incorporarán librerías de analítica, frameworks de UI (React, Vue), ORMs pesados ni paquetes de autenticación.

---

## 8. Riesgos y Limitaciones de la Alpha Privada

1. **Riesgo de desinterés por catálogo reducido:** Si el propietario o sus amigos abren la web repetidamente y solo encuentran 1 vacante real, la herramienta perderá utilidad percibida.
2. **Vigencia de la oferta real:** `OP-005` (CookUnity) tiene un TTL de 7 días. Si la empresa retira la vacante de Greenhouse, el catálogo quedará sin vacantes activas.
3. **Límite de distribución:** Si los amigos no tienen entorno Python/Git, dependen exclusivamente de la visualización presencial o compartiendo pantalla con el propietario.
4. **Tentación de sobreingeniería:** Riesgo de volver a iterar sobre la UI antes de contar con un catálogo real representativo.

---

## 9. Dependencias que Permanecen Formalmente Bloqueadas

Esta decisión de Alpha privada no elude las reglas de calidad ni los gates de gobernanza:

- **Investigación Formal R3-02 (`NOT_STARTED` / `PENDING_HUMAN`):** La evaluación informal del círculo cercano (`OWNER-FEEDBACK-01`) no cuenta como sesión formal. R3-02 continúa requiriendo 5 a 8 participantes protocolizados con consentimiento informado cuando el proyecto decida abrirse a audiencias externas.
- **R3-03 (Consolidación formal de hallazgos):** Permanece **`BLOCKED`** hasta la culminación formal de R3-02.
- **R3-04 (Refactor UX formal):** Permanece **`BLOCKED`**.
- **R3-05 (Decisión de MVP):** Permanece **`BLOCKED`**.
- **R4 (Automatización de fuentes):** Permanece **`BLOCKED`** hasta justificar demanda de volumen y contar con autorización institucional.
- **R5 (Evaluación explicable):** Permanece **`APLAZADA`**.

---

## 10. Próxima Acción Recomendada (Paso Único de Mayor Impacto)

Se recomienda enfocar el siguiente esfuerzo técnico en:

> **Bloque Recomendado: Ingesta Curada de Oportunidades Reales para la Alpha Privada (`R2-A-06` o `R3-ALPHA-CURATION-01`)**
> **Objetivo:** Incorporar de 3 a 5 vacantes reales adicionales de Ingeniería de Sistemas / TI en Lima o Remoto para Perú (p. ej. en Desarrollo de Software, QA Testing, Cloud/DevOps o Datos) utilizando el pipeline offline ya desarrollado en R2-OSS (`collector/` y `scripts/editorial_cli.py`).
> **Justificación:** Es la única acción que transforma la Alpha privada en una herramienta de consulta verdaderamente útil para el propietario y sus amigos, superando la limitación del catálogo monovacante actual sin alterar la arquitectura ni agregar dependencias.
