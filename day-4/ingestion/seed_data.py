"""Seed source registry for the Agentic RAG POC (Step 11).

A tiny, hand-authored corpus standing in for a real ingestion pipeline.
Each document carries the metadata SKILLS.md requires (source_type,
approved, version, ingested_at) and is pre-split into chunks. Mixes
approved/unapproved docs across all four source_types so the allowlist
filter in retrieval/engine.py is actually exercised.
"""

from __future__ import annotations

from typing import TypedDict


class Chunk(TypedDict):
    chunk_id: str
    text: str


class Document(TypedDict):
    document_id: str
    title: str
    source_type: str
    approved: bool
    version: str
    superseded_by: str | None
    ingested_at: str
    chunks: list[Chunk]


SEED_DOCUMENTS: list[Document] = [
    {
        "document_id": "doc-lit-001",
        "title": "Semaglutide mechanism of action in GLP-1 receptor agonism",
        "source_type": "literature",
        "approved": True,
        "version": "1.0",
        "superseded_by": None,
        "ingested_at": "2026-01-10T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-lit-001-c1",
                "text": (
                    "Semaglutide is a GLP-1 receptor agonist that mimics the "
                    "incretin hormone GLP-1, stimulating glucose-dependent "
                    "insulin secretion from pancreatic beta cells."
                ),
            },
            {
                "chunk_id": "doc-lit-001-c2",
                "text": (
                    "Beyond glycemic control, semaglutide slows gastric "
                    "emptying and acts on hypothalamic appetite centers, "
                    "which underlies its weight-loss effect."
                ),
            },
        ],
    },
    {
        "document_id": "doc-pat-002",
        "title": "Patent: sustained-release formulation of a GLP-1 agonist",
        "source_type": "patent",
        "approved": True,
        "version": "2.1",
        "superseded_by": None,
        "ingested_at": "2026-01-12T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-pat-002-c1",
                "text": (
                    "The claimed formulation encapsulates a GLP-1 receptor "
                    "agonist in a biodegradable polymer matrix to extend "
                    "release over seven days, reducing dosing frequency."
                ),
            }
        ],
    },
    {
        "document_id": "doc-ct-003",
        "title": "Phase III trial: GLP-1 agonist for cardiovascular outcomes",
        "source_type": "clinical_trial",
        "approved": True,
        "version": "1.0",
        "superseded_by": None,
        "ingested_at": "2026-01-15T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-ct-003-c1",
                "text": (
                    "In a randomized, double-blind trial of 17,604 patients, "
                    "the GLP-1 receptor agonist reduced major adverse "
                    "cardiovascular events by 20% versus placebo over a "
                    "median follow-up of 39.8 months."
                ),
            }
        ],
    },
    {
        "document_id": "doc-int-004",
        "title": "Internal report: competitive landscape for obesity drugs",
        "source_type": "internal_report",
        "approved": True,
        "version": "0.9",
        "superseded_by": None,
        "ingested_at": "2026-01-18T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-int-004-c1",
                "text": (
                    "Dual GIP/GLP-1 receptor agonists show superior weight "
                    "loss to single-target GLP-1 agonists in early-phase "
                    "readouts, intensifying pipeline competition."
                ),
            }
        ],
    },
    {
        "document_id": "doc-lit-005",
        "title": "Draft manuscript on a novel kinase inhibitor (unreviewed)",
        "source_type": "literature",
        "approved": False,
        "version": "0.1",
        "superseded_by": None,
        "ingested_at": "2026-01-20T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-lit-005-c1",
                "text": (
                    "Preliminary, unreviewed data suggest a novel kinase "
                    "inhibitor may show off-target activity against "
                    "GLP-1 receptor signaling pathways."
                ),
            }
        ],
    },
    {
        "document_id": "doc-pat-006",
        "title": "Withdrawn patent application: injection device",
        "source_type": "patent",
        "approved": False,
        "version": "1.0",
        "superseded_by": None,
        "ingested_at": "2026-01-21T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-pat-006-c1",
                "text": (
                    "This withdrawn application described an auto-injector "
                    "device for subcutaneous peptide delivery."
                ),
            }
        ],
    },
    {
        "document_id": "doc-ct-007",
        "title": "Superseded Phase II trial protocol (see doc-ct-003)",
        "source_type": "clinical_trial",
        "approved": False,
        "version": "1.0",
        "superseded_by": "doc-ct-003",
        "ingested_at": "2026-01-05T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-ct-007-c1",
                "text": (
                    "Early Phase II dosing protocol, superseded by the "
                    "Phase III cardiovascular outcomes trial."
                ),
            }
        ],
    },
    {
        "document_id": "doc-lit-008",
        "title": "PD-1 checkpoint inhibitor mechanism in advanced melanoma",
        "source_type": "literature",
        "approved": True,
        "version": "1.0",
        "superseded_by": None,
        "ingested_at": "2026-01-25T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-lit-008-c1",
                "text": (
                    "The PD-1 checkpoint inhibitor pembrolizumab blocks the "
                    "interaction between programmed cell death protein 1 on "
                    "T cells and its ligand PD-L1 on tumor cells, releasing "
                    "the brake that tumors use to evade cytotoxic T-cell "
                    "killing."
                ),
            },
            {
                "chunk_id": "doc-lit-008-c2",
                "text": (
                    "In advanced melanoma, restoring T-cell-mediated "
                    "anti-tumor immunity through PD-1 blockade produces "
                    "durable objective responses in a subset of patients, "
                    "particularly those with high tumor mutational burden "
                    "and pre-existing tumor-infiltrating lymphocytes."
                ),
            },
        ],
    },
    {
        "document_id": "doc-ct-009",
        "title": "Phase III trial: PD-1 checkpoint inhibitor in non-small-cell lung cancer",
        "source_type": "clinical_trial",
        "approved": True,
        "version": "1.0",
        "superseded_by": None,
        "ingested_at": "2026-01-26T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-ct-009-c1",
                "text": (
                    "In a randomized Phase III trial of 616 patients with "
                    "previously untreated metastatic non-small-cell lung "
                    "cancer, the PD-1 checkpoint inhibitor improved median "
                    "overall survival to 26.3 months versus 13.4 months for "
                    "platinum-based chemotherapy alone."
                ),
            },
            {
                "chunk_id": "doc-ct-009-c2",
                "text": (
                    "Immune-related adverse events, including pneumonitis "
                    "and thyroid dysfunction, occurred in 27% of patients "
                    "receiving the checkpoint inhibitor, consistent with the "
                    "known safety profile of PD-1/PD-L1 blockade."
                ),
            },
        ],
    },
    {
        "document_id": "doc-pat-010",
        "title": "Patent: PARP inhibitor for BRCA-mutant tumor treatment",
        "source_type": "patent",
        "approved": True,
        "version": "1.3",
        "superseded_by": None,
        "ingested_at": "2026-01-27T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-pat-010-c1",
                "text": (
                    "The claimed compound is a PARP inhibitor that exploits "
                    "synthetic lethality in tumors carrying BRCA1 or BRCA2 "
                    "mutations by trapping PARP1 on damaged DNA, preventing "
                    "base-excision repair and causing lethal double-strand "
                    "breaks selectively in homologous-recombination-deficient "
                    "cancer cells."
                ),
            },
            {
                "chunk_id": "doc-pat-010-c2",
                "text": (
                    "The formulation described is an orally bioavailable "
                    "tablet intended for maintenance therapy in ovarian and "
                    "breast cancer patients following response to "
                    "platinum-based chemotherapy."
                ),
            },
        ],
    },
    {
        "document_id": "doc-lit-011",
        "title": "Draft manuscript on PARP inhibitor resistance mechanisms (unreviewed)",
        "source_type": "literature",
        "approved": False,
        "version": "0.2",
        "superseded_by": None,
        "ingested_at": "2026-01-28T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-lit-011-c1",
                "text": (
                    "Preliminary, unreviewed data suggest that restoration "
                    "of homologous recombination repair through secondary "
                    "BRCA1 mutations may confer acquired resistance to PARP "
                    "inhibitor maintenance therapy in relapsed ovarian "
                    "cancer."
                ),
            }
        ],
    },
    {
        "document_id": "doc-ct-012",
        "title": "Phase III trial: SGLT2 inhibitor for heart failure with reduced ejection fraction",
        "source_type": "clinical_trial",
        "approved": True,
        "version": "1.0",
        "superseded_by": None,
        "ingested_at": "2026-01-29T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-ct-012-c1",
                "text": (
                    "In a randomized, placebo-controlled trial of 4,744 "
                    "patients with heart failure and reduced ejection "
                    "fraction, the SGLT2 inhibitor reduced the composite "
                    "risk of cardiovascular death or worsening heart failure "
                    "by 26% regardless of diabetes status, establishing a "
                    "cardio-renal benefit independent of glycemic control."
                ),
            },
            {
                "chunk_id": "doc-ct-012-c2",
                "text": (
                    "Renal outcomes were also improved: the rate of decline "
                    "in estimated glomerular filtration rate was "
                    "significantly slower in the SGLT2 inhibitor arm, "
                    "supporting its role in cardio-renal-metabolic protection "
                    "beyond blood glucose lowering."
                ),
            },
        ],
    },
    {
        "document_id": "doc-int-013",
        "title": "Internal report: market landscape for HIV pre-exposure prophylaxis",
        "source_type": "internal_report",
        "approved": True,
        "version": "1.1",
        "superseded_by": None,
        "ingested_at": "2026-01-30T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-int-013-c1",
                "text": (
                    "Long-acting injectable pre-exposure prophylaxis (PrEP) "
                    "regimens, dosed every two months, are displacing daily "
                    "oral tenofovir-based PrEP among at-risk populations "
                    "seeking better adherence for HIV prevention."
                ),
            },
            {
                "chunk_id": "doc-int-013-c2",
                "text": (
                    "Uptake of injectable PrEP is highest in sexual health "
                    "clinics serving populations with documented adherence "
                    "challenges to daily oral HIV prevention regimens, "
                    "intensifying competition for next-generation "
                    "long-acting antiretroviral formulations."
                ),
            },
        ],
    },
    {
        "document_id": "doc-lit-014",
        "title": "Retracted manuscript on oral PrEP adherence biomarkers",
        "source_type": "literature",
        "approved": False,
        "version": "1.0",
        "superseded_by": None,
        "ingested_at": "2026-01-31T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-lit-014-c1",
                "text": (
                    "This retracted study had claimed that a dried blood "
                    "spot biomarker could predict adherence to daily oral "
                    "tenofovir-based HIV pre-exposure prophylaxis, but the "
                    "underlying assay data could not be reproduced."
                ),
            }
        ],
    },
    {
        "document_id": "doc-pat-015",
        "title": "Withdrawn patent application: AAV capsid for gene therapy delivery",
        "source_type": "patent",
        "approved": False,
        "version": "0.1",
        "superseded_by": None,
        "ingested_at": "2026-02-01T00:00:00Z",
        "chunks": [
            {
                "chunk_id": "doc-pat-015-c1",
                "text": (
                    "This withdrawn application described an engineered "
                    "adeno-associated virus (AAV) capsid variant intended "
                    "for one-time gene therapy delivery of a functional gene "
                    "copy to liver tissue in patients with a rare inherited "
                    "metabolic disease."
                ),
            },
            {
                "chunk_id": "doc-pat-015-c2",
                "text": (
                    "The capsid engineering aimed to reduce pre-existing "
                    "neutralizing antibody binding, a common barrier to "
                    "systemic AAV-based gene therapy re-dosing in rare "
                    "disease patients previously exposed to wild-type AAV."
                ),
            },
        ],
    },
]
