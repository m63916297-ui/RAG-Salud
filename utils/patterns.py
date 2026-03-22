import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import pandas as pd


class PatternDetector:
    def __init__(self):
        self.symptom_patterns = {
            "dolor_cabeza": ["dolor de cabeza", "cefalea", "migraña", "jaqueca"],
            "fatiga": ["cansancio", "fatiga", "agotamiento", "sin energía", "exhausto"],
            "dolor_muscular": [
                "dolor muscular",
                "mialgia",
                "dolor en músculos",
                "músculos adoloridos",
            ],
            "insomnio": [
                "insomnio",
                "no puedo dormir",
                "dificultad para dormir",
                "sueño",
            ],
            "ansiedad": ["ansiedad", "nervios", "estrés", "preocupación", "ansioso"],
            "dolor_estomago": [
                "dolor de estómago",
                "náusea",
                "malestar estomacal",
                "indigestión",
            ],
            "mareo": ["mareo", "vértigo", "desmayo", "aturdimiento"],
            "respiratorio": [
                "tos",
                "congestión",
                "dificultad para respirar",
                "garganta",
            ],
        }

        self.severity_keywords = {
            "alta": ["muy fuerte", "intenso", "severo", "agudo", "insoportable"],
            "media": ["moderado", "regular", "normal", "tolerable"],
            "baja": ["leve", "ligero", "poco", "mínimo", "suave"],
        }

        self.time_patterns = [
            r"hace (\d+) días?",
            r"desde hace (\d+) días?",
            r"esta (mañana|tarde|noche|semana)",
            r"últimos? (\d+) días?",
            r"ayer|anteayer|hoy|ahora",
        ]

    def extract_symptoms(self, text: str) -> List[Dict]:
        text_lower = text.lower()
        symptoms_found = []

        for category, keywords in self.symptom_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    severity = self._extract_severity(text_lower)
                    duration = self._extract_duration(text_lower)
                    symptoms_found.append(
                        {
                            "category": category,
                            "keyword": keyword,
                            "severity": severity,
                            "duration": duration,
                            "raw_text": text,
                        }
                    )
                    break

        return symptoms_found

    def _extract_severity(self, text: str) -> str:
        for level, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return level
        return "media"

    def _extract_duration(self, text: str) -> str:
        for pattern in self.time_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return "no especificado"

    def detect_recurring_patterns(self, entries: List[Dict]) -> Dict:
        if not entries:
            return {"patterns": [], "insights": []}

        df = pd.DataFrame(entries)
        patterns = []
        insights = []

        category_counts = Counter([e.get("category", "unknown") for e in entries])
        recurring_symptoms = category_counts.most_common(3)

        for symptom, count in recurring_symptoms:
            if count >= 2:
                patterns.append(
                    {
                        "type": "recurring_symptom",
                        "symptom": symptom,
                        "occurrences": count,
                        "recommendation": self._get_recommendation(symptom),
                    }
                )
                insights.append(
                    f"Síntoma recurrente: {symptom} (aparece {count} veces)"
                )

        severity_trends = self._analyze_severity_trends(entries)
        if severity_trends:
            patterns.extend(severity_trends["patterns"])
            insights.extend(severity_trends["insights"])

        time_patterns = self._analyze_time_patterns(entries)
        if time_patterns:
            patterns.extend(time_patterns["patterns"])
            insights.extend(time_patterns["insights"])

        return {
            "patterns": patterns,
            "insights": insights,
            "summary": {
                "total_entries": len(entries),
                "unique_symptoms": len(category_counts),
                "most_common": dict(recurring_symptoms[:3]),
            },
        }

    def _analyze_severity_trends(self, entries: List[Dict]) -> Dict:
        severity_map = {"alta": 3, "media": 2, "baja": 1}
        severities = []

        for entry in entries:
            if "severity" in entry:
                sev = entry["severity"]
                if sev in severity_map:
                    severities.append(
                        {"severity": sev, "category": entry.get("category", "")}
                    )

        if len(severities) >= 3:
            high_severity_count = sum(1 for s in severities if s["severity"] == "alta")
            if high_severity_count >= len(severities) * 0.5:
                return {
                    "patterns": [
                        {
                            "type": "high_severity_trend",
                            "severity_count": high_severity_count,
                            "total": len(severities),
                            "alert_level": "warning"
                            if high_severity_count < len(severities) * 0.7
                            else "critical",
                        }
                    ],
                    "insights": [
                        f"Se detectaron {high_severity_count} episodios de alta severidad de {len(severities)} totales"
                    ],
                }

        return None

    def _analyze_time_patterns(self, entries: List[Dict]) -> Dict:
        time_keywords = {
            "mañana": ["mañana", "al despertar", "al levantarme"],
            "tarde": ["tarde", "durante el día", "mediodía"],
            "noche": ["noche", "al acostarme", "insomnio", "no puedo dormir"],
        }

        time_distribution = defaultdict(int)

        for entry in entries:
            raw_text = entry.get("raw_text", "").lower()
            for period, keywords in time_keywords.items():
                if any(kw in raw_text for kw in keywords):
                    time_distribution[period] += 1

        if time_distribution:
            most_common_time = max(time_distribution.items(), key=lambda x: x[1])
            if most_common_time[1] >= 2:
                return {
                    "patterns": [
                        {
                            "type": "time_pattern",
                            "time_period": most_common_time[0],
                            "occurrences": most_common_time[1],
                        }
                    ],
                    "insights": [
                        f"Los síntomas aparecen frecuentemente en la {most_common_time[0]}"
                    ],
                }

        return None

    def _get_recommendation(self, symptom: str) -> str:
        recommendations = {
            "dolor_cabeza": "Considere descansar en un ambiente tranquilo, hidratarse bien y consultar si persiste más de 3 días.",
            "fatiga": "Revise sus horas de sueño, alimentación e incluya actividad física moderada.",
            "dolor_muscular": "Aplique calor local, descanse el músculo afectado y stretching suave.",
            "insomnio": "Establezca una rutina de sueño regular y evite pantallas antes de dormir.",
            "ansiedad": "Practique técnicas de respiración, mindfulness o considere apoyo profesional.",
            "dolor_estomago": "Evite alimentos irritantes, coma despacio y manténgase hidratado.",
            "mareo": "Siéntese o acuéstese inmediatamente, evite movimientos bruscos.",
            "respiratorio": "Si persiste más de una semana, consulte a un médico.",
        }
        return recommendations.get(
            symptom, "Consulte con un profesional de salud si los síntomas persisten."
        )

    def generate_alerts(self, patterns: Dict) -> List[Dict]:
        alerts = []

        for pattern in patterns.get("patterns", []):
            if pattern["type"] == "recurring_symptom" and pattern["occurrences"] >= 3:
                alerts.append(
                    {
                        "level": "warning",
                        "title": "Síntoma Recurrente",
                        "message": f"{pattern['symptom']} ha aparecido {pattern['occurrences']} veces",
                        "action": pattern["recommendation"],
                    }
                )

            elif pattern["type"] == "high_severity_trend":
                if pattern.get("alert_level") == "critical":
                    alerts.append(
                        {
                            "level": "critical",
                            "title": "Tendencia de Alta Severidad",
                            "message": "Los síntomas de alta severidad son predominantes",
                            "action": "Se recomienda consultar a un médico lo antes posible",
                        }
                    )
                else:
                    alerts.append(
                        {
                            "level": "warning",
                            "title": "Aumento de Severidad",
                            "message": "Se detectan múltiples episodios de alta severidad",
                            "action": "Monitoree de cerca y consulte si continúa",
                        }
                    )

        return alerts
