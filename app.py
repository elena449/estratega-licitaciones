import streamlit as st
import google.generativeai as genai
import os
import tempfile
from pathlib import Path
import time

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Estratega de Licitaciones · Chakakuna",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --chakakuna-dark: #1a1a2e;
    --chakakuna-mid: #16213e;
    --chakakuna-accent: #e8643c;
    --chakakuna-light: #f5f0ea;
    --chakakuna-muted: #8a8a9a;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background-color: #f8f6f2; }

h1, h2, h3 { font-family: 'DM Serif Display', serif; }

/* Header */
.app-header {
    background: var(--chakakuna-dark);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.app-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    margin: 0;
    color: white;
}
.app-header p {
    font-size: 0.85rem;
    color: #aaa;
    margin: 0;
}
.accent-dot { color: var(--chakakuna-accent); }

/* Cards */
.section-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--chakakuna-accent);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.section-card h3 {
    color: var(--chakakuna-dark);
    font-size: 1rem;
    margin-bottom: 0.5rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.8rem;
}

/* Status badges */
.badge-ok {
    background: #d4edda; color: #155724;
    padding: 2px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600;
}
.badge-warn {
    background: #fff3cd; color: #856404;
    padding: 2px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--chakakuna-dark) !important;
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stFileUploader label { color: #ccc !important; }

/* Buttons */
.stButton > button {
    background: var(--chakakuna-accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button:hover {
    background: #c9522a !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(232,100,60,0.3) !important;
}

/* Report output */
.report-output {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.08);
    line-height: 1.7;
}

/* Chat messages */
.chat-user {
    background: var(--chakakuna-dark);
    color: white;
    padding: 0.8rem 1.2rem;
    border-radius: 12px 12px 4px 12px;
    margin: 0.5rem 0 0.5rem 3rem;
    font-size: 0.9rem;
}
.chat-agent {
    background: white;
    border: 1px solid #e8e8e8;
    padding: 0.8rem 1.2rem;
    border-radius: 12px 12px 12px 4px;
    margin: 0.5rem 3rem 0.5rem 0;
    font-size: 0.9rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* Divider */
.section-divider {
    border: none;
    border-top: 2px solid #f0ece6;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─── System Prompt ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres el "Estratega de Licitaciones y New Business" de Chakakuna, una consultora de investigación, diseño e innovación basada en Lima, Perú. Tu función es analizar Términos de Referencia (TdR) y encontrar el "match" perfecto con la experiencia histórica de la empresa almacenada en tu base de datos de proyectos.

Tus Fuentes de Información:
1. Base de Datos Permanente (Knowledge Base): Los archivos de proyectos pasados que te han sido compartidos, con metodologías, poblaciones atendidas y resultados.
2. Documento de Entrada: El archivo PDF de Términos de Referencia (TdR) cargado por el usuario.

Tu Misión: Al recibir un TdR, debes procesar la información y generar automáticamente un Informe de Viabilidad y Propuesta con la siguiente estructura EXACTA:

---

## 🎯 INFORME DE VIABILIDAD — [TÍTULO DEL TdR]

### 1. Propuesta de Valor y Expertise
Explica cómo la trayectoria general de Chakakuna se alinea con los desafíos específicos de este TdR. Identifica los pilares de identidad que nos hacen el postulante ideal.

### 2. Análisis de Similitud — Proyectos Más Relevantes
Selecciona los **3 proyectos más relevantes** de la base de datos. Para cada uno:

**Proyecto 1: [Nombre]**
- 🔧 Similitud Metodológica: [herramientas/procesos que este TdR solicita]
- 👥 Población Objetivo: [cómo nuestra experiencia con esa población se replica]
- 🎯 Objetivos Alineados: [metas logradas que garantizan el éxito]

(Repite para Proyecto 2 y Proyecto 3)

### 3. Recomendaciones Estratégicas y Propuesta
- Valor agregado o innovación que podemos proponer para este TdR
- Riesgos identificados en el TdR y cómo los mitigamos con experiencia previa

---

Directrices de Interacción:
- Tras entregar el informe inicial, responde preguntas del equipo sobre la base de datos y el TdR.
- REGLA DE ORO: Si la información no está en la base de datos o en el TdR, dilo claramente. NUNCA inventes experiencia no documentada.
- Mantén siempre un tono profesional y analítico.
- Responde siempre en español."""

# ─── Session state init ──────────────────────────────────────────────────────
if "kb_files" not in st.session_state:
    st.session_state.kb_files = []          # list of (name, bytes)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []      # list of {"role": ..., "content": ...}
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False
if "current_report" not in st.session_state:
    st.session_state.current_report = ""
if "tdr_name" not in st.session_state:
    st.session_state.tdr_name = ""

# ─── Helper: configure Gemini ────────────────────────────────────────────────
def get_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )

def upload_pdf_to_gemini(pdf_bytes: bytes, filename: str) -> genai.types.File:
    """Upload a PDF to Gemini Files API and return the file object."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    try:
        uploaded = genai.upload_file(tmp_path, mime_type="application/pdf", display_name=filename)
        # Wait for processing
        while uploaded.state.name == "PROCESSING":
            time.sleep(1)
            uploaded = genai.get_file(uploaded.name)
        return uploaded
    finally:
        os.unlink(tmp_path)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    api_key = st.text_input(
        "API Key de Gemini",
        type="password",
        help="Obtén tu key en aistudio.google.com/apikey"
    )

    st.markdown("---")
    st.markdown("### 🗂️ Base de Datos de Proyectos")
    st.caption("Sube aquí los PDFs de proyectos pasados de Chakakuna. Se mantienen durante toda la sesión.")

    kb_uploader = st.file_uploader(
        "Agregar proyectos a la base de datos",
        type="pdf",
        accept_multiple_files=True,
        key="kb_uploader",
        label_visibility="collapsed"
    )

    if kb_uploader:
        existing_names = {f[0] for f in st.session_state.kb_files}
        for f in kb_uploader:
            if f.name not in existing_names:
                st.session_state.kb_files.append((f.name, f.read()))
                existing_names.add(f.name)

    if st.session_state.kb_files:
        st.markdown(f"**{len(st.session_state.kb_files)} proyecto(s) cargado(s):**")
        for name, _ in st.session_state.kb_files:
            st.markdown(f"✅ {name[:35]}{'...' if len(name)>35 else ''}")
        if st.button("🗑️ Limpiar base de datos", use_container_width=True):
            st.session_state.kb_files = []
            st.session_state.report_generated = False
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.info("Aún no hay proyectos cargados.")

    st.markdown("---")
    st.caption("Chakakuna · Estratega de Licitaciones v1.0")

# ─── Main header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div>
        <h1>Estratega de Licitaciones<span class="accent-dot">.</span></h1>
        <p>Chakakuna · Análisis de TdR y matching con experiencia histórica</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Status bar ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    if api_key:
        st.markdown('<span class="badge-ok">✓ API Key configurada</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-warn">⚠ Sin API Key</span>', unsafe_allow_html=True)
with col2:
    n = len(st.session_state.kb_files)
    if n > 0:
        st.markdown(f'<span class="badge-ok">✓ {n} proyecto(s) en base de datos</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-warn">⚠ Base de datos vacía</span>', unsafe_allow_html=True)
with col3:
    if st.session_state.report_generated:
        st.markdown(f'<span class="badge-ok">✓ TdR analizado: {st.session_state.tdr_name[:25]}</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-warn">⚠ Sin TdR activo</span>', unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ─── Main area ───────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📄 Analizar TdR", "💬 Chat con el Agente"])

# ── TAB 1: Analyze TdR ───────────────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([1, 1.6], gap="large")

    with col_left:
        st.markdown("#### Subir Términos de Referencia")
        st.caption("Sube el PDF del TdR que deseas analizar contra la base de datos de proyectos.")

        tdr_file = st.file_uploader(
            "Seleccionar TdR (PDF)",
            type="pdf",
            key="tdr_uploader",
            label_visibility="collapsed"
        )

        if tdr_file:
            st.success(f"📎 **{tdr_file.name}** listo para analizar")

        st.markdown("---")

        ready = api_key and tdr_file and len(st.session_state.kb_files) > 0
        if not ready:
            missing = []
            if not api_key: missing.append("API Key")
            if not tdr_file: missing.append("TdR PDF")
            if not st.session_state.kb_files: missing.append("proyectos en base de datos")
            st.warning(f"Falta: {', '.join(missing)}")

        analyze_btn = st.button("🔍 Generar Informe de Viabilidad", disabled=not ready, use_container_width=True)

    with col_right:
        if analyze_btn and ready:
            with st.spinner("Analizando TdR contra base de datos de proyectos..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name="gemini-2.0-flash",
                        system_instruction=SYSTEM_PROMPT,
                    )

                    # Upload all files to Gemini
                    uploaded_files = []

                    # Upload knowledge base
                    with st.status("Procesando base de datos de proyectos...", expanded=False) as status:
                        for fname, fbytes in st.session_state.kb_files:
                            status.update(label=f"Subiendo: {fname}")
                            uf = upload_pdf_to_gemini(fbytes, fname)
                            uploaded_files.append(uf)
                        status.update(label="Base de datos procesada ✓", state="complete")

                    # Upload TdR
                    tdr_bytes = tdr_file.read()
                    tdr_uploaded = upload_pdf_to_gemini(tdr_bytes, tdr_file.name)

                    # Build prompt
                    contents = uploaded_files + [tdr_uploaded] + [
                        f"\nLos archivos anteriores ({len(st.session_state.kb_files)} documentos) son la BASE DE DATOS DE PROYECTOS de Chakakuna. "
                        f"El último archivo ({tdr_file.name}) es el TdR a analizar. "
                        f"Por favor genera el Informe de Viabilidad completo con las 3 secciones."
                    ]

                    response = model.generate_content(contents)
                    report = response.text

                    st.session_state.current_report = report
                    st.session_state.report_generated = True
                    st.session_state.tdr_name = tdr_file.name
                    # Seed chat with context
                    st.session_state.chat_history = [
                        {"role": "user", "content": f"[CONTEXTO INTERNO: Se ha analizado el TdR '{tdr_file.name}' contra {len(st.session_state.kb_files)} proyectos. El informe fue generado.]"},
                        {"role": "model", "content": report}
                    ]

                except Exception as e:
                    st.error(f"Error al procesar: {str(e)}")

        if st.session_state.report_generated:
            st.markdown('<div class="report-output">', unsafe_allow_html=True)
            st.markdown(st.session_state.current_report)
            st.markdown('</div>', unsafe_allow_html=True)

            st.download_button(
                "⬇️ Descargar informe (.md)",
                data=st.session_state.current_report,
                file_name=f"informe_{st.session_state.tdr_name.replace('.pdf','')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        elif not analyze_btn:
            st.markdown("""
            <div style="background:#f8f6f2;border-radius:12px;padding:3rem;text-align:center;color:#aaa;">
                <div style="font-size:3rem;margin-bottom:1rem;">📋</div>
                <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:#666;">
                    El informe aparecerá aquí
                </div>
                <div style="font-size:0.85rem;margin-top:0.5rem;">
                    Sube los proyectos en el panel izquierdo, luego sube el TdR y haz clic en Analizar
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── TAB 2: Chat ───────────────────────────────────────────────────────────────
with tab2:
    if not st.session_state.report_generated:
        st.info("💡 Primero genera un informe en la pestaña **Analizar TdR** para activar el chat con el agente.")
    else:
        st.caption(f"Chat activo · TdR: **{st.session_state.tdr_name}** · {len(st.session_state.kb_files)} proyectos en contexto")

        # Display chat history (skip the seed message)
        display_history = st.session_state.chat_history[2:] if len(st.session_state.chat_history) >= 2 else []

        if not display_history:
            st.markdown("""
            <div style="background:#f8f6f2;border-radius:8px;padding:1.5rem;text-align:center;color:#888;margin:1rem 0;">
                El informe ya fue generado. Puedes hacerme preguntas como:<br><br>
                <em>"¿Tenemos experiencia en la región Cajamarca?"</em><br>
                <em>"¿Qué presupuesto manejamos en proyectos similares?"</em><br>
                <em>"¿Hemos trabajado con poblaciones migrantes?"</em>
            </div>
            """, unsafe_allow_html=True)

        for msg in display_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">🙋 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-agent">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Escribe tu pregunta...",
                placeholder="Ej: ¿Tenemos experiencia trabajando con jóvenes en Lima Norte?",
                label_visibility="collapsed"
            )
            send = st.form_submit_button("Enviar →", use_container_width=True)

        if send and user_input and api_key:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.spinner("Consultando al agente..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name="gemini-2.0-flash",
                        system_instruction=SYSTEM_PROMPT,
                    )
                    # Build history for Gemini (role must be user/model)
                    gemini_history = [
                        {"role": h["role"], "parts": [h["content"]]}
                        for h in st.session_state.chat_history[:-1]
                    ]
                    chat = model.start_chat(history=gemini_history)
                    response = chat.send_message(user_input)
                    assistant_reply = response.text
                    st.session_state.chat_history.append({"role": "model", "content": assistant_reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
