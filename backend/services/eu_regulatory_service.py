"""
EU Regulatory API Service
Integrates with EUR-Lex for GDPR, AI Act, and other EU regulations
"""
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)


class EURegulatoryService:
    """
    Service for interacting with EU regulatory databases
    - EUR-Lex: Official EU legislation database
    - SPARQL endpoint for semantic queries
    """
    
    def __init__(self):
        self.eurlex_sparql = SPARQLWrapper(
            "http://publications.europa.eu/webapi/rdf/sparql"
        )
        self.eurlex_sparql.setReturnFormat(JSON)
        self.eurlex_rest = "https://eur-lex.europa.eu/legal-content"
        
        # Known regulation CELEX numbers
        self.REGULATIONS = {
            "GDPR": "32016R0679",
            "AI_ACT": "32024R1689",  # AI Act (when published)
            "DSA": "32022R2065",  # Digital Services Act
            "DGA": "32022R0868",  # Data Governance Act
            "NIS2": "32022L2555",  # Network and Information Security Directive
        }
    
    async def search_regulations(
        self, 
        keyword: str, 
        limit: int = 10,
        language: str = "EN"
    ) -> List[Dict]:
        """
        Search EU regulations by keyword using SPARQL
        
        Args:
            keyword: Search term (e.g., "artificial intelligence", "data protection")
            limit: Maximum number of results
            language: Language code (EN, ES, FR, etc.)
            
        Returns:
            List of regulation metadata
        """
        try:
            query = f'''
            PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            
            SELECT DISTINCT ?work ?celex ?title ?date ?type
            WHERE {{
              ?work cdm:work_has_expression ?expr .
              ?expr cdm:expression_title ?title .
              ?work cdm:work_date_document ?date .
              ?work cdm:resource_legal_id_celex ?celex .
              ?work cdm:work_is_about_concept_directory_code ?type .
              
              FILTER (
                CONTAINS(LCASE(STR(?title)), LCASE("{keyword}")) ||
                CONTAINS(LCASE(STR(?celex)), LCASE("{keyword}"))
              )
              FILTER (LANG(?title) = "{language}" || LANG(?title) = "")
            }}
            ORDER BY DESC(?date)
            LIMIT {limit}
            '''
            
            # Execute query asynchronously
            loop = asyncio.get_event_loop()
            self.eurlex_sparql.setQuery(query)
            results = await loop.run_in_executor(None, self.eurlex_sparql.query)
            data = results.convert()
            
            regulations = []
            for result in data.get("results", {}).get("bindings", []):
                regulations.append({
                    "celex": result.get("celex", {}).get("value", ""),
                    "title": result.get("title", {}).get("value", ""),
                    "date": result.get("date", {}).get("value", ""),
                    "url": result.get("work", {}).get("value", ""),
                    "type": result.get("type", {}).get("value", "")
                })
            
            logger.info(f"Found {len(regulations)} regulations for keyword: {keyword}")
            return regulations
            
        except Exception as e:
            logger.error(f"Error searching regulations: {str(e)}")
            # Return empty list on error to not break the application
            return []
    
    @lru_cache(maxsize=10)
    def get_gdpr_articles_cached(self) -> List[Dict]:
        """Cached version of GDPR articles retrieval"""
        return self._get_gdpr_articles_sync()
    
    def _get_gdpr_articles_sync(self) -> List[Dict]:
        """
        Synchronous helper to get GDPR articles
        This is cached to avoid repeated API calls
        """
        key_articles = [
            {
                "article": "Article 5",
                "title": "Principles relating to processing of personal data",
                "requirements": [
                    "Lawfulness, fairness and transparency",
                    "Purpose limitation",
                    "Data minimization",
                    "Accuracy",
                    "Storage limitation",
                    "Integrity and confidentiality"
                ],
                "risk_level": "HIGH"
            },
            {
                "article": "Article 6",
                "title": "Lawfulness of processing",
                "requirements": [
                    "Consent of data subject",
                    "Performance of contract",
                    "Legal obligation",
                    "Vital interests",
                    "Public interest",
                    "Legitimate interests"
                ],
                "risk_level": "HIGH"
            },
            {
                "article": "Article 9",
                "title": "Processing of special categories of personal data",
                "requirements": [
                    "Explicit consent required",
                    "Employment and social security law",
                    "Vital interests",
                    "Foundations, associations, etc.",
                    "Data manifestly made public",
                    "Legal claims",
                    "Substantial public interest",
                    "Health or social care",
                    "Public health",
                    "Archiving, research, statistics"
                ],
                "risk_level": "CRITICAL"
            },
            {
                "article": "Article 15",
                "title": "Right of access by the data subject",
                "requirements": [
                    "Confirmation of processing",
                    "Access to personal data",
                    "Information about processing"
                ],
                "risk_level": "MEDIUM"
            },
            {
                "article": "Article 17",
                "title": "Right to erasure ('right to be forgotten')",
                "requirements": [
                    "Data no longer necessary",
                    "Withdrawal of consent",
                    "Objection to processing",
                    "Unlawful processing",
                    "Legal obligation"
                ],
                "risk_level": "HIGH"
            },
            {
                "article": "Article 25",
                "title": "Data protection by design and by default",
                "requirements": [
                    "Implement appropriate technical measures",
                    "Implement appropriate organizational measures",
                    "Data minimization by default",
                    "Pseudonymization where possible"
                ],
                "risk_level": "HIGH"
            },
            {
                "article": "Article 32",
                "title": "Security of processing",
                "requirements": [
                    "Pseudonymization and encryption",
                    "Ensure ongoing confidentiality",
                    "Ensure ongoing integrity",
                    "Ensure ongoing availability",
                    "Ensure resilience of systems",
                    "Testing and evaluation procedures"
                ],
                "risk_level": "HIGH"
            },
            {
                "article": "Article 35",
                "title": "Data protection impact assessment",
                "requirements": [
                    "DPIA for high-risk processing",
                    "Systematic description of processing",
                    "Assessment of necessity and proportionality",
                    "Assessment of risks to rights and freedoms",
                    "Measures to address risks"
                ],
                "risk_level": "HIGH"
            }
        ]
        
        return key_articles
    
    async def get_gdpr_requirements(self) -> Dict:
        """
        Get GDPR key articles and requirements
        
        Returns:
            Dictionary with GDPR articles and metadata
        """
        try:
            key_articles = self.get_gdpr_articles_cached()
            
            return {
                "regulation": "GDPR",
                "celex": self.REGULATIONS["GDPR"],
                "full_name": "General Data Protection Regulation",
                "effective_date": "2018-05-25",
                "key_articles": key_articles,
                "total_articles": len(key_articles),
                "url": f"{self.eurlex_rest}/EN/TXT/?uri=CELEX:{self.REGULATIONS['GDPR']}"
            }
            
        except Exception as e:
            logger.error(f"Error getting GDPR requirements: {str(e)}")
            return {
                "regulation": "GDPR",
                "error": str(e),
                "key_articles": []
            }
    
    async def get_ai_act_requirements(self, risk_level: str) -> Dict:
        """
        Get AI Act requirements based on risk level
        
        Args:
            risk_level: One of UNACCEPTABLE, HIGH, LIMITED, MINIMAL
            
        Returns:
            Requirements for the specified risk level
        """
        risk_requirements = {
            "UNACCEPTABLE": {
                "level": "UNACCEPTABLE",
                "action": "PROHIBITED",
                "description": "AI systems that pose unacceptable risk are prohibited",
                "examples": [
                    "Social scoring by governments",
                    "Real-time biometric identification in public spaces (with exceptions)",
                    "Subliminal manipulation",
                    "Exploitation of vulnerabilities"
                ],
                "requirements": ["Complete prohibition of deployment"],
                "penalties": "Up to €30 million or 6% of annual worldwide turnover"
            },
            "HIGH": {
                "level": "HIGH",
                "action": "STRICT REQUIREMENTS",
                "description": "High-risk AI systems must comply with strict requirements",
                "examples": [
                    "Critical infrastructure",
                    "Education and vocational training",
                    "Employment and worker management",
                    "Essential private and public services",
                    "Law enforcement",
                    "Migration, asylum and border control",
                    "Administration of justice"
                ],
                "requirements": [
                    "Risk management system",
                    "Data governance and quality",
                    "Technical documentation",
                    "Record keeping and logging",
                    "Transparency and information provision",
                    "Human oversight",
                    "Accuracy, robustness and cybersecurity",
                    "Conformity assessment before market placement",
                    "Registration in EU database",
                    "Post-market monitoring"
                ],
                "penalties": "Up to €20 million or 4% of annual worldwide turnover"
            },
            "LIMITED": {
                "level": "LIMITED",
                "action": "TRANSPARENCY OBLIGATIONS",
                "description": "Limited risk AI must ensure transparency",
                "examples": [
                    "Chatbots and conversational agents",
                    "Emotion recognition systems",
                    "Biometric categorization systems",
                    "AI-generated content (deepfakes)"
                ],
                "requirements": [
                    "Users must be informed they are interacting with AI",
                    "AI-generated content must be clearly labeled",
                    "Transparency about AI system capabilities and limitations"
                ],
                "penalties": "Up to €10 million or 2% of annual worldwide turnover"
            },
            "MINIMAL": {
                "level": "MINIMAL",
                "action": "NO SPECIFIC OBLIGATIONS",
                "description": "Minimal risk AI systems have no specific obligations",
                "examples": [
                    "AI-enabled video games",
                    "Spam filters",
                    "General purpose AI systems"
                ],
                "requirements": [
                    "Voluntary codes of conduct encouraged",
                    "Self-regulation recommended"
                ],
                "penalties": "None specified"
            }
        }
        
        risk_level_upper = risk_level.upper()
        if risk_level_upper not in risk_requirements:
            risk_level_upper = "MINIMAL"
        
        return {
            "regulation": "AI Act",
            "celex": self.REGULATIONS.get("AI_ACT", "TBD"),
            "full_name": "Artificial Intelligence Act",
            "risk_level": risk_level_upper,
            **risk_requirements[risk_level_upper]
        }
    
    async def check_document_compliance(
        self, 
        document_content: str, 
        document_title: str,
        regulations: List[str]
    ) -> Dict:
        """
        Check document compliance against specified regulations
        
        NOTE: This is a basic implementation. For production, this would need:
        - NLP analysis of document content
        - Machine learning models for clause detection
        - Legal expertise integration
        
        Args:
            document_content: Text content of document
            document_title: Document title
            regulations: List of regulation codes to check (e.g., ['GDPR', 'AI_ACT'])
            
        Returns:
            Compliance report with violations and recommendations
        """
        violations = []
        recommendations = []
        checked_regulations = []
        
        for regulation in regulations:
            if regulation == "GDPR":
                gdpr_data = await self.get_gdpr_requirements()
                checked_regulations.append({
                    "code": "GDPR",
                    "name": "General Data Protection Regulation",
                    "checked": True
                })
                
                # Basic keyword-based compliance checks
                content_lower = document_content.lower()
                
                # Check for consent mentions
                if "personal data" in content_lower or "personal information" in content_lower:
                    if "consent" not in content_lower:
                        violations.append({
                            "regulation": "GDPR",
                            "article": "Article 6",
                            "description": "Document mentions personal data but does not explicitly reference consent requirements",
                            "severity": "high"
                        })
                        recommendations.append(
                            "Add explicit consent clauses when processing personal data"
                        )
                
                # Check for data subject rights
                if "personal data" in content_lower:
                    rights_keywords = ["right to access", "right to erasure", "right to be forgotten"]
                    if not any(keyword in content_lower for keyword in rights_keywords):
                        violations.append({
                            "regulation": "GDPR",
                            "article": "Article 15-17",
                            "description": "Document does not mention data subject rights (access, erasure, etc.)",
                            "severity": "medium"
                        })
                        recommendations.append(
                            "Include information about data subject rights (access, rectification, erasure)"
                        )
                
                # Check for security measures
                if "data" in content_lower or "information" in content_lower:
                    security_keywords = ["encryption", "security", "protection", "safeguard"]
                    if not any(keyword in content_lower for keyword in security_keywords):
                        violations.append({
                            "regulation": "GDPR",
                            "article": "Article 32",
                            "description": "Document does not reference security measures for data protection",
                            "severity": "high"
                        })
                        recommendations.append(
                            "Specify technical and organizational security measures (encryption, access controls, etc.)"
                        )
            
            elif regulation == "AI_ACT":
                checked_regulations.append({
                    "code": "AI_ACT",
                    "name": "Artificial Intelligence Act",
                    "checked": True
                })
                
                content_lower = document_content.lower()
                
                # Check for AI transparency
                ai_keywords = ["artificial intelligence", "machine learning", "ai system", "automated decision"]
                if any(keyword in content_lower for keyword in ai_keywords):
                    if "transparency" not in content_lower and "explainability" not in content_lower:
                        violations.append({
                            "regulation": "AI Act",
                            "article": "Transparency Requirements",
                            "description": "Document references AI but does not address transparency obligations",
                            "severity": "medium"
                        })
                        recommendations.append(
                            "Add transparency disclosures for AI systems (how they work, limitations, etc.)"
                        )
                    
                    # Check for human oversight
                    if "human oversight" not in content_lower and "human supervision" not in content_lower:
                        violations.append({
                            "regulation": "AI Act",
                            "article": "Human Oversight Requirements",
                            "description": "Document does not mention human oversight of AI systems",
                            "severity": "high"
                        })
                        recommendations.append(
                            "Include provisions for human oversight and intervention in AI-driven processes"
                        )
        
        # Determine overall compliance status
        if not violations:
            compliance_status = "compliant"
        elif any(v["severity"] == "high" for v in violations):
            compliance_status = "non_compliant"
        else:
            compliance_status = "partial"
        
        return {
            "document_title": document_title,
            "regulations_checked": checked_regulations,
            "compliance_status": compliance_status,
            "violations": violations,
            "recommendations": recommendations,
            "checked_at": datetime.utcnow().isoformat(),
            "total_violations": len(violations),
            "high_severity_violations": len([v for v in violations if v["severity"] == "high"]),
            "summary": self._generate_compliance_summary(compliance_status, violations)
        }
    
    def _generate_compliance_summary(self, status: str, violations: List[Dict]) -> str:
        """Generate human-readable compliance summary"""
        if status == "compliant":
            return "Document appears to be compliant with checked regulations. No violations detected."
        elif status == "non_compliant":
            high_sev = len([v for v in violations if v["severity"] == "high"])
            return f"Document has {len(violations)} compliance issues, including {high_sev} high-severity violations requiring immediate attention."
        else:
            return f"Document has {len(violations)} minor compliance issues. Review and address recommendations to ensure full compliance."


# Global instance
_eu_regulatory_service = None

def get_eu_regulatory_service() -> EURegulatoryService:
    """Get or create singleton instance of EU Regulatory Service"""
    global _eu_regulatory_service
    if _eu_regulatory_service is None:
        _eu_regulatory_service = EURegulatoryService()
    return _eu_regulatory_service
