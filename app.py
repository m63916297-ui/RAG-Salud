import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

try:
    from utils.zep_client import ZepHealthClient, get_zep_client
except ImportError:
    ZepHealthClient = None
    get_zep_client = None

try:
    from utils.patterns import PatternDetector
except ImportError:
    PatternDetector = None

try:
    from utils.alerts import AlertSystem
except ImportError:
    AlertSystem = None

load_dotenv()

st.set_page_config(
    page_title="SaludAI - Seguimiento de Salud",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00C896;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #888;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #00C89633;
    }
    .profile-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #00C89633;
        margin-bottom: 1rem;
    }
    .alert-critical {
        background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background: linear-gradient(135deg, #ffa502 0%, #ffbe76 100%);
        padding: 1rem;
        border-radius: 8px;
        color: #1a1a2e;
        margin: 0.5rem 0;
    }
    .stChatMessage {
        background: #262730;
        border-radius: 12px;
        padding: 1rem;
    }
    .treatment-box {
        background: #2d2d44;
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 4px solid #00C896;
        margin: 0.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "entries" not in st.session_state:
    st.session_state.entries = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "zep_client" not in st.session_state:
    st.session_state.zep_client = None
    if ZepHealthClient and get_zep_client:
        try:
            st.session_state.zep_client = get_zep_client()
        except Exception:
            st.session_state.zep_client = None

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "nombre": "",
        "edad": "",
        "correo": "",
        "examenes": "",
        "tratamiento": "",
    }

pattern_detector = PatternDetector() if PatternDetector else None
alert_system = AlertSystem() if AlertSystem else None


def extract_entry_data(user_input: str, profile: Dict) -> Dict:
    symptoms = []
    if pattern_detector:
        symptoms = pattern_detector.extract_symptoms(user_input)

    severity = "media"
    for entry in symptoms:
        if entry.get("severity"):
            severity = entry["severity"]
            break

    categories = [s["category"] for s in symptoms]

    return {
        "timestamp": datetime.now().isoformat(),
        "raw_text": user_input,
        "symptoms": symptoms,
        "category": categories[0] if categories else "general",
        "severity": severity,
        "nombre": profile.get("nombre", ""),
        "edad": profile.get("edad", ""),
        "correo": profile.get("correo", ""),
        "examenes": profile.get("examenes", ""),
        "tratamiento": profile.get("tratamiento", ""),
    }


def create_symptom_chart(entries: List[Dict]):
    if not entries or len(entries) < 2:
        return None

    categories = [e.get("category", "unknown") for e in entries]
    severities = [e.get("severity", "media") for e in entries]

    severity_map = {"alta": 3, "media": 2, "baja": 1}
    severity_scores = [severity_map.get(s, 2) for s in severities]

    timestamps = [datetime.fromisoformat(e["timestamp"]) for e in entries]

    fig = px.line(
        x=timestamps,
        y=severity_scores,
        color=categories,
        title="Tendencia de Síntomas",
        labels={"y": "Nivel de Severidad", "x": "Fecha"},
        markers=True,
    )
    fig.update_layout(
        template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def create_category_pie(entries: List[Dict]):
    if not entries:
        return None

    categories = [e.get("category", "unknown") for e in entries]
    category_counts = {}
    for cat in categories:
        category_counts[cat] = category_counts.get(cat, 0) + 1

    fig = px.pie(
        names=list(category_counts.keys()),
        values=list(category_counts.values()),
        title="Distribución de Síntomas",
        hole=0.4,
    )
    fig.update_layout(
        template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def create_treatment_timeline(entries: List[Dict]):
    if not entries:
        return None

    entries_with_treatment = [e for e in entries if e.get("tratamiento")]
    if not entries_with_treatment:
        return None

    timestamps = [
        datetime.fromisoformat(e["timestamp"]) for e in entries_with_treatment
    ]
    treatments = [
        e.get("tratamiento", "")[:50] + "..."
        if len(e.get("tratamiento", "")) > 50
        else e.get("tratamiento", "")
        for e in entries_with_treatment
    ]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=timestamps,
                y=[1] * len(timestamps),
                mode="markers+text",
                marker=dict(size=15, color="#00C896"),
                text=treatments,
                textposition="top center",
                textfont=dict(color="white"),
            )
        ]
    )

    fig.update_layout(
        title="Línea de Tiempo de Tratamientos",
        template="plotly_dark",
        height=200,
        showlegend=False,
        xaxis_title="Fecha",
        yaxis=dict(showticklabels=False, showgrid=False),
    )
    return fig


def render_alert(alert: Dict):
    level = alert.get("level", "warning")
    if level == "critical":
        st.markdown(
            f"""
        <div class="alert-critical">
            <strong>🚨 {alert.get("title", "Alerta")}</strong><br>
            {alert.get("message", "")}<br>
            <em>Acción recomendada: {alert.get("action", "Consulte a un profesional")}</em>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
        <div class="alert-warning">
            <strong>⚠️ {alert.get("title", "Advertencia")}</strong><br>
            {alert.get("message", "")}<br>
            <em>Acción recomendada: {alert.get("action", "Monitoree sus síntomas")}</em>
        </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    st.markdown('<h1 class="main-header">🏥 SaludAI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Seguimiento inteligente de salud con GraphRAG</p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("👤 Perfil del Paciente")

        with st.container():
            st.markdown('<div class="profile-card">', unsafe_allow_html=True)

            nombre = st.text_input(
                "📛 Nombre completo",
                value=st.session_state.user_profile.get("nombre", ""),
            )
            edad = st.text_input(
                "🎂 Edad", value=st.session_state.user_profile.get("edad", "")
            )
            correo = st.text_input(
                "📧 Correo electrónico",
                value=st.session_state.user_profile.get("correo", ""),
            )

            st.session_state.user_profile["nombre"] = nombre
            st.session_state.user_profile["edad"] = edad
            st.session_state.user_profile["correo"] = correo

            st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("📋 Estadísticas")
        total_entries = len(st.session_state.entries)
        st.metric("Total de entradas", total_entries)

        if total_entries > 0:
            unique_symptoms = len(
                set(e.get("category", "") for e in st.session_state.entries)
            )
            entries_with_treatment = sum(
                1 for e in st.session_state.entries if e.get("tratamiento")
            )
            st.metric("Categorías únicas", unique_symptoms)
            st.metric("Con tratamiento", entries_with_treatment)

        st.subheader("🔑 API Key")
        api_key_input = st.text_input(
            "Zep API Key",
            type="password",
            value=os.getenv("ZEP_API_KEY", ""),
            help="Obtén tu API key en getzep.com",
        )

        if api_key_input and api_key_input != os.getenv("ZEP_API_KEY"):
            os.environ["ZEP_API_KEY"] = api_key_input
            if ZepHealthClient:
                try:
                    st.session_state.zep_client = ZepHealthClient(api_key=api_key_input)
                    st.success("Conexión con Zep establecida")
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")

        st.subheader("📊 Puntuación de Salud")
        if total_entries > 0 and alert_system:
            health_score = alert_system.generate_health_score(st.session_state.entries)
            score = health_score["score"]

            if score >= 80:
                score_color = "#00C896"
            elif score >= 50:
                score_color = "#ffa502"
            else:
                score_color = "#ff4757"

            st.markdown(
                f"""
            <div class="metric-card">
                <h2 style="color: {score_color}; text-align: center; font-size: 3rem; margin: 0;">{score}</h2>
                <p style="text-align: center; color: #888;">{health_score["status"]}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Registra síntomas para ver tu puntuación")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Registrar Síntomas y Tratamiento")

        with st.form("symptom_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)

            with col_a:
                examenes = st.text_area(
                    "🧪 Exámenes realizados",
                    placeholder="Ej: Análisis de sangre, Radiografía torácica...",
                    height=100,
                )

            with col_b:
                tratamiento = st.text_area(
                    "💊 Tratamiento actual",
                    placeholder="Ej: Paracetamol 500mg cada 8 horas, Ibuprofeno...",
                    height=100,
                )

            sintomas = st.text_area(
                "🔍 Descripción de síntomas",
                placeholder="Describe tus síntomas en detalle...",
                height=120,
            )

            submitted = st.form_submit_button("Registrar", use_container_width=True)

            if submitted and sintomas:
                st.session_state.user_profile["examenes"] = examenes
                st.session_state.user_profile["tratamiento"] = tratamiento

                entry_data = extract_entry_data(sintomas, st.session_state.user_profile)
                st.session_state.entries.append(entry_data)

                st.success("✅ Registro guardado exitosamente")

                with st.chat_message("assistant", avatar="🤖"):
                    st.write("📝 **Registro Recibido**")
                    st.write(
                        f"**Paciente:** {st.session_state.user_profile.get('nombre', 'No especificado')}"
                    )
                    if st.session_state.user_profile.get("edad"):
                        st.write(
                            f"**Edad:** {st.session_state.user_profile['edad']} años"
                        )
                    st.write(f"\n**Síntomas:** {sintomas[:200]}...")

                    if examenes:
                        st.write(
                            f"\n**Exámenes:** {examenes[:100]}{'...' if len(examenes) > 100 else ''}"
                        )

                    if tratamiento:
                        st.write(
                            f"\n**Tratamiento:** {tratamiento[:100]}{'...' if len(tratamiento) > 100 else ''}"
                        )

                    alerts = {"has_alerts": False, "alerts": []}
                    if alert_system:
                        alerts = alert_system.check_symptoms(sintomas)
                        if alerts["has_alerts"]:
                            for alert in alerts["alerts"]:
                                render_alert(alert)

                    patterns = {"patterns": [], "insights": []}
                    if pattern_detector:
                        patterns = pattern_detector.detect_recurring_patterns(
                            st.session_state.entries
                        )
                        if patterns["insights"]:
                            st.write("\n**💡 Patrones detectados:**")
                            for insight in patterns["insights"][:2]:
                                st.write(f"- {insight}")

                    if st.session_state.zep_client:
                        try:
                            full_context = f"Paciente: {st.session_state.user_profile.get('nombre', '')}. "
                            full_context += f"Síntomas: {sintomas}. "
                            if examenes:
                                full_context += f"Exámenes: {examenes}. "
                            if tratamiento:
                                full_context += f"Tratamiento: {tratamiento}."
                            st.session_state.zep_client.add_symptom_entry(full_context)
                            st.info("📡 Sincronizado con GraphRAG (Zep)")
                        except Exception:
                            pass

        st.subheader("📈 Tendencias")
        if len(st.session_state.entries) >= 2:
            fig_trend = create_symptom_chart(st.session_state.entries)
            if fig_trend:
                st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Registra al menos 2 entradas para ver tendencias")

        st.subheader("🥧 Distribución de Síntomas")
        if st.session_state.entries:
            fig_pie = create_category_pie(st.session_state.entries)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("💊 Línea de Tiempo de Tratamientos")
        fig_timeline = create_treatment_timeline(st.session_state.entries)
        if fig_timeline:
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Agrega tratamientos para ver la línea de tiempo")

    with col2:
        st.subheader("🧠 GraphRAG - Red de Conocimiento")

        if st.session_state.entries:
            with st.expander("Ver red de síntomas-tratamientos"):
                categories = [
                    e.get("category", "unknown") for e in st.session_state.entries
                ]
                category_counts = {}
                for cat in categories:
                    category_counts[cat] = category_counts.get(cat, 0) + 1

                st.markdown("**📌 Síntomas registrados:**")
                for cat, count in category_counts.items():
                    st.write(f"- **{cat}**: {count} vez/veces")

                treatments = [
                    e.get("tratamiento", "")
                    for e in st.session_state.entries
                    if e.get("tratamiento")
                ]
                if treatments:
                    st.markdown("\n**💊 Tratamientos:**")
                    for i, t in enumerate(set(treatments), 1):
                        st.write(f"{i}. {t[:60]}{'...' if len(t) > 60 else ''}")

                examenes_list = [
                    e.get("examenes", "")
                    for e in st.session_state.entries
                    if e.get("examenes")
                ]
                if examenes_list:
                    st.markdown("\n**🧪 Exámenes:**")
                    for i, ex in enumerate(set(examenes_list), 1):
                        st.write(f"{i}. {ex[:60]}{'...' if len(ex) > 60 else ''}")

    st.subheader("📋 Historial Completo")
    if st.session_state.entries:
        for entry in reversed(st.session_state.entries[-10:]):
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime(
                "%d/%m/%Y %H:%M"
            )

            with st.expander(f"📌 {timestamp}"):
                if entry.get("nombre"):
                    st.write(f"**Paciente:** {entry['nombre']}")
                if entry.get("edad"):
                    st.write(f"**Edad:** {entry['edad']} años")
                if entry.get("correo"):
                    st.write(f"**Correo:** {entry['correo']}")

                st.write(f"\n**Síntomas:** {entry.get('raw_text', '')}")
                st.write(f"**Categoría:** {entry.get('category', 'general')}")
                st.write(f"**Severidad:** {entry.get('severity', 'media')}")

                if entry.get("examenes"):
                    st.markdown(
                        f"**🧪 Exámenes:**\n<div class='treatment-box'>{entry['examenes']}</div>",
                        unsafe_allow_html=True,
                    )

                if entry.get("tratamiento"):
                    st.markdown(
                        f"**💊 Tratamiento:**\n<div class='treatment-box'>{entry['tratamiento']}</div>",
                        unsafe_allow_html=True,
                    )

                if entry.get("symptoms"):
                    symptoms_list = [s["keyword"] for s in entry["symptoms"]]
                    st.write(f"**🔍 Síntomas detectados:** {', '.join(symptoms_list)}")
    else:
        st.info("Aún no hay entradas registradas. ¡Comienza registrando tus síntomas!")

    with st.expander("📊 Exportar Datos"):
        if st.session_state.entries:
            import json

            data_str = json.dumps(
                st.session_state.entries, indent=2, ensure_ascii=False
            )
            st.download_button(
                "Descargar JSON",
                data_str,
                file_name="saludai_registros.json",
                mime="application/json",
            )
        else:
            st.info("No hay datos para exportar")


if __name__ == "__main__":
    main()
