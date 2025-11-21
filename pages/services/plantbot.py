import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from requests.exceptions import RequestException

from django.conf import settings


GENERAL_RESPONSES = [
    (
        ("metabolite", "metabolomics"),
        "MPMDB curates LC–MS/NMR supported metabolite fingerprints across alkaloids, flavonoids, terpenoids, phenolics, glycosides, and essential oils. Specify a plant and the bot will align the relevant evidence.",
    ),
    (
        ("transcript", "rna", "expression"),
        "Transcriptome dashboards summarise RNA-Seq experiments, SNP calls, and stress-condition contrasts. Ask for the transcriptomic posture of a plant to focus the response.",
    ),
    (
        ("proteome", "protein", "peptide"),
        "Proteomic dossiers surface peptide accessions, identical protein groups, and curated pathway annotations. Mention the plant name plus 'proteome' for a targeted answer.",
    ),
    (
        ("sequencing", "genome", "assembly"),
        "Use the Sequencing Bot prompts to retrieve genome assembly counts, nucleotide records, and mRNA support for each plant.",
    ),
]


FOCUS_PRIORITIES = {
    "genomics": {"genome"},
    "proteomics": {"proteome"},
    "transcriptomics": {"transcript"},
    "taxonomy": {"classification"},
}


WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"


class PlantKnowledge:
    """
    Lightweight in-memory knowledge graph over the CSV assets.

    - Normalises aliases so common and scientific names resolve to a single key.
    - Indexes each dataset (basic, classification, genome, proteome, transcript, phyto)
      under that key.
    - Produces focused scientific summaries for the Plant Bot.
    """

    splitter = re.compile(r"[/,;|]+")
    normalizer = re.compile(r"[^a-z0-9]+")

    def __init__(self):
        self.records: Dict[str, dict] = {}
        self.alias_index: Dict[str, str] = {}
        self._load()

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        return self.normalizer.sub(" ", text.lower()).strip()

    def _split_aliases(self, text: str):
        if not text:
            return []
        for token in self.splitter.split(text):
            alias = token.strip()
            if alias:
                yield alias

    def _canonical_key(self, label: str) -> str:
        aliases = list(self._split_aliases(label))
        base = aliases[0] if aliases else (label or "plant")
        return self._normalize(base)

    def _register_alias(self, alias: str, canonical_key: str, record: dict):
        norm = self._normalize(alias)
        if not norm:
            return
        self.alias_index[norm] = canonical_key
        record["aliases"].add(alias)

    def _ensure_record(self, plant_name: str, scientific_name: str):
        label_source = plant_name or scientific_name or "Plant"
        canonical_key = self._canonical_key(label_source)
        pretty_label = (
            list(self._split_aliases(plant_name))[0]
            if plant_name
            else (scientific_name or label_source)
        )
        record = self.records.setdefault(
            canonical_key,
            {
                "canonical_label": pretty_label,
                "scientific_label": scientific_name or "",
                "aliases": set(),
                "datasets": defaultdict(list),
            },
        )

        if plant_name and not record["canonical_label"]:
            record["canonical_label"] = plant_name
        if scientific_name and not record["scientific_label"]:
            record["scientific_label"] = scientific_name

        for alias in self._split_aliases(plant_name):
            self._register_alias(alias, canonical_key, record)
        for alias in self._split_aliases(scientific_name):
            self._register_alias(alias, canonical_key, record)

        return record

    def _read_csv(self, filename: str) -> List[dict]:
        """
        Read a CSV from the project root or app root using BASE_DIR.
        This allows you to keep the original CSVs in the same relative locations.
        """
        path = Path(settings.BASE_DIR) / filename
        if not path.exists():
            return []
        with path.open(encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def _ingest_single(self, dataset_name: str, rows: List[dict]):
        for row in rows:
            record = self._ensure_record(
                row.get("Plant_Name", ""), row.get("Scientific_Name", "")
            )
            record["datasets"][dataset_name] = row

    def _ingest_phyto(self, rows: List[dict]):
        for row in rows:
            record = self._ensure_record(
                row.get("Plant_Name", ""), row.get("Scientific_Name", "")
            )
            record["datasets"]["phyto"].append(row)

    def _load(self):
        """
        Wire the CSV files into the in-memory index. Filenames are
        kept identical to the legacy implementation so you do not
        have to rename anything.
        """
        file_map = {
            "basic": "basic_info.csv",
            "classification": "class.csv",
            "genome": "genome.csv",
            "proteome": "proteome.csv",
            "transcript": "trans.csv",
            "phyto": "phyto.csv",
        }

        for dataset, filename in file_map.items():
            rows = self._read_csv(filename)
            if not rows:
                continue
            if dataset == "phyto":
                self._ingest_phyto(rows)
            else:
                self._ingest_single(dataset, rows)

    def match(self, question: str):
        """
        Very lightweight fuzzy match between a free-text question and the aliases.
        """
        norm_question = self._normalize(question)
        if not norm_question:
            return None

        tokens = set(norm_question.split())
        best_key = None
        best_score = 0

        for alias, canonical in self.alias_index.items():
            if not alias:
                continue
            if alias in norm_question:
                score = len(alias)
            else:
                score = len(set(alias.split()) & tokens)
            if score > best_score:
                best_score = score
                best_key = canonical

        return self.records.get(best_key)

    def summarize(self, record: dict, focus: Optional[str] = None):
        """
        Build a scientist-facing narrative using all available datasets,
        optionally prioritising a specific omics or taxonomy focus.
        """
        datasets = record["datasets"]
        sections: List[Tuple[str, str]] = []
        references = set()

        label = record.get("canonical_label") or "This plant"
        scientific = record.get("scientific_label")
        alias_snippet = ", ".join(sorted(list(record["aliases"]))[:3])

        intro_bits = []
        if scientific:
            intro_bits.append(f"{label} ({scientific})")
        else:
            intro_bits.append(label)
        if alias_snippet:
            intro_bits.append(
                f"aka {alias_snippet}"
                + ("…" if len(record["aliases"]) > 3 else "")
            )

        sections.append(
            ("general", " ".join(intro_bits) + " is curated inside MPMDB.")
        )

        # Basic descriptor block
        basic = datasets.get("basic")
        if isinstance(basic, dict):
            desc = basic.get("Description", "").strip()
            chem = basic.get("Chemical_Properties", "").strip()
            medicinal = basic.get("Medicinal_Value", "").strip()
            morphology = basic.get("Morphological_Features", "").strip()
            region = basic.get("Worldwide_regions_Support_their_Growth", "").strip()

            if desc:
                sections.append(("basic", desc))
            if chem:
                sections.append(("basic", f"Chemistry focus: {chem}"))
            if medicinal:
                sections.append(("basic", f"Therapeutic evidence: {medicinal}"))
            if morphology:
                sections.append(("basic", f"Morphology: {morphology}"))
            if region:
                sections.append(("basic", f"Geography: {region}"))
            if basic.get("References"):
                references.add(basic["References"])

        # Taxonomy
        classification = datasets.get("classification")
        if isinstance(classification, dict):
            lineage = [
                classification.get("Order"),
                classification.get("Family"),
                classification.get("Genus"),
                classification.get("Species"),
            ]
            lineage = [item for item in lineage if item]
            if lineage:
                sections.append(
                    ("classification", "Taxonomy · " + " → ".join(lineage))
                )
            if classification.get("NCBI_link"):
                references.add(classification["NCBI_link"])

        # Genome
        genome = datasets.get("genome")
        if isinstance(genome, dict):
            sections.append(
                (
                    "genome",
                    (
                        "Genome resources: "
                        f"{genome.get('Nucleotide', '0')} nucleotide entries, "
                        f"{genome.get('Genome_Sequence', '0')} genome assemblies, and "
                        f"{genome.get('mRNA_Sequence', '0')} mRNA sequences curated via NCBI."
                    ),
                )
            )
            if genome.get("NCBI_link"):
                references.add(genome["NCBI_link"])

        # Proteome
        proteome = datasets.get("proteome")
        if isinstance(proteome, dict):
            sections.append(
                (
                    "proteome",
                    (
                        "Proteome coverage: "
                        f"{proteome.get('Protein_Seq', '0')} protein sequences, "
                        f"{proteome.get('Identical_Protein_Groups', '0')} identical protein groups, "
                        f"{proteome.get('Protein', '0')} peptide identifications."
                    ),
                )
            )
            if proteome.get("NCBI_link"):
                references.add(proteome["NCBI_link"])

        # Transcriptome
        transcript = datasets.get("transcript")
        if isinstance(transcript, dict):
            sections.append(
                (
                    "transcript",
                    (
                        "Transcriptomics: "
                        f"{transcript.get('SRA', '0')} SRA runs with "
                        f"{transcript.get('DNA', '0')} DNA and "
                        f"{transcript.get('RNA', '0')} RNA libraries across "
                        f"{transcript.get('BioProject', '0')} BioProjects / "
                        f"{transcript.get('BioSample', '0')} BioSamples."
                    ),
                )
            )
            if transcript.get("NCBI_link"):
                references.add(transcript["NCBI_link"])

        # Phytochemical / metabolite layer
        phyto_rows = datasets.get("phyto")
        if phyto_rows:
            compounds = []
            seen = set()
            for row in phyto_rows:
                compound = row.get("Phytochemicals")
                if not compound or compound in seen:
                    continue
                activity = row.get("Activity_Count") or "NA"
                part = row.get("Plant_Part") or "various tissues"
                compounds.append(
                    f"{compound} (activity {activity}, {part.lower()})"
                )
                seen.add(compound)
                if len(compounds) == 3:
                    break
                if row.get("References"):
                    references.add(row["References"])
            if compounds:
                sections.append(
                    (
                        "phyto",
                        "Highlighted phytochemicals: "
                        + "; ".join(compounds)
                        + ".",
                    )
                )

        # Reorder based on focus if provided
        focus_keys = FOCUS_PRIORITIES.get(focus or "", set())
        ordered_sections: List[str] = []

        if focus_keys:
            for key, text in sections:
                if key in focus_keys:
                    ordered_sections.append(text)
            if not ordered_sections:
                ordered_sections.append(
                    f"No curated {focus} dataset yet inside MPMDB. "
                    "Consider contributing data or cross-checking NCBI."
                )
            ordered_sections.extend(text for key, text in sections if key not in focus_keys)
        else:
            ordered_sections = [text for _, text in sections]

        answer = " ".join(seg.strip() for seg in ordered_sections if seg.strip())
        source = "; ".join(sorted(ref for ref in references if ref)) or None
        return answer, source


KNOWLEDGE_BASE = PlantKnowledge()


def _wiki_summary(topic: str) -> Optional[Tuple[str, str]]:
    """
    Fetch a short encyclopedic-style summary from Wikipedia as a
    fallback when the plant is not yet curated in MPMDB.
    """
    try:
        search_resp = requests.get(
            WIKI_SEARCH_URL,
            params={
                "action": "opensearch",
                "search": topic,
                "limit": 1,
                "namespace": 0,
                "format": "json",
            },
            timeout=6,
        )
        search_resp.raise_for_status()
        data = search_resp.json()
        if not data or len(data) < 2 or not data[1]:
            return None

        title = data[1][0]
        summary_resp = requests.get(
            WIKI_SUMMARY_URL.format(title=title.replace(" ", "_")),
            timeout=6,
            headers={"Accept": "application/json"},
        )
        summary_resp.raise_for_status()
        summary_data = summary_resp.json()
        summary = summary_data.get("extract")
        url = (
            summary_data.get("content_urls", {})
            .get("desktop", {})
            .get("page")
            or summary_data.get("canonical")
        )

        if summary:
            return summary.strip(), url
    except RequestException:
        return None

    return None


def generate_answer(question: str, focus: Optional[str] = None):
    """
    Main entry point for the Plant Bot.

    - First, respond with general guidance snippets if the query is broad
      (e.g., "metabolomics", "sequencing", etc.).
    - Next, try to resolve the plant into the curated CSV-backed knowledge base
      and build a scientist-facing summary, optionally focused on a given layer.
    - Finally, if no curated plant matches, fall back to a Wikipedia-style
      summary so that queries for any species still receive a useful answer.
    """
    question_lower = question.lower()

    # 1) General responses for broad modality questions
    for keywords, response in GENERAL_RESPONSES:
        if any(keyword in question_lower for keyword in keywords):
            return response, None

    # 2) Curated plant knowledge from CSVs
    record = KNOWLEDGE_BASE.match(question)
    if record:
        return KNOWLEDGE_BASE.summarize(record, focus=focus)

    # 3) Fallback: external encyclopedic summary so exotic species still work
    wiki = _wiki_summary(question)
    if wiki:
        summary, url = wiki
        reply = (
            "Here's what I found after checking recent encyclopedic sources:\n"
            f"{summary}"
        )
        return reply, url

    # 4) Final graceful fallback
    return (
        "I could not match that request to our curated plants yet. "
        "Try providing the botanical or scientific name, optionally followed by "
        "genome/proteome/transcriptome/metabolite context. You can also ask for "
        "taxonomy, sequencing, or metabolite insights explicitly.",
        None,
    )

