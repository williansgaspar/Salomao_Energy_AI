from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from salomao_core import LocalRetriever, normalize, tokens
from redacao import compose_auditable_draft


class LocalRetrieverTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retriever = LocalRetriever()

    def test_loads_verified_primary_sources_with_local_text(self):
        self.assertGreater(len(self.retriever.sources), 5)
        self.assertTrue(all(source.verification_status == "verified" for source in self.retriever.sources))
        self.assertTrue(all(source.source_kind == "primary_text" for source in self.retriever.sources))

    def test_group_a_query_prioritizes_portaria_50(self):
        result = self.retriever.search("consumidores Grupo A carga individual inferior a 500 kW")
        self.assertEqual(result[0].source.id, "portaria-mme-50-2022")
        self.assertIn("500 kW", result[0].excerpt)
        self.assertEqual(result[0].provision, "art. 1º, § 2º")

    def test_group_a_option_query_recovers_effective_date(self):
        result = self.retriever.search("Grupo A opção compra energia 1 janeiro 2024")
        self.assertEqual(result[0].source.id, "portaria-mme-50-2022")
        self.assertIn("1º de janeiro de 2024", result[0].excerpt)

    def test_varejista_query_recovers_ren_1011(self):
        result = self.retriever.search("gestora informações comercialização varejista CCEE")
        self.assertIn("ren-aneel-1011-2022", {item.source.id for item in result})

    def test_unknown_norm_blocks_generation(self):
        pack = self.retriever.evidence_pack("REN ANEEL 9.999 tarifa municipal inexistente")
        self.assertEqual(pack["status"], "insufficient_evidence")
        self.assertEqual(pack["evidence"], [])

    def test_draft_contains_citation_and_confidence(self):
        pack = self.retriever.evidence_pack(
            "consumidores Grupo A carga individual inferior a 500 kW", limit=1
        )
        draft = compose_auditable_draft(pack)
        self.assertEqual(draft["status"], "draft_ready")
        self.assertIn("PORTARIA nº 50", draft["text"])
        self.assertIn("art. 1º, § 2º", draft["text"])
        self.assertIn("Nível de confiança", draft["text"])

    def test_draft_refuses_insufficient_evidence(self):
        draft = compose_auditable_draft(
            self.retriever.evidence_pack("REN ANEEL 9.999 tarifa municipal inexistente")
        )
        self.assertEqual(draft["status"], "refused")

    def test_normalization_removes_accents_without_losing_tokens(self):
        self.assertEqual(normalize("Comercialização"), "comercializacao")
        self.assertEqual(tokens("Grupo A"), {"grupo"})


if __name__ == "__main__":
    unittest.main()
