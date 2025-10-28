"""
EU Regulatory Compliance API
Integración con EUR-Lex para compliance automático
"""

import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EURLexAPI:
    """API para consultar regulaciones de la UE"""
    
    def __init__(self):
        self.sparql_endpoint = "http://publications.europa.eu/webapi/rdf/sparql"
        self.rest_api = "https://eur-lex.europa.eu/legal-content/EN/TXT/"
        self.sparql = SPARQLWrapper(self.sparql_endpoint)
        
        # CELEX numbers importantes
        self.regulations = {
            'GDPR': '32016R0679',
            'AI_ACT': '52021PC0206',  # Propuesta AI Act
            'NIS2': '32022L2555',
            'DATA_ACT': '52022PC0068',
            'DGA': '32022R0868',  # Data Governance Act
        }
    
    def search_regulations(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        Busca regulaciones por palabra clave
        """
        query = f"""
        PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT DISTINCT ?celex ?title ?date
        WHERE {{
            ?work cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/REGULATION> .
            ?work cdm:resource_legal_id_celex ?celex .
            ?work cdm:work_date_document ?date .
            ?work cdm:work_title ?title .
            FILTER(LANG(?title) = 'en')
            FILTER(CONTAINS(LCASE(?title), LCASE("{keyword}")))
        }}
        ORDER BY DESC(?date)
        LIMIT {limit}
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()
            
            regulations = []
            for result in results["results"]["bindings"]:
                regulations.append({
                    'celex': result['celex']['value'],
                    'title': result['title']['value'],
                    'date': result['date']['value']
                })
            
            logger.info(f"Found {len(regulations)} regulations for '{keyword}'")
            return regulations
            
        except Exception as e:
            logger.error(f"Error searching regulations: {e}")
            return []
    
    def get_regulation_by_celex(self, celex: str) -> Optional[Dict]:
        """
        Obtiene una regulación específica por CELEX
        """
        url = f"{self.rest_api}?uri=CELEX:{celex}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extraer información básica
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else "N/A"
            
            return {
                'celex': celex,
                'title': title_text,
                'url': url,
                'retrieved_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving regulation {celex}: {e}")
            return None
    
    def get_gdpr_requirements(self) -> Dict:
        """
        Obtiene requisitos clave del GDPR
        """
        gdpr_articles = {
            'key_articles': [
                {
                    'article': 'Article 5',
                    'title': 'Principles relating to processing of personal data',
                    'requirements': [
                        'Lawfulness, fairness and transparency',
                        'Purpose limitation',
                        'Data minimisation',
                        'Accuracy',
                        'Storage limitation',
                        'Integrity and confidentiality'
                    ]
                },
                {
                    'article': 'Article 6',
                    'title': 'Lawfulness of processing',
                    'requirements': [
                        'Consent',
                        'Contract',
                        'Legal obligation',
                        'Vital interests',
                        'Public task',
                        'Legitimate interests'
                    ]
                },
                {
                    'article': 'Article 13-14',
                    'title': 'Information to be provided',
                    'requirements': [
                        'Identity of controller',
                        'Purpose of processing',
                        'Legal basis',
                        'Recipients of data',
                        'Retention period',
                        'Rights of data subject'
                    ]
                },
                {
                    'article': 'Article 15-22',
                    'title': 'Rights of data subject',
                    'requirements': [
                        'Right of access',
                        'Right to rectification',
                        'Right to erasure',
                        'Right to restriction',
                        'Right to data portability',
                        'Right to object',
                        'Automated decision-making'
                    ]
                },
                {
                    'article': 'Article 25',
                    'title': 'Data protection by design and by default',
                    'requirements': [
                        'Implement appropriate technical measures',
                        'Ensure only necessary data is processed',
                        'Pseudonymisation where possible'
                    ]
                },
                {
                    'article': 'Article 32',
                    'title': 'Security of processing',
                    'requirements': [
                        'Pseudonymisation and encryption',
                        'Confidentiality, integrity, availability',
                        'Regular testing and evaluation',
                        'Process for restoring availability'
                    ]
                },
                {
                    'article': 'Article 35',
                    'title': 'Data protection impact assessment',
                    'requirements': [
                        'Systematic description of processing',
                        'Assessment of necessity and proportionality',
                        'Assessment of risks',
                        'Measures to address risks'
                    ]
                }
            ],
            'celex': self.regulations['GDPR'],
            'full_name': 'General Data Protection Regulation',
            'effective_date': '2018-05-25'
        }
        
        return gdpr_articles
    
    def get_ai_act_structure(self) -> Dict:
        """
        Obtiene estructura del AI Act
        """
        ai_act = {
            'risk_levels': {
                'unacceptable': {
                    'level': 'Unacceptable Risk',
                    'description': 'Prohibited AI systems',
                    'examples': [
                        'Social scoring by governments',
                        'Real-time biometric identification in public spaces',
                        'Subliminal manipulation',
                        'Exploitation of vulnerabilities'
                    ],
                    'action': 'BANNED'
                },
                'high': {
                    'level': 'High Risk',
                    'description': 'AI systems that pose significant risks',
                    'examples': [
                        'Biometric identification',
                        'Critical infrastructure management',
                        'Educational/vocational training',
                        'Employment and worker management',
                        'Access to essential services',
                        'Law enforcement',
                        'Migration and border control',
                        'Administration of justice'
                    ],
                    'requirements': [
                        'Risk management system',
                        'Data governance',
                        'Technical documentation',
                        'Record-keeping',
                        'Transparency',
                        'Human oversight',
                        'Accuracy, robustness, cybersecurity',
                        'Conformity assessment'
                    ],
                    'action': 'STRICT_COMPLIANCE'
                },
                'limited': {
                    'level': 'Limited Risk',
                    'description': 'AI with transparency obligations',
                    'examples': [
                        'Chatbots',
                        'Emotion recognition',
                        'Biometric categorisation',
                        'Deep fakes'
                    ],
                    'requirements': [
                        'Transparency obligations',
                        'Inform users they are interacting with AI'
                    ],
                    'action': 'TRANSPARENCY_REQUIRED'
                },
                'minimal': {
                    'level': 'Minimal Risk',
                    'description': 'AI with minimal or no risk',
                    'examples': [
                        'Spam filters',
                        'Video games',
                        'Inventory management'
                    ],
                    'requirements': [
                        'Voluntary codes of conduct'
                    ],
                    'action': 'NO_OBLIGATIONS'
                }
            },
            'celex': self.regulations['AI_ACT'],
            'status': 'Proposed (under negotiation)',
            'expected_enforcement': '2024-2026'
        }
        
        return ai_act
    
    def get_nis2_requirements(self) -> Dict:
        """
        Obtiene requisitos de NIS2 Directive (ciberseguridad)
        """
        nis2 = {
            'full_name': 'Network and Information Security Directive 2',
            'celex': self.regulations['NIS2'],
            'scope': [
                'Essential entities',
                'Important entities',
                'Digital infrastructure providers',
                'Public administration'
            ],
            'key_requirements': [
                {
                    'category': 'Risk Management',
                    'measures': [
                        'Policies on risk analysis',
                        'Incident handling',
                        'Business continuity',
                        'Supply chain security',
                        'Security in network and information systems acquisition',
                        'Policies and procedures to assess effectiveness'
                    ]
                },
                {
                    'category': 'Corporate Governance',
                    'measures': [
                        'Management body approval of cybersecurity measures',
                        'Training for management',
                        'Oversight of cybersecurity risk management'
                    ]
                },
                {
                    'category': 'Incident Reporting',
                    'measures': [
                        'Early warning (24 hours)',
                        'Incident notification (72 hours)',
                        'Final report (1 month)',
                        'Significant incidents must be reported'
                    ]
                }
            ],
            'penalties': 'Up to €10M or 2% of global turnover',
            'deadline': '2024-10-17'
        }
        
        return nis2


class ComplianceChecker:
    """Evaluador de compliance para casos de uso de IA"""
    
    def __init__(self):
        self.api = EURLexAPI()
        self.ai_act = self.api.get_ai_act_structure()
        self.gdpr = self.api.get_gdpr_requirements()
        self.nis2 = self.api.get_nis2_requirements()
    
    def assess_ai_risk_level(self, use_case: Dict) -> Dict:
        """
        Evalúa el nivel de riesgo de un caso de uso de IA según AI Act
        """
        risk_level = 'minimal'
        requirements = []
        warnings = []
        
        # Check for unacceptable risk
        if use_case.get('purpose') in ['social_scoring', 'subliminal_manipulation']:
            risk_level = 'unacceptable'
            warnings.append('⛔ PROHIBITED: This use case is banned under AI Act')
            return {
                'risk_level': risk_level,
                'requirements': ['SYSTEM MUST NOT BE DEPLOYED'],
                'warnings': warnings,
                'compliance_status': 'NON_COMPLIANT'
            }
        
        # Check for high risk
        high_risk_sectors = [
            'biometric_identification',
            'critical_infrastructure',
            'education',
            'recruitment',
            'employment',
            'essential_services',
            'law_enforcement',
            'migration',
            'justice'
        ]
        
        if (use_case.get('sector') in high_risk_sectors or
            use_case.get('decision_type') == 'automated' and use_case.get('affects_rights') or
            use_case.get('involves_biometrics')):
            
            risk_level = 'high'
            requirements = self.ai_act['risk_levels']['high']['requirements']
            warnings.append('⚠️ HIGH RISK: Strict compliance requirements apply')
        
        # Check for limited risk
        elif (use_case.get('purpose') in ['chatbot', 'emotion_recognition', 'deepfake'] or
              use_case.get('interacts_with_humans')):
            risk_level = 'limited'
            requirements = self.ai_act['risk_levels']['limited']['requirements']
            warnings.append('ℹ️ LIMITED RISK: Transparency obligations apply')
        
        # GDPR considerations
        if use_case.get('processes_personal_data'):
            requirements.append('GDPR compliance required')
            requirements.extend([
                'Data protection impact assessment (DPIA)',
                'Legal basis for processing',
                'Data subject rights implementation',
                'Security measures (Art. 32)'
            ])
        
        # Automated decision-making (GDPR Art. 22)
        if use_case.get('decision_type') == 'automated' and use_case.get('affects_rights'):
            requirements.append('GDPR Art. 22: Right not to be subject to automated decision-making')
            requirements.append('Human oversight required')
            warnings.append('⚠️ GDPR Art. 22 applies: Automated decisions with legal/significant effects')
        
        compliance_status = 'COMPLIANT' if risk_level in ['minimal', 'limited'] else 'REQUIRES_ASSESSMENT'
        
        return {
            'risk_level': risk_level,
            'requirements': requirements,
            'warnings': warnings,
            'compliance_status': compliance_status,
            'applicable_regulations': self._get_applicable_regulations(use_case)
        }
    
    def _get_applicable_regulations(self, use_case: Dict) -> List[str]:
        """Determina qué regulaciones aplican"""
        regulations = []
        
        if use_case.get('processes_personal_data'):
            regulations.append('GDPR (32016R0679)')
        
        if use_case.get('uses_ai'):
            regulations.append('AI Act (52021PC0206)')
        
        if use_case.get('sector') in ['critical_infrastructure', 'essential_services']:
            regulations.append('NIS2 Directive (32022L2555)')
        
        if use_case.get('involves_data_sharing'):
            regulations.append('Data Governance Act (32022R0868)')
        
        return regulations
    
    def generate_compliance_report(self, project_name: str, use_cases: List[Dict]) -> str:
        """
        Genera reporte completo de compliance
        """
        report = []
        report.append("=" * 80)
        report.append(f"EU REGULATORY COMPLIANCE REPORT")
        report.append(f"Project: {project_name}")
        report.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        risk_counts = {'unacceptable': 0, 'high': 0, 'limited': 0, 'minimal': 0}
        
        for i, use_case in enumerate(use_cases, 1):
            assessment = self.assess_ai_risk_level(use_case)
            risk_counts[assessment['risk_level']] += 1
            
            report.append(f"\n{'='*80}")
            report.append(f"USE CASE #{i}: {use_case.get('purpose', 'Unnamed')}")
            report.append(f"{'='*80}")
            report.append(f"Risk Level: {assessment['risk_level'].upper()}")
            report.append(f"Compliance Status: {assessment['compliance_status']}")
            report.append("")
            
            if assessment['warnings']:
                report.append("⚠️ WARNINGS:")
                for warning in assessment['warnings']:
                    report.append(f"  {warning}")
                report.append("")
            
            report.append("📋 REQUIREMENTS:")
            for req in assessment['requirements']:
                report.append(f"  • {req}")
            report.append("")
            
            report.append("📜 APPLICABLE REGULATIONS:")
            for reg in assessment['applicable_regulations']:
                report.append(f"  • {reg}")
            report.append("")
        
        # Overall summary
        report.append("\n" + "=" * 80)
        report.append("SUMMARY")
        report.append("=" * 80)
        report.append(f"Total Use Cases: {len(use_cases)}")
        report.append(f"  • Unacceptable Risk: {risk_counts['unacceptable']}")
        report.append(f"  • High Risk: {risk_counts['high']}")
        report.append(f"  • Limited Risk: {risk_counts['limited']}")
        report.append(f"  • Minimal Risk: {risk_counts['minimal']}")
        report.append("")
        
        if risk_counts['unacceptable'] > 0:
            report.append("🚨 CRITICAL: Some use cases are PROHIBITED under EU regulations")
        elif risk_counts['high'] > 0:
            report.append("⚠️ ACTION REQUIRED: High-risk systems require strict compliance")
        else:
            report.append("✅ No high-risk or prohibited use cases detected")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def check_credit_scoring_compliance(self, model_info: Dict) -> Dict:
        """
        Verifica compliance específico para modelos de credit scoring
        """
        compliance_checks = {
            'gdpr_compliance': [],
            'ai_act_compliance': [],
            'transparency': [],
            'fairness': [],
            'status': 'COMPLIANT'
        }
        
        # GDPR checks
        if model_info.get('processes_personal_data'):
            compliance_checks['gdpr_compliance'].append({
                'requirement': 'Legal basis for processing',
                'status': 'REQUIRED',
                'article': 'GDPR Art. 6'
            })
            compliance_checks['gdpr_compliance'].append({
                'requirement': 'Data protection impact assessment',
                'status': 'REQUIRED',
                'article': 'GDPR Art. 35'
            })
            compliance_checks['gdpr_compliance'].append({
                'requirement': 'Right to explanation',
                'status': 'REQUIRED',
                'article': 'GDPR Art. 13-14, 22'
            })
        
        # AI Act checks (High Risk - Credit Scoring)
        compliance_checks['ai_act_compliance'].append({
            'requirement': 'Risk management system',
            'status': 'REQUIRED',
            'category': 'High Risk AI'
        })
        compliance_checks['ai_act_compliance'].append({
            'requirement': 'Data governance and quality',
            'status': 'REQUIRED',
            'category': 'High Risk AI'
        })
        compliance_checks['ai_act_compliance'].append({
            'requirement': 'Technical documentation',
            'status': 'REQUIRED',
            'category': 'High Risk AI'
        })
        compliance_checks['ai_act_compliance'].append({
            'requirement': 'Human oversight',
            'status': 'REQUIRED',
            'category': 'High Risk AI'
        })
        
        # Transparency checks
        if model_info.get('model_type'):
            compliance_checks['transparency'].append({
                'item': 'Model type disclosed',
                'value': model_info['model_type'],
                'status': '✅'
            })
        
        if model_info.get('features'):
            compliance_checks['transparency'].append({
                'item': 'Features used',
                'value': f"{len(model_info['features'])} features",
                'status': '✅'
            })
        
        if model_info.get('accuracy'):
            compliance_checks['transparency'].append({
                'item': 'Model accuracy',
                'value': f"{model_info['accuracy']:.2%}",
                'status': '✅'
            })
        
        # Fairness checks
        if model_info.get('protected_attributes'):
            compliance_checks['fairness'].append({
                'check': 'Protected attributes handling',
                'attributes': model_info['protected_attributes'],
                'status': 'REVIEW_REQUIRED'
            })
        
        if model_info.get('bias_mitigation'):
            compliance_checks['fairness'].append({
                'check': 'Bias mitigation',
                'implemented': model_info['bias_mitigation'],
                'status': '✅'
            })
        
        return compliance_checks


if __name__ == "__main__":
    # Test API
    print("🔍 Testing EU Regulatory API...\n")
    
    api = EURLexAPI()
    
    # Search AI regulations
    print("1. Searching for AI regulations...")
    ai_regs = api.search_regulations("artificial intelligence", limit=3)
    for reg in ai_regs:
        print(f"  • {reg['celex']}: {reg['title'][:80]}...")
    
    print("\n2. GDPR Key Articles:")
    gdpr = api.get_gdpr_requirements()
    for article in gdpr['key_articles'][:3]:
        print(f"  • {article['article']}: {article['title']}")
    
    print("\n3. AI Act Risk Levels:")
    ai_act = api.get_ai_act_structure()
    for level, info in ai_act['risk_levels'].items():
        print(f"  • {info['level']}: {info['action']}")
    
    # Test compliance checker
    print("\n4. Testing Compliance Checker...")
    checker = ComplianceChecker()
    
    use_case = {
        "purpose": "AI-powered credit scoring",
        "sector": "essential_services",
        "decision_type": "automated",
        "involves_biometrics": False,
        "affects_rights": True,
        "processes_personal_data": True,
        "uses_ai": True
    }
    
    assessment = checker.assess_ai_risk_level(use_case)
    print(f"  Risk Level: {assessment['risk_level'].upper()}")
    print(f"  Status: {assessment['compliance_status']}")
    print(f"  Requirements: {len(assessment['requirements'])}")
    
    print("\n✅ API Test Complete!")
