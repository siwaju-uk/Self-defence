"""
Initialize sample legal data for the UK Legal Chatbot
This script should be run within Flask application context
"""

from app import app, db
from models import LegalCase, LegalKnowledge, SolicitorReferral
import logging

def initialize_sample_legal_cases():
    """Initialize sample legal case data"""
    sample_cases = [
        {
            'case_name': 'Dunlop Pneumatic Tyre Co Ltd v New Garage and Motor Co Ltd',
            'citation': '[1915] AC 79',
            'court': 'House of Lords',
            'year': 1915,
            'track_type': 'multi_track',
            'claim_value': 5000000,  # Historical value in pence
            'case_summary': 'Landmark case establishing the difference between penalty clauses and liquidated damages in contract law.',
            'legal_principles': 'Penalty clauses are unenforceable if they are disproportionate to the actual loss. Liquidated damages must be a genuine pre-estimate of loss.',
            'url': 'https://www.bailii.org/uk/cases/UKHL/1915/1.html'
        },
        {
            'case_name': 'Hadley v Baxendale',
            'citation': '(1854) 9 Exch 341',
            'court': 'Court of Exchequer',
            'year': 1854,
            'track_type': 'fast_track',
            'claim_value': 2500000,
            'case_summary': 'Established the test for remoteness of damage in contract law.',
            'legal_principles': 'Damages for breach of contract are limited to losses that arise naturally from the breach or were reasonably foreseeable.',
            'url': 'https://www.bailii.org/ew/cases/EWHC/Exch/1854/J70.html'
        },
        {
            'case_name': 'Jarvis v Swans Tours Ltd',
            'citation': '[1973] QB 233',
            'court': 'Court of Appeal',
            'year': 1973,
            'track_type': 'small_claims',
            'claim_value': 31050,  # £31.05 in 1973
            'case_summary': 'Established that damages for disappointment and distress can be recovered in consumer contracts.',
            'legal_principles': 'Non-pecuniary losses including disappointment and distress are recoverable in consumer contracts for holidays and leisure.',
            'url': 'https://www.bailii.org/ew/cases/EWCA/Civ/1972/12.html'
        },
        {
            'case_name': 'Caparo Industries plc v Dickman',
            'citation': '[1990] 2 AC 605',
            'court': 'House of Lords',
            'year': 1990,
            'track_type': 'multi_track',
            'claim_value': 1500000000,  # £15 million claim
            'case_summary': 'Established the three-part test for duty of care in negligence: foreseeability, proximity, and fair/just/reasonable.',
            'legal_principles': 'For a duty of care to exist in negligence there must be: (1) reasonable foreseeability of harm, (2) proximity of relationship, (3) fair, just and reasonable to impose duty.',
            'url': 'https://www.bailii.org/uk/cases/UKHL/1990/2.html'
        },
        {
            'case_name': 'Mitchell v News Group Newspapers Ltd',
            'citation': '[2013] EWCA Civ 1537',
            'court': 'Court of Appeal',
            'year': 2013,
            'track_type': 'multi_track',
            'claim_value': 5000000,  # £50,000 claim
            'case_summary': 'Important case on costs sanctions and relief from sanctions under CPR 3.9, establishing the Denton principles.',
            'legal_principles': 'Courts should adopt a more robust approach to case management and parties must comply with court orders and directions.',
            'url': 'https://www.bailii.org/ew/cases/EWCA/Civ/2013/1537.html'
        }
    ]
    
    for case_data in sample_cases:
        existing_case = LegalCase.query.filter_by(citation=case_data['citation']).first()
        if not existing_case:
            case = LegalCase()
            for key, value in case_data.items():
                setattr(case, key, value)
            db.session.add(case)
    
    logging.info(f"Initialized {len(sample_cases)} legal cases")

def initialize_sample_legal_knowledge():
    """Initialize sample legal knowledge data"""
    sample_procedures = [
        {
            'title': 'Small Claims Track Procedure',
            'content': 'Small claims are designed for disputes up to £10,000. The procedure is simplified with limited disclosure, no requirement for legal representation, and restricted costs recovery. Hearings are informal and conducted by District Judges. Claims can be started online at gov.uk/make-court-claim-for-money.',
            'category': 'procedure',
            'subcategory': 'small_claims',
            'track_relevance': '["small_claims"]',
            'keywords': 'small claims, simplified procedure, district judge, informal hearing, £10000, online claim',
            'source_url': 'https://www.gov.uk/make-court-claim-for-money'
        },
        {
            'title': 'Fast Track Case Management',
            'content': 'Fast track claims (£10,000-£25,000) follow standard directions with a trial window of 30 weeks. Fixed trial costs apply. Standard directions include disclosure by list, witness statement exchange, and expert evidence (usually single joint expert). The track is designed to balance accessibility with proper case management.',
            'category': 'procedure',
            'subcategory': 'fast_track',
            'track_relevance': '["fast_track"]',
            'keywords': 'fast track, standard directions, fixed costs, 30 weeks, £10000, £25000',
            'source_url': 'https://www.justice.gov.uk/courts/procedure-rules/civil'
        },
        {
            'title': 'Multi-Track Case Management Conference',
            'content': 'Multi-track claims over £25,000 require active case management including Case Management Conferences (CMC), costs budgeting under Precedent H, and tailored directions. The court controls the litigation timetable and will make directions suited to the particular case. Costs budgeting is mandatory for claims over £10 million.',
            'category': 'procedure',
            'subcategory': 'multi_track',
            'track_relevance': '["multi_track"]',
            'keywords': 'multi track, case management conference, costs budgeting, precedent h, £25000, cmc',
            'source_url': 'https://www.justice.gov.uk/courts/procedure-rules/civil'
        },
        {
            'title': 'Part 36 Offers',
            'content': 'Part 36 offers are formal settlement offers with costs consequences. An offer must be open for at least 21 days. If the claimant fails to beat a defendant\'s Part 36 offer at trial, they may have to pay the defendant\'s costs from the expiry of the offer plus interest and additional amount.',
            'category': 'procedure',
            'subcategory': 'settlement',
            'track_relevance': '["small_claims", "fast_track", "multi_track"]',
            'keywords': 'part 36, settlement offer, costs consequences, 21 days, indemnity costs',
            'source_url': 'https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part36'
        },
        {
            'title': 'Disclosure and Inspection',
            'content': 'Standard disclosure requires parties to disclose documents that support or adversely affect their case or another party\'s case. Documents must be listed in a disclosure statement. Proportionality is key - the court will control disclosure to ensure it is proportionate to the case value and complexity.',
            'category': 'procedure',
            'subcategory': 'disclosure',
            'track_relevance': '["fast_track", "multi_track"]',
            'keywords': 'disclosure, inspection, documents, proportionality, standard disclosure, privilege',
            'source_url': 'https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part31'
        }
    ]
    
    # Statutory provisions
    sample_statutes = [
        {
            'title': 'Limitation Act 1980',
            'content': 'Sets limitation periods for bringing legal claims. Contract claims must generally be brought within 6 years, tort claims within 6 years, personal injury claims within 3 years. Time usually runs from when the cause of action accrued, but may be extended in cases of fraud, concealment or disability.',
            'category': 'statute',
            'subcategory': 'limitation',
            'track_relevance': '["small_claims", "fast_track", "multi_track"]',
            'keywords': 'limitation period, 6 years, 3 years, personal injury, contract, tort, time limit',
            'source_url': 'https://www.legislation.gov.uk/ukpga/1980/58'
        },
        {
            'title': 'Consumer Rights Act 2015',
            'content': 'Provides rights for consumers including the right to goods that are of satisfactory quality, fit for purpose and as described. Consumers have rights to reject, repair, replacement and refund. Unfair contract terms are not binding on consumers.',
            'category': 'statute',
            'subcategory': 'consumer',
            'track_relevance': '["small_claims", "fast_track"]',
            'keywords': 'consumer rights, satisfactory quality, fit for purpose, unfair terms, refund, replacement',
            'source_url': 'https://www.legislation.gov.uk/ukpga/2015/15'
        },
        {
            'title': 'Civil Liability Act 2018',
            'content': 'Reformed personal injury claims by introducing fixed tariffs for whiplash injuries lasting up to 2 years and raising the small claims limit for RTA-related personal injury claims to £5,000. Affects how personal injury damages are calculated and which track cases are allocated to.',
            'category': 'statute',
            'subcategory': 'personal_injury',
            'track_relevance': '["small_claims", "fast_track"]',
            'keywords': 'whiplash, fixed tariff, personal injury, RTA, £5000, small claims limit',
            'source_url': 'https://www.legislation.gov.uk/ukpga/2018/29'
        }
    ]
    
    all_knowledge = sample_procedures + sample_statutes
    
    for knowledge_data in all_knowledge:
        existing_knowledge = LegalKnowledge.query.filter_by(title=knowledge_data['title']).first()
        if not existing_knowledge:
            knowledge = LegalKnowledge()
            for key, value in knowledge_data.items():
                setattr(knowledge, key, value)
            db.session.add(knowledge)
    
    logging.info(f"Initialized {len(all_knowledge)} knowledge items")

def initialize_sample_solicitors():
    """Initialize sample solicitor data"""
    sample_solicitors = [
        {
            'firm_name': 'City Commercial Law LLP',
            'contact_name': 'Sarah Johnson',
            'specialties': '["commercial_dispute", "contract_dispute", "debt_recovery", "multi_track"]',
            'track_experience': '["fast_track", "multi_track"]',
            'location': 'London',
            'contact_email': 'sarah.johnson@citycommercial.co.uk',
            'contact_phone': '020 7123 4567',
            'website': 'https://www.citycommercial.co.uk',
            'min_claim_value': 1000000,  # £10,000 in pence
            'max_claim_value': 10000000,  # £100,000 in pence
            'funding_options': '["CFA", "ATE", "DBA"]',
            'active': True
        },
        {
            'firm_name': 'Regional Litigation Partners',
            'contact_name': 'Michael Brown',
            'specialties': '["personal_injury", "employment", "consumer_dispute", "general_litigation"]',
            'track_experience': '["small_claims", "fast_track", "multi_track"]',
            'location': 'Manchester',
            'contact_email': 'michael.brown@regionallitigation.co.uk',
            'contact_phone': '0161 234 5678',
            'website': 'https://www.regionallitigation.co.uk',
            'min_claim_value': 50000,  # £500 in pence
            'max_claim_value': 5000000,  # £50,000 in pence
            'funding_options': '["CFA", "ATE", "legal_aid"]',
            'active': True
        },
        {
            'firm_name': 'Professional Negligence Specialists',
            'contact_name': 'Dr. Emma Wilson',
            'specialties': '["professional_negligence", "medical_negligence", "legal_negligence"]',
            'track_experience': '["fast_track", "multi_track"]',
            'location': 'Birmingham',
            'contact_email': 'emma.wilson@profnegligence.co.uk',
            'contact_phone': '0121 345 6789',
            'website': 'https://www.profnegligence.co.uk',
            'min_claim_value': 500000,  # £5,000 in pence
            'max_claim_value': 10000000,  # £100,000 in pence
            'funding_options': '["CFA", "ATE", "third_party_funding"]',
            'active': True
        },
        {
            'firm_name': 'High Street Legal Services',
            'contact_name': 'James Thompson',
            'specialties': '["small_claims", "consumer_dispute", "landlord_tenant", "debt_recovery"]',
            'track_experience': '["small_claims", "fast_track"]',
            'location': 'Leeds',
            'contact_email': 'james.thompson@highstreetlegal.co.uk',
            'contact_phone': '0113 456 7890',
            'website': 'https://www.highstreetlegal.co.uk',
            'min_claim_value': 10000,  # £100 in pence
            'max_claim_value': 2500000,  # £25,000 in pence
            'funding_options': '["CFA", "hourly_rate", "fixed_fee"]',
            'active': True
        }
    ]
    
    for solicitor_data in sample_solicitors:
        existing_solicitor = SolicitorReferral.query.filter_by(
            firm_name=solicitor_data['firm_name']
        ).first()
        if not existing_solicitor:
            solicitor = SolicitorReferral()
            for key, value in solicitor_data.items():
                setattr(solicitor, key, value)
            db.session.add(solicitor)
    
    logging.info(f"Initialized {len(sample_solicitors)} solicitor referrals")

def initialize_all_sample_data():
    """Initialize all sample data"""
    try:
        # Check if data already exists
        if LegalCase.query.first() is not None:
            logging.info("Sample data already exists, skipping initialization")
            return
        
        initialize_sample_legal_cases()
        initialize_sample_legal_knowledge()
        initialize_sample_solicitors()
        
        db.session.commit()
        logging.info("Successfully initialized all sample data")
        
    except Exception as e:
        logging.error(f"Error initializing sample data: {e}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    with app.app_context():
        initialize_all_sample_data()