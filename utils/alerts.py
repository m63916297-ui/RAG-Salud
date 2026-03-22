from typing import List, Dict
from datetime import datetime, timedelta
import pandas as pd


class AlertSystem:
    def __init__(self):
        self.alert_thresholds = {
            "critical_symptoms": [
                "dolor en el pecho",
                "dificultad para respirar",
                "sangrado",
                "fiebre alta",
                "desmayo",
            ],
            "max_recurring_days": 7,
            "max_daily_entries": 10,
        }

    def check_symptoms(self, text: str) -> Dict:
        text_lower = text.lower()
        alerts = []

        for symptom in self.alert_thresholds["critical_symptoms"]:
            if symptom in text_lower:
                alerts.append(
                    {
                        "level": "critical",
                        "type": "emergency_keyword",
                        "symptom": symptom,
                        "message": f"Se detectó '{symptom}'. Considere buscar atención médica inmediata.",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return {"has_alerts": len(alerts) > 0, "alerts": alerts}

    def analyze_trends(self, entries: List[Dict]) -> Dict:
        if not entries:
            return {"trends": [], "summary": {}}

        df = pd.DataFrame(entries)
        trends = []

        if "category" in df.columns:
            category_counts = df["category"].value_counts()

            if len(category_counts) > 1:
                dominant = category_counts.iloc[0]
                total = len(df)
                percentage = (dominant / total) * 100

                if percentage >= 60:
                    trends.append(
                        {
                            "type": "dominant_symptom",
                            "symptom": category_counts.index[0],
                            "percentage": round(percentage, 1),
                            "message": f"El {percentage:.1f}% de los síntomas registrados pertenecen a una misma categoría",
                        }
                    )

        if "severity" in df.columns:
            severity_scores = {"alta": 3, "media": 2, "baja": 1}
            df["severity_score"] = df["severity"].map(severity_scores).fillna(2)

            if len(df) >= 3:
                recent_avg = df.tail(3)["severity_score"].mean()
                overall_avg = df["severity_score"].mean()

                if recent_avg > overall_avg * 1.2:
                    trends.append(
                        {
                            "type": "worsening_trend",
                            "message": "Los síntomas recientes son más severos que el promedio",
                            "severity_change": round(recent_avg - overall_avg, 2),
                        }
                    )
                elif recent_avg < overall_avg * 0.8:
                    trends.append(
                        {
                            "type": "improving_trend",
                            "message": "Los síntomas recientes son menos severos",
                            "severity_change": round(overall_avg - recent_avg, 2),
                        }
                    )

        return {
            "trends": trends,
            "summary": {
                "total_entries": len(df),
                "date_range": f"{df.get('timestamp', [datetime.now()] * len(df)).min()} - {df.get('timestamp', [datetime.now()] * len(df)).max()}"
                if len(df) > 0
                else "Sin datos",
            },
        }

    def generate_health_score(self, entries: List[Dict]) -> Dict:
        if not entries:
            return {"score": 100, "status": "Sin datos", "factors": []}

        score = 100
        factors = []

        severity_map = {"alta": -20, "media": -10, "baja": -5}

        for entry in entries:
            if "severity" in entry:
                penalty = severity_map.get(entry["severity"], -5)
                score += penalty
                factors.append(f"Severidad {entry['severity']}: {penalty} puntos")

        if len(entries) >= 5:
            categories = [e.get("category", "") for e in entries]
            unique_categories = len(set(categories))

            if unique_categories >= 4:
                score -= 15
                factors.append("Múltiples categorías de síntomas: -15 puntos")
            elif unique_categories <= 2:
                score += 10
                factors.append("Síntomas concentrados en pocas categorías: +10 puntos")

        score = max(0, min(100, score))

        if score >= 80:
            status = "Excelente"
        elif score >= 60:
            status = "Bueno"
        elif score >= 40:
            status = "Regular"
        else:
            status = "Necesita atención"

        return {
            "score": score,
            "status": status,
            "factors": factors,
            "interpretation": self._interpret_score(score),
        }

    def _interpret_score(self, score: int) -> str:
        interpretations = {
            range(
                90, 101
            ): "Su historial de salud muestra patrones positivos con síntomas leves y espaciados.",
            range(
                70, 90
            ): "Los síntomas reportados son moderados. Continúe monitoreando.",
            range(
                50, 70
            ): "Se detectan algunos patrones que merecen atención. Revise las recomendaciones.",
            range(0, 50): "Los patrones detectados requieren atención profesional.",
        }

        for score_range, interpretation in interpretations.items():
            if score in score_range:
                return interpretation

        return "Sin información suficiente para generar una interpretación."


alert_system = AlertSystem()
