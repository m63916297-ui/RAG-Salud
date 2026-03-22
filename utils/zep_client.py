import os
from datetime import datetime
from typing import Optional
from zep_cloud import Zep
from zep_cloud.client import Thread


class ZepHealthClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ZEP_API_KEY")
        if not self.api_key:
            raise ValueError("ZEP_API_KEY no está configurada")
        self.client = Zep(api_key=self.api_key)
        self.user_id = "health_tracker_user"
        self._ensure_user_session()

    def _ensure_user_session(self):
        try:
            self.client.memory.get_user(self.user_id)
        except:
            self.client.memory.add_user(
                self.user_id, description="Usuario de seguimiento de salud"
            )

    def add_symptom_entry(self, symptom_text: str, session_id: str = None) -> dict:
        timestamp = datetime.now().isoformat()
        entry = {
            "content": symptom_text,
            "timestamp": timestamp,
            "type": "symptom_report",
        }

        try:
            self.client.graph.add(user_id=self.user_id, data=entry, type="json")

            self.client.memory.add(
                user_id=self.user_id,
                messages=[{"role": "user", "content": symptom_text}],
            )

            return {"status": "success", "entry": entry}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_symptom_context(self, current_query: str = None) -> dict:
        try:
            if current_query:
                results = self.client.graph.search(
                    user_id=self.user_id, query=current_query, limit=10
                )
                return {
                    "context": results.text
                    if hasattr(results, "text")
                    else str(results),
                    "status": "success",
                }

            user_summary = self.client.memory.get(self.user_id)
            return {
                "context": user_summary.summary
                if hasattr(user_summary, "summary")
                else "",
                "status": "success",
            }
        except Exception as e:
            return {"context": "", "status": "error", "message": str(e)}

    def get_knowledge_graph(self) -> dict:
        try:
            facts = self.client.graph.search(
                user_id=self.user_id, query="síntoma tratamiento", limit=50
            )
            return {"facts": self._parse_facts(facts), "status": "success"}
        except Exception as e:
            return {"facts": [], "status": "error", "message": str(e)}

    def _parse_facts(self, results) -> list:
        facts = []
        if hasattr(results, "nodes"):
            for node in results.nodes:
                facts.append(
                    {
                        "entity": node.get("name", ""),
                        "type": node.get("type", "unknown"),
                        "properties": node.get("properties", {}),
                    }
                )
        return facts

    def query_treatments(self, symptom: str) -> list:
        try:
            results = self.client.graph.search(
                user_id=self.user_id, query=f"tratamiento {symptom}", limit=5
            )
            treatments = []
            if hasattr(results, "edges"):
                for edge in results.edges:
                    if edge.get("target", "").lower() == symptom.lower():
                        treatments.append(edge.get("source", ""))
            return treatments
        except:
            return []

    def build_symptom_graph(self, entries: list) -> dict:
        nodes = []
        edges = []

        for idx, entry in enumerate(entries):
            symptom_node = f"symptom_{idx}"
            nodes.append(
                {
                    "id": symptom_node,
                    "label": entry.get("symptom", "Unknown"),
                    "type": "symptom",
                }
            )

            if entry.get("treatment"):
                treatment_node = f"treatment_{idx}"
                nodes.append(
                    {
                        "id": treatment_node,
                        "label": entry.get("treatment", ""),
                        "type": "treatment",
                    }
                )
                edges.append(
                    {
                        "from": symptom_node,
                        "to": treatment_node,
                        "label": "treated_with",
                    }
                )

            if entry.get("severity"):
                severity_node = f"severity_{idx}"
                nodes.append(
                    {
                        "id": severity_node,
                        "label": f"Severidad: {entry['severity']}",
                        "type": "severity",
                    }
                )
                edges.append(
                    {"from": symptom_node, "to": severity_node, "label": "has_severity"}
                )

        return {"nodes": nodes, "edges": edges}


zep_client: Optional[ZepHealthClient] = None


def get_zep_client() -> ZepHealthClient:
    global zep_client
    if zep_client is None:
        zep_client = ZepHealthClient()
    return zep_client
