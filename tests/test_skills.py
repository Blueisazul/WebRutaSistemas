"""Unit tests for technical skills extraction, normalization, and opportunity comparison.

TASK-R7-02: Comparador de Trayectorias y Requisitos Técnicos.
Verifies:
- Deterministic extraction and alias normalization (AWS, Postgres, TypeScript, etc.).
- False-positive prevention (C vs Conocimientos, Java vs JavaScript, Redes vs Redes sociales).
- Priority classification: REQUIRED, PREFERRED, MENTIONED, UNSPECIFIED.
- Opportunity contrast: shared skills, exclusive skills, priority divergence.
- Explicit handling of unstated/empty skills and requirements.
- Full traceability with source fields and context excerpts.
"""

from __future__ import annotations

import unittest

from collector.skills import (
    PRIORITY_MENTIONED,
    PRIORITY_PREFERRED,
    PRIORITY_REQUIRED,
    SKILL_TAXONOMY,
    compare_opportunity_skills,
    extract_skills_from_opportunity,
)


class TestSkillsExtractionAndNormalization(unittest.TestCase):
    """Tests technical skills detection, alias normalization, and false-positive guards."""

    def test_alias_normalization(self):
        job = {
            "title": "Ingeniero Backend",
            "skills": "Postgres · Amazon Web Services · Microsoft Azure · TS · K8s · Golang",
        }
        skills = extract_skills_from_opportunity(job)
        self.assertIn("PostgreSQL", skills)
        self.assertEqual(skills["PostgreSQL"].canonical, "PostgreSQL")
        self.assertIn("AWS", skills)
        self.assertEqual(skills["AWS"].canonical, "AWS")
        self.assertIn("Azure", skills)
        self.assertEqual(skills["Azure"].canonical, "Azure")
        self.assertIn("TypeScript", skills)
        self.assertEqual(skills["TypeScript"].canonical, "TypeScript")
        self.assertIn("Kubernetes", skills)
        self.assertEqual(skills["Kubernetes"].canonical, "Kubernetes")
        self.assertIn("Go", skills)
        self.assertEqual(skills["Go"].canonical, "Go")

    def test_false_positive_guard_c_language(self):
        # 'Conocimientos' or 'Comunicación' must NOT trigger C
        job = {
            "title": "Analista de Sistemas",
            "requirements": "Conocimientos generales; comunicación asertiva; capacidad de análisis",
        }
        skills = extract_skills_from_opportunity(job)
        self.assertNotIn("C", skills)

        # Legitimate C language pattern should trigger
        job_c = {
            "title": "Desarrollador de Firmware",
            "requirements": "Programación en C y C++; depuración de controladores",
        }
        skills_c = extract_skills_from_opportunity(job_c)
        self.assertIn("C", skills_c)
        self.assertIn("C++", skills_c)

    def test_false_positive_guard_java_vs_javascript(self):
        job_java = {
            "title": "Java Backend Engineer",
            "requirements": "Experiencia sólida en Java y Spring Boot",
        }
        skills_java = extract_skills_from_opportunity(job_java)
        self.assertIn("Java", skills_java)
        self.assertNotIn("JavaScript", skills_java)

        job_js = {
            "title": "Frontend Engineer",
            "requirements": "Dominio de JavaScript moderno y React",
        }
        skills_js = extract_skills_from_opportunity(job_js)
        self.assertIn("JavaScript", skills_js)
        self.assertNotIn("Java", skills_js)

    def test_false_positive_guard_redes_sociales(self):
        job = {
            "title": "Especialista en Marketing Digital",
            "tasks": "Administrar redes sociales y campañas de difusión",
        }
        skills = extract_skills_from_opportunity(job)
        self.assertNotIn("Redes", skills)

        job_infra = {
            "title": "Ingeniero de Redes y Telecomunicaciones",
            "requirements": "Experiencia en configuración de redes de datos y switches Cisco",
        }
        skills_infra = extract_skills_from_opportunity(job_infra)
        self.assertIn("Redes", skills_infra)

    def test_false_positive_guard_sql_server(self):
        job = {
            "title": "DBA SQL Server",
            "skills": "SQL Server · Transact-SQL",
        }
        skills = extract_skills_from_opportunity(job)
        self.assertIn("SQL Server", skills)
        self.assertNotIn("SQL", skills)  # Generic SQL is excluded by negative lookahead


class TestPriorityClassification(unittest.TestCase):
    """Tests priority determination: REQUIRED vs PREFERRED vs MENTIONED."""

    def test_required_in_requirements_field(self):
        job = {
            "title": "Python Developer",
            "requirements": "Requisito indispensable: 2 años de experiencia en Python; conocimiento en Docker",
        }
        skills = extract_skills_from_opportunity(job)
        self.assertEqual(skills["Python"].priority, PRIORITY_REQUIRED)
        self.assertEqual(skills["Docker"].priority, PRIORITY_REQUIRED)

    def test_preferred_in_requirements_clause(self):
        job = {
            "title": "Backend Developer",
            "requirements": "Experiencia obligatoria en Python; deseable conocimiento en Kubernetes; plus si manejas Terraform",
        }
        skills = extract_skills_from_opportunity(job)
        self.assertEqual(skills["Python"].priority, PRIORITY_REQUIRED)
        self.assertEqual(skills["Kubernetes"].priority, PRIORITY_PREFERRED)
        self.assertEqual(skills["Terraform"].priority, PRIORITY_PREFERRED)

    def test_mentioned_in_tasks_field(self):
        job = {
            "title": "Analista de Soporte",
            "tasks": "Coordinar despliegues de microservicios usando Docker en servidores Linux",
        }
        skills = extract_skills_from_opportunity(job)
        self.assertEqual(skills["Docker"].priority, PRIORITY_MENTIONED)
        self.assertEqual(skills["Linux"].priority, PRIORITY_MENTIONED)

    def test_priority_upgrade_when_repeated(self):
        # If mentioned in tasks first, but required in requirements, upgrade to REQUIRED
        job = {
            "title": "Fullstack Developer",
            "tasks": "Desarrollar vistas usando React",
            "requirements": "Requisito indispensable: dominio avanzado de React",
        }
        skills = extract_skills_from_opportunity(job)
        self.assertEqual(skills["React"].priority, PRIORITY_REQUIRED)


class TestOpportunityComparison(unittest.TestCase):
    """Tests comparative contrast: shared skills, exclusive skills, and limitations."""

    def setUp(self):
        self.job_a = {
            "id": "JOB-A",
            "employer": "TechCorp",
            "title": "Senior Cloud Engineer",
            "skills": "Python · AWS · Docker · Terraform",
            "requirements": "Experiencia obligatoria en Python y AWS; deseable Docker",
        }
        self.job_b = {
            "id": "JOB-B",
            "employer": "FinBank",
            "title": "Backend Microservices Developer",
            "skills": "Python · Docker · Kubernetes · Java",
            "requirements": "Indispensable Java y Python; deseable Kubernetes",
        }

    def test_shared_and_exclusive_skills(self):
        res = compare_opportunity_skills(self.job_a, self.job_b)

        # Shared skills: Python and Docker
        shared_names = [s["canonical"] for s in res.shared_skills]
        self.assertIn("Python", shared_names)
        self.assertIn("Docker", shared_names)
        self.assertEqual(len(shared_names), 2)

        # Exclusive to A: AWS, Terraform
        exclusive_a_names = [s["canonical"] for s in res.exclusive_a]
        self.assertIn("AWS", exclusive_a_names)
        self.assertIn("Terraform", exclusive_a_names)
        self.assertNotIn("Python", exclusive_a_names)

        # Exclusive to B: Java, Kubernetes
        exclusive_b_names = [s["canonical"] for s in res.exclusive_b]
        self.assertIn("Java", exclusive_b_names)
        self.assertIn("Kubernetes", exclusive_b_names)
        self.assertNotIn("Docker", exclusive_b_names)

    def test_priority_divergence_in_shared_skills(self):
        res = compare_opportunity_skills(self.job_a, self.job_b)
        python_shared = next(s for s in res.shared_skills if s["canonical"] == "Python")
        self.assertEqual(python_shared["priorityA"], PRIORITY_REQUIRED)
        self.assertEqual(python_shared["priorityB"], PRIORITY_REQUIRED)

        docker_shared = next(s for s in res.shared_skills if s["canonical"] == "Docker")
        # In Job A: deseable Docker -> PREFERRED
        # In Job B: listed in skills without deseable -> REQUIRED
        self.assertEqual(docker_shared["priorityA"], PRIORITY_PREFERRED)
        self.assertEqual(docker_shared["priorityB"], PRIORITY_REQUIRED)

    def test_unspecified_skills_graceful_handling(self):
        job_empty = {
            "id": "JOB-EMPTY",
            "employer": "Entidad Sin Tecnologías",
            "title": "Asistente Administrativo",
        }
        res = compare_opportunity_skills(self.job_a, job_empty)
        self.assertFalse(res.is_a_unspecified)
        self.assertTrue(res.is_b_unspecified)
        self.assertEqual(len(res.shared_skills), 0)
        self.assertEqual(len(res.exclusive_b), 0)
        self.assertEqual(len(res.exclusive_a), 4)

    def test_traceability_information(self):
        skills = extract_skills_from_opportunity(self.job_a)
        aws_skill = skills["AWS"]
        self.assertEqual(aws_skill.source_field, "requirements")
        self.assertIn("AWS", aws_skill.context)
        self.assertEqual(aws_skill.canonical, "AWS")


if __name__ == "__main__":
    unittest.main()
