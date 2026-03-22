import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict
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
    page_title="SaludAI - Seguimiento de Síntomas",
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

pattern_detector = PatternDetector() if PatternDetector else None
alert_system = AlertSystem() if AlertSystem else None


def extract_entry_data(user_input: str) -> Dict:
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
    }


def create_symptom_chart(entries: List[Dict]):
    if not entries:
        return None

    categories = [e.get("category", "unknown") for e in entries]
    severities = [e.get("severity", "media") for e in entries]

    severity_map = {"alta": 3, "media": 2, "baja": 1}
    severity_scores = [severity_map.get(s, 2) for s in severities]

    timestamps = [datetime.fromisoformat(e["timestamp"]) for e in entries]

    df = {"Fecha": timestamps, "Categoría": categories, "Severidad": severity_scores}

    fig = px.line(
        x=df["Fecha"],
        y=df["Severidad"],
        color=df["Categoría"],
        title="Tendencia de Síntomas",
        labels={"y": "Nivel de Severidad", "x": "Fecha"},
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
        '<p class="sub-header">Seguimiento inteligente de síntomas con GraphRAG</p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Configuración")

        st.subheader("📋 Estadísticas")
        total_entries = len(st.session_state.entries)
        st.metric("Total de entradas", total_entries)

        if total_entries > 0:
            unique_symptoms = len(
                set(e.get("category", "") for e in st.session_state.entries)
            )
            st.metric("Categorías únicas", unique_symptoms)

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
        st.subheader("💬 Chat de Síntomas")

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write(msg["content"])

        if prompt := st.chat_input("Describe tus síntomas...", key="symptom_input"):
            with st.chat_message("user", avatar="👤"):
                st.write(prompt)

            st.session_state.chat_history.append({"role": "user", "content": prompt})

            entry_data = extract_entry_data(prompt)
            st.session_state.entries.append(entry_data)

            alerts = {"has_alerts": False, "alerts": []}
            if alert_system:
                alerts = alert_system.check_symptoms(prompt)
                if alerts["has_alerts"]:
                    for alert in alerts["alerts"]:
                        render_alert(alert)

            patterns = {"patterns": [], "insights": []}
            pattern_alerts = []
            if pattern_detector:
                patterns = pattern_detector.detect_recurring_patterns(
                    st.session_state.entries
                )
                pattern_alerts = pattern_detector.generate_alerts(patterns)

            for alert in pattern_alerts:
                render_alert(alert)

            response = f"📝 **Resumen registrado**\n\n"
            response += f"Síntomas detectados: {', '.join([s['keyword'] for s in entry_data['symptoms']]) if entry_data['symptoms'] else 'Ninguno específico'}\n\n"

            if entry_data["symptoms"]:
                response += f"Categoría: {entry_data['category']}\n"
                response += f"Severidad: {entry_data['severity']}\n"
                response += f"Duración: {entry_data['symptoms'][0].get('duration', 'no especificada')}\n\n"

            if patterns["insights"]:
                response += "💡 **Patrones detectados:**\n"
                for insight in patterns["insights"][:2]:
                    response += f"- {insight}\n"

            with st.chat_message("assistant", avatar="🤖"):
                st.write(response)

            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

            if st.session_state.zep_client:
                try:
                    st.session_state.zep_client.add_symptom_entry(prompt)
                except Exception as e:
                    st.warning(f"No se pudo guardar en Zep: {str(e)}")

    with col2:
        st.subheader("📈 Tendencias")

        if len(st.session_state.entries) >= 2:
            fig_trend = create_symptom_chart(st.session_state.entries)
            if fig_trend:
                st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Registra al menos 2 entradas para ver tendencias")

        st.subheader("🥧 Distribución")
        if st.session_state.entries:
            fig_pie = create_category_pie(st.session_state.entries)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("🧠 GraphRAG - Relación Síntomas-Tratamientos")

    if st.session_state.entries:
        with st.expander("Ver gráfico de conocimiento"):
            categories = [
                e.get("category", "unknown") for e in st.session_state.entries
            ]
            category_counts = {}
            for cat in categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1

            st.markdown("**Red de Síntomas:**")

            nodes_data = []
            edges_data = []

            for cat, count in category_counts.items():
                nodes_data.append(f"- **{cat}**: {count} ocurrencias")

            for i, entry in enumerate(st.session_state.entries):
                if i > 0:
                    prev_cat = st.session_state.entries[i - 1].get("category", "")
                    curr_cat = entry.get("category", "")
                    if prev_cat != curr_cat:
                        edges_data.append(f"- {prev_cat} → {curr_cat}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Nodos (Síntomas):**")
                for node in nodes_data[:5]:
                    st.write(node)

            with col2:
                st.markdown("**Conexiones:**")
                if edges_data:
                    for edge in edges_data[:3]:
                        st.write(edge)
                else:
                    st.write("Los síntomas se repiten en la misma categoría")

    st.subheader("📋 Historial de Entradas")
    if st.session_state.entries:
        for entry in reversed(st.session_state.entries[-5:]):
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime(
                "%d/%m/%Y %H:%M"
            )
            with st.expander(f"📌 {timestamp}"):
                st.write(f"**Texto:** {entry.get('raw_text', '')}")
                st.write(f"**Categoría:** {entry.get('category', 'general')}")
                st.write(f"**Severidad:** {entry.get('severity', 'media')}")
                if entry.get("symptoms"):
                    symptoms_list = [s["keyword"] for s in entry["symptoms"]]
                    st.write(f"**Síntomas detectados:** {', '.join(symptoms_list)}")
    else:
        st.info("Aún no hay entradas registradas. ¡Comienza describiendo tus síntomas!")


if __name__ == "__main__":
    main()
