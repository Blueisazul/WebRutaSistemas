
const canvas = document.getElementById("canvas");

if (!canvas) {
    throw new Error("No se encontró el elemento canvas#canvas.");
}

const gl = canvas.getContext("webgl2", { alpha: true, antialias: true });

if (!gl) {
    throw new Error("WebGL2 no es compatible con este navegador.");
}

// ============================================================================
// 1. VERTEX SHADER
// ============================================================================
const vertexShaderSource = `#version 300 es
      precision highp float;

      const float TAU = 6.28318530718;

      in float aU;
      in float aAngle;
      in float aArm;
      in float aRadius;
      in float aRegion;
      in float aSpeed;
      in vec3 aSeed;

      uniform float uTwist;
      uniform float uSpin;
      uniform float uTime;
      uniform mat4 uProjection;

      out float vU;
      out float vAlpha;
      out float vDepth;
      out float vRegion;

      vec3 getSpine(float u, float t) {
        float x = mix(-8.5, 8.5, u);
        float y = -1.55 
                + sin(u * 3.8 - 0.6 - t * 0.18) * 0.45 
                + cos(u * 2.0 + 0.3) * 0.25;
        float z = -6.2 
                + sin(u * 3.14159) * 1.45 
                + cos(u * 3.6 - t * 0.18) * 0.60;
        return vec3(x, y, z);
      }

      void main() {
        float u = fract(aU + uTime * aSpeed);

        vec3 spinePos = getSpine(u, uTime);
        vec3 nextPos  = getSpine(min(u + 0.008, 1.0), uTime);
        vec3 tangent  = normalize(nextPos - spinePos);

        vec3 worldUp = vec3(0.0, 1.0, 0.0);
        vec3 side    = normalize(cross(tangent, worldUp));
        vec3 normal  = cross(side, tangent);
        float armAngle = aArm * (TAU / 3.0);
        float longitudinalTwist = u * TAU * 2.4;
        float twistWave = (sin(u * TAU) * 0.45 + cos(u * TAU * 2.0) * 0.2) * uTwist;
        float spinAngle = uTime * uSpin;
        float vortexAngle = armAngle + aAngle + longitudinalTwist + twistWave + spinAngle;
        float envelope = 0.35 + sin(u * 3.14159) * 0.35;
        float strandRadius = (aRegion < 1.5) ? 0.95 : 1.85;
        float r = aRadius * strandRadius * envelope;
        float helixX = cos(vortexAngle) * r;
        float helixY = sin(vortexAngle) * r;
        float waveOffset = sin(u * 6.0 - uTime * 0.8 + aSeed.y * 6.28) * 0.08 * aRegion;
        vec3 microJitter = vec3(
        sin(uTime * 1.5 + aSeed.x * 35.0),
        cos(uTime * 1.3 + aSeed.y * 35.0),
        sin(uTime * 1.1 + aSeed.z * 35.0)
        ) * (0.015 + aRegion * 0.02);
        vec3 finalPos = spinePos
        + side * (helixX + waveOffset)
        + normal * helixY
        + microJitter;
        gl_Position = uProjection * vec4(finalPos, 1.0);
        float dist = max(1.2, -finalPos.z);
        vDepth = dist;
        float baseSize = (aRegion < 1.5) ? (14.0 + aSeed.x * 6.0) : (12.0 + aSeed.x * 6.0);
        gl_PointSize = clamp((baseSize / dist) * 1.8, 1.5, 34.0);
        vU = u;
        vRegion = aRegion;
        float edgeFade = smoothstep(0.0, 0.12, u) * smoothstep(1.0, 0.88, u);
        float depthFade = smoothstep(9.5, 4.2, dist);
        float regionAlpha = (aRegion < 1.5) ? 0.85 : 0.45;
        vAlpha = edgeFade * depthFade * regionAlpha;
        }
        `;
// ============================================================================
// 2. FRAGMENT SHADER (Armonizado con iceBlue, crystalBlue y arcticBlue)
// ============================================================================
const fragmentShaderSource = `#version 300 es
        precision highp float;
        in float vU;
        in float vAlpha;
        in float vDepth;
        in float vRegion;
        out vec4 fragColor;
        void main() {
        vec2 p = gl_PointCoord - 0.5;
        float d = length(p) * 2.0;
        if (d > 1.0) discard;
        vec3 iceBlue = vec3(0.396, 0.780, 0.949);      // #65C7F2
        vec3 crystalBlue  = vec3(0.161, 0.620, 0.859); // #299EDC
        vec3 arcticBlue  = vec3(0.090, 0.396, 0.710);  // #1765B5
        vec3 baseColor = mix(iceBlue, crystalBlue, smoothstep(0.20, 0.80, vU));
        if (vRegion >= 1.5) {
          baseColor = mix(baseColor, arcticBlue, 0.45);
        }
        float edge = fwidth(d);
        float circleAlpha = 1.0 - smoothstep(1.0 - edge * 1.5, 1.0, d);
        float finalAlpha = clamp(circleAlpha * vAlpha, 0.0, 1.0);
        fragColor = vec4(baseColor, finalAlpha);
        }
        `;
function compileShader(type, source) {
    const shader = gl.createShader(type);
    if (!shader) {
        throw new Error("No se pudo crear el shader WebGL2.");
    }
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        const info = gl.getShaderInfoLog(shader) || "sin información adicional";
        gl.deleteShader(shader);
        throw new Error(`Error al compilar shader WebGL2: ${info}`);
    }
    return shader;
}
const program = gl.createProgram();
if (!program) {
    throw new Error("No se pudo crear el programa WebGL2.");
}
gl.attachShader(
    program,
    compileShader(gl.VERTEX_SHADER, vertexShaderSource),
);
gl.attachShader(
    program,
    compileShader(gl.FRAGMENT_SHADER, fragmentShaderSource),
);
gl.linkProgram(program);
if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const info = gl.getProgramInfoLog(program) || "sin información adicional";
    gl.deleteProgram(program);
    throw new Error(`Error al enlazar shaders WebGL2: ${info}`);
}
gl.useProgram(program);
const uTwistLoc = gl.getUniformLocation(program, "uTwist");
const uSpinLoc = gl.getUniformLocation(program, "uSpin");
const uTimeLoc = gl.getUniformLocation(program, "uTime");
const uProjLoc = gl.getUniformLocation(program, "uProjection");
const TWIST = 1.8;
const SPIN = 0.22;
gl.uniform1f(uTwistLoc, TWIST);
gl.uniform1f(uSpinLoc, SPIN);

// ============================================================================
// 3. GENERACIÓN DE PARTÍCULAS
// ============================================================================
const numParticles = 14000;
const uData = new Float32Array(numParticles);
const angleData = new Float32Array(numParticles);
const armData = new Float32Array(numParticles);
const radiusData = new Float32Array(numParticles);
const regionData = new Float32Array(numParticles);
const speedData = new Float32Array(numParticles);
const seedData = new Float32Array(numParticles * 3);
for (let i = 0; i < numParticles; i++) {
    uData[i] = Math.random();
    armData[i] = i % 3;
    angleData[i] = (Math.random() - 0.5) * 1.2;
    const isCore = Math.random() < 0.75;
    if (isCore) {
        regionData[i] = 1.0;
        radiusData[i] = Math.pow(Math.random(), 0.8);
        speedData[i] = 0.016 + Math.random() * 0.006;
    } else {
        regionData[i] = 2.0;
        radiusData[i] = 0.5 + Math.random() * 0.5;
        speedData[i] = 0.012 + Math.random() * 0.01;
    }
    seedData[i * 3 + 0] = Math.random();
    seedData[i * 3 + 1] = Math.random();
    seedData[i * 3 + 2] = Math.random();
}
function bindAttribute(data, name, size) {
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(program, name);
    if (loc !== -1) {
        gl.enableVertexAttribArray(loc);
        gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
    }
}
bindAttribute(uData, "aU", 1);
bindAttribute(angleData, "aAngle", 1);
bindAttribute(armData, "aArm", 1);
bindAttribute(radiusData, "aRadius", 1);
bindAttribute(regionData, "aRegion", 1);
bindAttribute(speedData, "aSpeed", 1);
bindAttribute(seedData, "aSeed", 3);

// ============================================================================
// 4. PROYECCIÓN Y RESIZE (Blindado contra dimensiones 0x0)
// ============================================================================
let projScaleX = 1;
let projScaleY = 1;

function updateProjection() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const container = canvas.parentElement;
  if (!container) return;

  const { width, height } = container.getBoundingClientRect();

  if (width <= 0 || height <= 0) return;

  canvas.width = Math.floor(width * dpr);
  canvas.height = Math.floor(height * dpr);
  gl.viewport(0, 0, canvas.width, canvas.height);

  const aspect = canvas.width / canvas.height;
  const fov = (45 * Math.PI) / 180;
  const near = 0.1;
  const far = 100.0;
  const f = 1.0 / Math.tan(fov / 2);
  const nf = 1 / (near - far);
  projScaleX = f / aspect;
  projScaleY = f;

  const projMatrix = new Float32Array([
    projScaleX, 0, 0, 0,
    0, projScaleY, 0, 0,
    0, 0, (far + near) * nf, -1,
    0, 0, 2 * far * near * nf, 0,
  ]);

  gl.uniformMatrix4fv(uProjLoc, false, projMatrix);
}

// Observa cambios reales de tamaño del Hero (incluyendo cuando Tailwind termina de aplicar clases)
const resizeObserver = new ResizeObserver(() => updateProjection());
if (canvas.parentElement) {
    resizeObserver.observe(canvas.parentElement);
}
window.addEventListener("resize", updateProjection);
updateProjection();

gl.enable(gl.BLEND);
gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

// ============================================================================
// 5. CÁLCULO 3D Y NOTIFICACIONES
// ============================================================================
const TAU = Math.PI * 2;

function getSpineJS(u, t) {
    return {
        x: -8.5 + 17.0 * u,
        y: -1.55 + Math.sin(u * 3.8 - 0.6 - t * 0.18) * 0.45 + Math.cos(u * 2.0 + 0.3) * 0.25,
        z: -6.2 + Math.sin(u * Math.PI) * 1.45 + Math.cos(u * 3.6 - t * 0.18) * 0.6,
    };
}

function normalizeVec(v) {
    const len = Math.hypot(v.x, v.y, v.z) || 1;
    return { x: v.x / len, y: v.y / len, z: v.z / len };
}

function crossVec(a, b) {
    return {
        x: a.y * b.z - a.z * b.y,
        y: a.z * b.x - a.x * b.z,
        z: a.x * b.y - a.y * b.x,
    };
}

function smoothstep(edge0, edge1, x) {
    const t = Math.max(0, Math.min(1, (x - edge0) / (edge1 - edge0)));
    return t * t * (3 - 2 * t);
}

const worldUp = { x: 0, y: 1, z: 0 };

const flowAnchors = [
    { el: document.getElementById("anchor-0"), offset: 0.0, arm: 0, speed: 0.022, startU: 0.14, endU: 0.56 },
    { el: document.getElementById("anchor-1"), offset: 0.33, arm: 1, speed: 0.022, startU: 0.34, endU: 0.76 },
    { el: document.getElementById("anchor-2"), offset: 0.66, arm: 2, speed: 0.022, startU: 0.52, endU: 0.92 },
];

function updateFlowNodes(t) {
    const container = canvas.parentElement;
    if (!container) return;

    const { width, height } = container.getBoundingClientRect();
    if (width <= 0 || height <= 0) return;

    for (const node of flowAnchors) {
        if (!node.el) continue;

        const cycle = (node.offset + t * (node.speed / 0.42)) % 1.0;
        const u = node.startU + cycle * (node.endU - node.startU);

        const spinePos = getSpineJS(u, t);
        const nextPos = getSpineJS(Math.min(u + 0.008, 1.0), t);

        const tangent = normalizeVec({
            x: nextPos.x - spinePos.x,
            y: nextPos.y - spinePos.y,
            z: nextPos.z - spinePos.z,
        });

        const side = normalizeVec(crossVec(tangent, worldUp));
        const normal = crossVec(side, tangent);

        const armAngle = node.arm * (TAU / 3.0);
        const longitudinalTwist = u * TAU * 2.4;
        const twistWave = (Math.sin(u * TAU) * 0.45 + Math.cos(u * TAU * 2.0) * 0.2) * TWIST;
        const spinAngle = t * SPIN;
        const vortexAngle = armAngle + longitudinalTwist + twistWave + spinAngle;

        const envelope = 0.35 + Math.sin(u * Math.PI) * 0.35;
        const r = 0.8 * 0.95 * envelope;

        const helixX = Math.cos(vortexAngle) * r;
        const helixY = Math.sin(vortexAngle) * r;

        const worldX = spinePos.x + side.x * helixX + normal.x * helixY;
        const worldY = spinePos.y + side.y * helixX + normal.y * helixY;
        const worldZ = spinePos.z + side.z * helixX + normal.z * helixY;

        const clipX = worldX * projScaleX;
        const clipY = worldY * projScaleY;
        const clipW = -worldZ;

        const screenX = ((clipX / clipW) * 0.5 + 0.5) * width;
        const screenY = (1.0 - ((clipY / clipW) * 0.5 + 0.5)) * height;

        const fadeIn = smoothstep(0.0, 0.22, cycle);
        const fadeOut = smoothstep(1.0, 0.76, cycle);
        const opacity = fadeIn * fadeOut;

        if (cycle >= 0.46) {
            node.el.classList.add("is-checked");
        } else {
            node.el.classList.remove("is-checked");
        }

        const riseOffset = (1.0 - fadeIn) * 8.0;
        const scale = Math.max(0.84, Math.min(1.1, 5.8 / clipW));

        node.el.style.opacity = opacity.toFixed(3);
        node.el.style.transform = `translate3d(${screenX.toFixed(1)}px, ${(screenY + riseOffset).toFixed(1)}px, 0) scale(${scale.toFixed(3)})`;
    }
}

// ============================================================================
// 6. BUCLE DE RENDERIZADO
// ============================================================================
const startTime = performance.now();

function render(now) {
    const t = (now - startTime) * 0.001;

    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.uniform1f(uTimeLoc, t);
    gl.drawArrays(gl.POINTS, 0, numParticles);

    updateFlowNodes(t);
    requestAnimationFrame(render);
}

requestAnimationFrame(render);