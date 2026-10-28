from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StaticContractTests(unittest.TestCase):
    def test_frontend_has_no_runtime_tailwind_or_external_script(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("cdn.jsdelivr.net", html)
        self.assertNotIn("tailwindcss/browser", html)
        self.assertNotIn("<script src=\"http", html)

    def test_workflow_has_no_schedule_or_repository_write_permission(self):
        workflow = (ROOT / ".github" / "workflows" / "refresh-catalog.yml").read_text(encoding="utf-8")
        self.assertNotIn("schedule:", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("needs: validate", workflow)
        self.assertIn("node tests/catalog_ui.test.cjs", workflow)
        self.assertIn("node --check app.js", workflow)
        self.assertNotIn("collector.refresh_catalog", workflow)
        self.assertIn("python scripts/pages_artifact.py --output dist", workflow)
        self.assertIn("needs: validate", workflow)
        self.assertIn("path: dist", workflow)
        self.assertLess(workflow.index("python scripts/pages_artifact.py --output dist"), workflow.index("uses: actions/upload-pages-artifact@v3"))
        self.assertLess(workflow.index("python scripts/pages_artifact.py --output dist"), workflow.index("uses: actions/deploy-pages@v4"))
        self.assertNotIn("continue-on-error: true", workflow)

    def test_opportunity_details_distinguish_employer_publisher_and_apply_channel(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("Entidad que difunde", app)
        self.assertIn("Ficha informativa", app)
        self.assertIn("Procedencia por dato", app)
        self.assertIn("const applyUrl = safeHttpsUrl(job.applyUrl);", app)
        self.assertNotIn("job.applyUrl || job.sourceUrl", app)
        self.assertIn("No hay evidencia desglosada por campo", app)

    def test_demonstrations_are_opt_in_and_excluded_from_real_metrics(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="include-demonstrations"', html)
        self.assertIn("Incluir ejemplos demostrativos", html)
        self.assertNotRegex(html, r'<input[^>]*id="include-demonstrations"[^>]*checked')
        self.assertIn("if (demonstration && !includeDemonstrations) return false", app)
        self.assertIn("job.recordKind !== 'demonstration'", app)
        self.assertIn("const realJobs = catalog.filter((job) => job.recordKind !== 'demonstration')", app)
        self.assertIn("No hay oportunidades verificadas disponibles", html)
        self.assertIn("Las oportunidades se incorporan después de revisar", html)

    def test_demonstrations_never_receive_a_postulation_cta(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("state.publicationStatus === 'active' && job.recordKind !== 'demonstration'", app)
        self.assertIn("const applyUrl = safeHttpsUrl(job.applyUrl);", app)

    def test_malformed_catalog_fails_closed_and_shows_load_error(self):
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("if (!isValidCatalogPayload(result)) throw new Error", app)
        self.assertIn("No se pudo cargar el catálogo", app)
        self.assertIn("No se pudo cargar el catálogo. Reintenta", app)
        self.assertIn("fetch('./data/opportunities.json'", app)

    def test_primary_controls_are_keyboard_labeled_and_mobile_layout_exists(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn('<label class="history-toggle"><input type="checkbox" id="include-demonstrations"', html)
        self.assertIn('role="button" tabindex="0" data-open=', app)
        self.assertIn("list.addEventListener('keydown'", app)
        self.assertIn("@media(max-width:520px)", css)


if __name__ == "__main__":
    unittest.main()
