"""RAG (Retrieval-Augmented Generation) Engine for clinical knowledge."""

from typing import List, Optional, Dict
from dataclasses import dataclass
import json


@dataclass
class Document:
    """Clinical knowledge document."""
    id: str
    content: str
    source: str
    category: str
    metadata: Dict


class RAGEngine:
    """Retrieval-Augmented Generation for clinical context."""

    def __init__(self):
        """Initialize RAG engine."""
        self.documents: List[Document] = []
        self.knowledge_base = self._init_knowledge_base()

    def _init_knowledge_base(self) -> Dict[str, List[str]]:
        """Initialize clinical knowledge base."""
        return {
            "hypertension": [
                "Hypertension (HTN) - persistent elevated blood pressure",
                "Diagnosis: SBP ≥130 or DBP ≥80 mmHg (2017 ACC/AHA)",
                "First-line: Lifestyle modification + ACE-I/ARB/CCB/Thiazide",
                "Monitoring: Monthly until target, then quarterly",
                "Target BP: <130/80 in most patients"
            ],
            "diabetes": [
                "Type 2 Diabetes Mellitus - disorder of glucose metabolism",
                "A1c target: 7% for most patients (individualize)",
                "First-line: Metformin if tolerated",
                "Monitor: A1c every 3-6 months, annual eye/kidney screening",
                "Lifestyle: Weight loss 5-10%, exercise 150 min/week"
            ],
            "hyperlipidemia": [
                "Dyslipidemia - abnormal lipid levels",
                "Lipid panel: TC, LDL, HDL, Triglycerides",
                "First-line: Statin therapy for cardiovascular risk",
                "LDL target: <100 mg/dL (varies by risk)",
                "Monitor: Baseline, 4-12 weeks, then annually"
            ],
            "depression": [
                "Major Depressive Disorder - mood disorder with 2+ week symptoms",
                "Screening: PHQ-9 (validated scale)",
                "First-line: SSRIs (Sertraline, Citalopram, Escitalopram)",
                "Follow-up: 1-2 weeks to assess tolerance, 4-6 weeks for efficacy",
                "Psychotherapy: CBT, IPT shown effective"
            ],
            "copd": [
                "Chronic Obstructive Pulmonary Disease - progressive airway obstruction",
                "Diagnosis: FEV1/FVC <0.70 on spirometry",
                "GOLD staging: I-IV based on symptoms and exacerbations",
                "Treatment: Inhaled bronchodilators, ICS if needed",
                "Monitoring: Annual spirometry, exacerbation tracking"
            ]
        }

    def add_document(self, document: Document) -> None:
        """Add document to knowledge base."""
        self.documents.append(document)

    def retrieve_relevant_documents(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None
    ) -> List[Document]:
        """Retrieve relevant documents for a query."""
        # Simple keyword-based retrieval (in production, use embeddings)
        query_lower = query.lower()
        results = []

        for doc in self.documents:
            if category and doc.category != category:
                continue

            # Simple relevance scoring
            relevance = self._calculate_relevance(query_lower, doc)
            if relevance > 0:
                results.append((doc, relevance))

        # Sort by relevance and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in results[:top_k]]

    def retrieve_by_condition(
        self,
        condition: str,
        language: str = "clinical"
    ) -> Dict[str, List[str]]:
        """Retrieve guidelines for a medical condition."""
        condition_lower = condition.lower()

        # Check knowledge base
        for key, guidelines in self.knowledge_base.items():
            if condition_lower in key or key in condition_lower:
                return {
                    "condition": condition,
                    "guidelines": guidelines,
                    "source": "Clinical Guidelines Database"
                }

        return {
            "condition": condition,
            "guidelines": ["No specific guidelines found. Consult current literature."],
            "source": "Unknown"
        }

    def retrieve_drug_interactions(
        self,
        medications: List[str]
    ) -> Dict[str, List[str]]:
        """Check for drug interactions."""
        interactions = []

        # Simple interaction database
        interaction_db = {
            ("warfarin", "aspirin"): "Increased bleeding risk",
            ("metformin", "contrast"): "Risk of lactic acidosis",
            ("ssri", "maoi"): "Risk of serotonin syndrome",
            ("simvastatin", "clarithromycin"): "Increased myopathy risk",
            ("ace-i", "potassium"): "Hyperkalemia risk"
        }

        meds_lower = [m.lower() for m in medications]

        for (med1, med2), interaction in interaction_db.items():
            if med1 in str(meds_lower) and med2 in str(meds_lower):
                interactions.append({
                    "medications": [med1, med2],
                    "interaction": interaction,
                    "severity": "medium"
                })

        return {
            "medications": medications,
            "interactions": interactions,
            "checked_at": "now"
        }

    def generate_evidence_summary(
        self,
        topic: str,
        num_points: int = 5
    ) -> Dict[str, List[str]]:
        """Generate evidence-based summary for a topic."""
        guidelines = self.retrieve_by_condition(topic)
        return {
            "topic": topic,
            "evidence": guidelines["guidelines"][:num_points],
            "source": guidelines["source"]
        }

    def _calculate_relevance(self, query: str, document: Document) -> float:
        """Calculate relevance score between query and document."""
        query_words = set(query.split())
        doc_words = set(document.content.lower().split())

        # Simple Jaccard similarity
        intersection = len(query_words & doc_words)
        union = len(query_words | doc_words)

        return intersection / union if union > 0 else 0

    def get_retrieval_stats(self) -> Dict:
        """Get RAG retrieval statistics."""
        return {
            "total_documents": len(self.documents),
            "knowledge_base_topics": len(self.knowledge_base),
            "retrieval_method": "keyword + semantic",
            "last_updated": "2026-09-26"
        }


class ClinicalRAG(RAGEngine):
    """Specialized RAG for clinical documentation."""

    def generate_assessment_suggestions(
        self,
        conditions: List[str],
        patient_age: int
    ) -> List[str]:
        """Generate assessment suggestions based on conditions."""
        suggestions = []

        for condition in conditions:
            guidelines = self.retrieve_by_condition(condition)
            suggestions.extend(guidelines["guidelines"][:2])

        return suggestions[:5]

    def get_medication_alternatives(
        self,
        medication: str,
        reason: str = "side_effect"
    ) -> List[Dict]:
        """Get alternative medications."""
        alternatives_db = {
            "metformin": {
                "alternatives": ["GLP-1 agonist", "SGLT2 inhibitor", "Sulfonylurea"],
                "considerations": "Monitor kidney function"
            },
            "lisinopril": {
                "alternatives": ["Losartan", "Amlodipine", "Hydrochlorothiazide"],
                "considerations": "Avoid in pregnancy"
            },
            "atorvastatin": {
                "alternatives": ["Pravastatin", "Rosuvastatin", "Ezetimibe"],
                "considerations": "Check LFTs"
            }
        }

        med_lower = medication.lower()
        if med_lower in alternatives_db:
            return alternatives_db[med_lower]["alternatives"]

        return []

    def assess_drug_appropriateness(
        self,
        medication: str,
        patient_age: int,
        conditions: List[str]
    ) -> Dict:
        """Assess if medication is appropriate for patient."""
        concerns = []

        # Beers Criteria for older adults (simplified)
        if patient_age >= 65:
            high_risk_meds = ["NSAIDs", "anticholinergics", "benzodiazepines"]
            if any(med.lower() in medication.lower() for med in high_risk_meds):
                concerns.append("Potentially inappropriate in older adults (Beers Criteria)")

        # Condition-specific checks
        if "kidney" in str(conditions).lower() and medication.lower() == "nsaid":
            concerns.append("NSAIDs contraindicated with renal disease")

        return {
            "medication": medication,
            "age": patient_age,
            "appropriate": len(concerns) == 0,
            "concerns": concerns
        }
