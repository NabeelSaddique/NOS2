import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import base64
from io import StringIO

# Set page configuration
st.set_page_config(
    page_title="Newcastle-Ottawa Scale Assessment Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .developer-info {
        background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 6px solid #3498db;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .domain-header {
        background: linear-gradient(135deg, #6c757d, #495057);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-weight: bold;
        margin: 1rem 0 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .quality-good { background-color: #28a745; color: white; padding: 0.3rem 0.6rem; border-radius: 5px; font-weight: bold; }
    .quality-fair { background-color: #ffc107; color: black; padding: 0.3rem 0.6rem; border-radius: 5px; font-weight: bold; }
    .quality-poor { background-color: #dc3545; color: white; padding: 0.3rem 0.6rem; border-radius: 5px; font-weight: bold; }
    
    .robvis-bar {
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        font-weight: bold;
        margin: 4px 0;
        padding: 0 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .robvis-good { background: linear-gradient(135deg, #28a745, #34ce57); }
    .robvis-fair { background: linear-gradient(135deg, #ffc107, #ffcd39); color: black; }
    .robvis-poor { background: linear-gradient(135deg, #dc3545, #e85370); }
    
    .study-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #dee2e6;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .summary-container {
        background: linear-gradient(135deg, #e8f5e8, #d1ecf1);
        padding: 2rem;
        border-radius: 12px;
        border: 3px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'studies' not in st.session_state:
    st.session_state.studies = []

# Newcastle-Ottawa Scale criteria
NOS_CRITERIA = {
    "Cohort Studies": {
        "Selection": {
            "representativeness": {
                "question": "1. Representativeness of the exposed cohort",
                "options": {
                    "truly_representative": "Truly representative of the average population in the community (★)",
                    "somewhat_representative": "Somewhat representative of the average population in the community (★)",
                    "selected_group": "Selected group of users (e.g., nurses, volunteers)",
                    "no_description": "No description of the derivation of the cohort"
                },
                "stars": {"truly_representative": 1, "somewhat_representative": 1, "selected_group": 0, "no_description": 0}
            },
            "selection_nonexposed": {
                "question": "2. Selection of the non-exposed cohort",
                "options": {
                    "same_community": "Drawn from the same community as the exposed cohort (★)",
                    "different_source": "Drawn from a different source",
                    "no_description": "No description of the derivation of the non-exposed cohort"
                },
                "stars": {"same_community": 1, "different_source": 0, "no_description": 0}
            },
            "ascertainment_exposure": {
                "question": "3. Ascertainment of exposure",
                "options": {
                    "secure_record": "Secure record (e.g., surgical records) (★)",
                    "structured_interview": "Structured interview where blind to case/control status (★)",
                    "written_self_report": "Written self-report",
                    "no_description": "No description"
                },
                "stars": {"secure_record": 1, "structured_interview": 1, "written_self_report": 0, "no_description": 0}
            },
            "outcome_not_present": {
                "question": "4. Demonstration that outcome of interest was not present at start of study",
                "options": {
                    "yes": "Yes (★)",
                    "no": "No"
                },
                "stars": {"yes": 1, "no": 0}
            }
        },
        "Comparability": {
            "comparability": {
                "question": "5. Comparability of cohorts on the basis of the design or analysis",
                "options": {
                    "most_important": "Study controls for the most important factor (★)",
                    "additional_factor": "Study controls for any additional factor (★★)",
                    "no_control": "No control for confounding factors"
                },
                "stars": {"most_important": 1, "additional_factor": 2, "no_control": 0},
                "max_stars": 2
            }
        },
        "Outcome": {
            "assessment_outcome": {
                "question": "6. Assessment of outcome",
                "options": {
                    "independent_blind": "Independent blind assessment (★)",
                    "record_linkage": "Record linkage (★)",
                    "self_report": "Self-report",
                    "no_description": "No description"
                },
                "stars": {"independent_blind": 1, "record_linkage": 1, "self_report": 0, "no_description": 0}
            },
            "adequate_followup_length": {
                "question": "7. Was follow-up long enough for outcomes to occur",
                "options": {
                    "yes": "Yes (★)",
                    "no": "No"
                },
                "stars": {"yes": 1, "no": 0}
            },
            "adequacy_followup": {
                "question": "8. Adequacy of follow up of cohorts",
                "options": {
                    "complete_followup": "Complete follow up - all subjects accounted for (★)",
                    "small_loss": "Subjects lost to follow up unlikely to introduce bias - small number lost (★)",
                    "high_loss": "High rate of follow up but no description of those lost",
                    "no_statement": "No statement"
                },
                "stars": {"complete_followup": 1, "small_loss": 1, "high_loss": 0, "no_statement": 0}
            }
        }
    },
    "Case-Control Studies": {
        "Selection": {
            "case_definition": {
                "question": "1. Is the case definition adequate?",
                "options": {
                    "independent_validation": "Yes, with independent validation (★)",
                    "record_linkage": "Yes, e.g., record linkage or based on self-reports",
                    "no_description": "No description"
                },
                "stars": {"independent_validation": 1, "record_linkage": 0, "no_description": 0}
            },
            "representativeness_cases": {
                "question": "2. Representativeness of the cases",
                "options": {
                    "consecutive_series": "Consecutive or obviously representative series of cases (★)",
                    "potential_selection": "Potential for selection biases or not stated"
                },
                "stars": {"consecutive_series": 1, "potential_selection": 0}
            },
            "selection_controls": {
                "question": "3. Selection of Controls",
                "options": {
                    "community_controls": "Community controls (★)",
                    "hospital_controls": "Hospital controls",
                    "no_description": "No description"
                },
                "stars": {"community_controls": 1, "hospital_controls": 0, "no_description": 0}
            },
            "definition_controls": {
                "question": "4. Definition of Controls",
                "options": {
                    "no_history": "No history of disease (endpoint) (★)",
                    "no_description": "No description of source"
                },
                "stars": {"no_history": 1, "no_description": 0}
            }
        },
        "Comparability": {
            "comparability": {
                "question": "5. Comparability of cases and controls on the basis of the design or analysis",
                "options": {
                    "most_important": "Study controls for the most important factor (★)",
                    "additional_factor": "Study controls for any additional factor (★★)",
                    "no_control": "No control for confounding factors"
                },
                "stars": {"most_important": 1, "additional_factor": 2, "no_control": 0},
                "max_stars": 2
            }
        },
        "Exposure": {
            "ascertainment_exposure": {
                "question": "6. Ascertainment of exposure",
                "options": {
                    "secure_record": "Secure record (e.g., surgical records) (★)",
                    "structured_interview": "Structured interview where blind to case/control status (★)",
                    "interview_not_blinded": "Interview not blinded to case/control status",
                    "written_self_report": "Written self-report or medical record only",
                    "no_description": "No description"
                },
                "stars": {"secure_record": 1, "structured_interview": 1, "interview_not_blinded": 0, "written_self_report": 0, "no_description": 0}
            },
            "same_method": {
                "question": "7. Same method of ascertainment for cases and controls",
                "options": {
                    "yes": "Yes (★)",
                    "no": "No"
                },
                "stars": {"yes": 1, "no": 0}
            },
            "non_response_rate": {
                "question": "8. Non-Response rate",
                "options": {
                    "same_rate": "Same rate for both groups (★)",
                    "non_respondents": "Non-respondents described",
                    "rate_different": "Rate different and no designation"
                },
                "stars": {"same_rate": 1, "non_respondents": 0, "rate_different": 0}
            }
        }
    },
    "Cross-Sectional Studies": {
        "Selection": {
            "representativeness": {
                "question": "1. Representativeness of the sample",
                "options": {
                    "truly_representative": "Truly representative of the average population (★)",
                    "somewhat_representative": "Somewhat representative of the average population (★)",
                    "selected_group": "Selected group of users",
                    "no_description": "No description of the sampling strategy"
                },
                "stars": {"truly_representative": 1, "somewhat_representative": 1, "selected_group": 0, "no_description": 0}
            },
            "sample_size": {
                "question": "2. Sample size",
                "options": {
                    "justified": "Justified and satisfactory (★)",
                    "not_justified": "Not justified"
                },
                "stars": {"justified": 1, "not_justified": 0}
            },
            "non_respondents": {
                "question": "3. Non-respondents",
                "options": {
                    "comparability": "Comparability between respondents and non-respondents characteristics is established (★)",
                    "response_rate": "Response rate satisfactory or non-respondents described",
                    "no_description": "No description of non-respondents"
                },
                "stars": {"comparability": 1, "response_rate": 0, "no_description": 0}
            },
            "exposure_outcome": {
                "question": "4. Ascertainment of the exposure (or risk factor)",
                "options": {
                    "validated_tool": "Validated measurement tool (★)",
                    "non_validated": "Non-validated measurement tool or unclear"
                },
                "stars": {"validated_tool": 1, "non_validated": 0}
            }
        },
        "Comparability": {
            "comparability": {
                "question": "5. The subjects in different outcome groups are comparable",
                "options": {
                    "most_important": "Study controls for the most important confounding factor (★)",
                    "additional_factor": "Study controls for additional confounding factors (★★)",
                    "no_control": "No control for confounding factors"
                },
                "stars": {"most_important": 1, "additional_factor": 2, "no_control": 0},
                "max_stars": 2
            }
        },
        "Outcome": {
            "assessment_outcome": {
                "question": "6. Assessment of the outcome",
                "options": {
                    "independent_blind": "Independent blind assessment (★)",
                    "record_linkage": "Record linkage (★)",
                    "self_report": "Self-report",
                    "no_description": "No description"
                },
                "stars": {"independent_blind": 1, "record_linkage": 1, "self_report": 0, "no_description": 0}
            },
            "statistical_test": {
                "question": "7. Statistical test",
                "options": {
                    "appropriate": "The statistical test used to analyze the data is clearly described and appropriate (★)",
                    "inappropriate": "The statistical test is not appropriate, not described or incomplete"
                },
                "stars": {"appropriate": 1, "inappropriate": 0}
            }
        }
    }
}
def calculate_total_stars(assessment, study_type):
    """Calculate total stars for an assessment"""
    total_stars = 0
    criteria = NOS_CRITERIA[study_type]
    
    for domain_name, domain in criteria.items():
        for criterion_name, criterion in domain.items():
            if criterion_name in assessment:
                selected_option = assessment[criterion_name]
                if selected_option in criterion["stars"]:
                    stars = criterion["stars"][selected_option]
                    if criterion_name == "comparability" and "max_stars" in criterion:
                        if selected_option == "most_important":
                            total_stars += 1
                        elif selected_option == "additional_factor":
                            total_stars += 2
                    else:
                        total_stars += stars
    
    return total_stars

def get_quality_rating(total_stars, study_type):
    """Determine quality rating based on total stars"""
    if study_type in ["Cohort Studies", "Case-Control Studies"]:
        max_stars = 9
        if total_stars >= 7:
            return "Good Quality", "#28a745"
        elif total_stars >= 5:
            return "Fair Quality", "#ffc107"
        else:
            return "Poor Quality", "#dc3545"
    else:  # Cross-sectional
        max_stars = 8
        if total_stars >= 6:
            return "Good Quality", "#28a745"
        elif total_stars >= 4:
            return "Fair Quality", "#ffc107"
        else:
            return "Poor Quality", "#dc3545"

def calculate_domain_scores(study):
    """Calculate detailed domain scores"""
    study_type = study['study_type']
    assessment = study['assessment']
    criteria = NOS_CRITERIA[study_type]
    
    domain_scores = {}
    
    for domain_name, domain in criteria.items():
        domain_stars = 0
        max_domain_stars = len(domain)
        if domain_name == "Comparability":
            max_domain_stars = 2
        
        for criterion_name, criterion in domain.items():
            if criterion_name in assessment:
                selected_option = assessment[criterion_name]
                if selected_option in criterion["stars"]:
                    stars = criterion["stars"][selected_option]
                    if criterion_name == "comparability" and "max_stars" in criterion:
                        if selected_option == "most_important":
                            domain_stars += 1
                        elif selected_option == "additional_factor":
                            domain_stars += 2
                    else:
                        domain_stars += stars
        
        domain_scores[domain_name] = {
            'stars': domain_stars,
            'max_stars': max_domain_stars,
            'percentage': (domain_stars / max_domain_stars * 100) if max_domain_stars > 0 else 0
        }
    
    return domain_scores

def create_robvis_visualization(studies_data):
    """Create robvis-style visualization using HTML/CSS"""
    if not studies_data:
        return None
    
    html_content = '''
    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h3 style="text-align: center; color: #2c3e50; margin-bottom: 20px; font-family: Arial, sans-serif;">
            📊 Risk of Bias Assessment Summary (Newcastle-Ottawa Scale)
        </h3>
        <div style="display: flex; justify-content: center; margin-bottom: 20px; gap: 20px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #28a745; border-radius: 3px;"></div>
                <span style="font-size: 14px; font-weight: bold;">Good Quality</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #ffc107; border-radius: 3px;"></div>
                <span style="font-size: 14px; font-weight: bold;">Fair Quality</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #dc3545; border-radius: 3px;"></div>
                <span style="font-size: 14px; font-weight: bold;">Poor Quality</span>
            </div>
        </div>
    '''
    
    for study in studies_data:
        quality = study['quality_rating']
        stars = study['total_stars']
        star_text = "★" * stars
        
        if quality == "Good Quality":
            css_class = "robvis-good"
            color = "#28a745"
        elif quality == "Fair Quality":
            css_class = "robvis-fair"
            color = "#ffc107"
        else:
            css_class = "robvis-poor"
            color = "#dc3545"
        
        display_name = study['study_name']
        if len(display_name) > 40:
            display_name = display_name[:37] + "..."
        
        html_content += f'''
        <div class="robvis-bar {css_class}" style="
            background: linear-gradient(135deg, {color}, {color}dd);
            margin: 8px 0;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <span style="font-weight: bold; font-size: 14px;">
                {display_name}
            </span>
            <span style="font-size: 14px;">
                {quality} ({stars}/9) {star_text}
            </span>
        </div>
        '''
    
    html_content += '</div>'
    return html_content

def create_domain_heatmap(studies_data):
    """Create domain-wise heatmap visualization"""
    if not studies_data:
        return None
    
    all_domains = set()
    for study in studies_data:
        study_type = study['study_type']
        for domain in NOS_CRITERIA[study_type].keys():
            all_domains.add(domain)
    
    all_domains = sorted(list(all_domains))
    
    html_content = '''
    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h3 style="text-align: center; color: #2c3e50; margin-bottom: 20px; font-family: Arial, sans-serif;">
            🔍 Domain-wise Risk of Bias Assessment
        </h3>
        <div style="display: flex; justify-content: center; margin-bottom: 15px; gap: 15px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 15px; height: 15px; background: #28a745; border-radius: 2px;"></div>
                <span style="font-size: 12px;">High (>75%)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 15px; height: 15px; background: #ffc107; border-radius: 2px;"></div>
                <span style="font-size: 12px;">Medium (25-75%)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 15px; height: 15px; background: #dc3545; border-radius: 2px;"></div>
                <span style="font-size: 12px;">Low (<25%)</span>
            </div>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
            <thead><tr>
                <th style="border: 1px solid #ddd; padding: 8px; background: #f8f9fa; text-align: left; min-width: 150px;">Study</th>
    '''
    
    for domain in all_domains:
        html_content += f'<th style="border: 1px solid #ddd; padding: 8px; background: #f8f9fa; text-align: center; min-width: 100px;">{domain}</th>'
    
    html_content += '</tr></thead><tbody>'
    
    for study in studies_data:
        domain_scores = calculate_domain_scores(study)
        display_name = study['study_name']
        if len(display_name) > 25:
            display_name = display_name[:22] + "..."
        
        html_content += f'<tr><td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">{display_name}</td>'
        
        for domain in all_domains:
            if domain in domain_scores:
                percentage = domain_scores[domain]['percentage']
                stars = domain_scores[domain]['stars']
                max_stars = domain_scores[domain]['max_stars']
                
                if percentage >= 75:
                    bg_color = "#28a745"
                    text_color = "white"
                elif percentage >= 25:
                    bg_color = "#ffc107"
                    text_color = "black"
                else:
                    bg_color = "#dc3545"
                    text_color = "white"
                
                html_content += f'''
                <td style="
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: center; 
                    background: {bg_color}; 
                    color: {text_color};
                    font-weight: bold;
                ">
                    {stars}/{max_stars}
                </td>
                '''
            else:
                html_content += '<td style="border: 1px solid #ddd; padding: 8px; text-align: center; background: #f8f9fa;">N/A</td>'
        
        html_content += '</tr>'
    
    html_content += '</tbody></table></div>'
    return html_content

def generate_summary_statistics(studies_data):
    """Generate comprehensive summary statistics"""
    if not studies_data:
        return {}
    
    total_studies = len(studies_data)
    quality_counts = {"Good Quality": 0, "Fair Quality": 0, "Poor Quality": 0}
    study_types = {}
    star_distribution = {}
    domain_performance = {}
    
    for study in studies_data:
        quality_counts[study['quality_rating']] += 1
        
        study_type = study['study_type']
        study_types[study_type] = study_types.get(study_type, 0) + 1
        
        stars = study['total_stars']
        star_distribution[stars] = star_distribution.get(stars, 0) + 1
        
        domain_scores = calculate_domain_scores(study)
        for domain_name, scores in domain_scores.items():
            if domain_name not in domain_performance:
                domain_performance[domain_name] = {
                    'total_stars': 0,
                    'total_possible': 0,
                    'studies': 0
                }
            domain_performance[domain_name]['total_stars'] += scores['stars']
            domain_performance[domain_name]['total_possible'] += scores['max_stars']
            domain_performance[domain_name]['studies'] += 1
    
    quality_percentages = {k: (v/total_studies)*100 for k, v in quality_counts.items()}
    
    domain_averages = {}
    for domain, perf in domain_performance.items():
        domain_averages[domain] = {
            'average_percentage': (perf['total_stars'] / perf['total_possible'] * 100) if perf['total_possible'] > 0 else 0,
            'average_stars': perf['total_stars'] / perf['studies'] if perf['studies'] > 0 else 0
        }
    
    return {
        'total_studies': total_studies,
        'quality_counts': quality_counts,
        'quality_percentages': quality_percentages,
        'study_types': study_types,
        'star_distribution': star_distribution,
        'domain_averages': domain_averages,
        'overall_quality_score': sum(study['total_stars'] for study in studies_data) / (total_studies * 9) * 100 if total_studies > 0 else 0
    }

def create_study_summary_card(study):
    """Create an enhanced study summary card"""
    quality_rating, color = get_quality_rating(study['total_stars'], study['study_type'])
    domain_scores = calculate_domain_scores(study)
    
    domain_mini_chart = ""
    for domain_name, scores in domain_scores.items():
        percentage = scores['percentage']
        if percentage >= 75:
            domain_mini_chart += "🟢"
        elif percentage >= 50:
            domain_mini_chart += "🟡" 
        elif percentage >= 25:
            domain_mini_chart += "🟠"
        else:
            domain_mini_chart += "🔴"
    
    card_html = f'''
    <div class="study-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <div style="flex: 1;">
                <h4 style="margin: 0 0 5px 0; color: #2c3e50;">{study['study_name']}</h4>
                <p style="margin: 0; color: #6c757d; font-size: 14px;">
                    <strong>Authors:</strong> {study['authors'][:50]}{'...' if len(study['authors']) > 50 else ''}<br>
                    <strong>Journal:</strong> {study['journal']} ({study['publication_year']})<br>
                    <strong>Study Type:</strong> {study['study_type']}
                </p>
            </div>
            <div style="text-align: right; margin-left: 15px;">
                <div class="quality-{quality_rating.lower().replace(' ', '-')}" style="margin-bottom: 8px;">
                    {quality_rating}
                </div>
                <div style="font-size: 18px; margin-bottom: 5px;">
                    {'★' * study['total_stars']}{'☆' * (9 - study['total_stars'])}
                </div>
                <div style="font-size: 12px; color: #6c757d;">
                    {study['total_stars']}/9 stars
                </div>
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 12px; color: #6c757d;">Domain Performance:</span>
            <span style="font-size: 16px;">{domain_mini_chart}</span>
        </div>
        
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; font-size: 12px;">
    '''
    
    for domain_name, scores in domain_scores.items():
        card_html += f'''
                <div style="text-align: center;">
                    <div style="font-weight: bold; color: #2c3e50;">{domain_name}</div>
                    <div style="color: #6c757d;">{scores['stars']}/{scores['max_stars']} ({scores['percentage']:.0f}%)</div>
                </div>
        '''
    
    card_html += f'''
            </div>
        </div>
        
        <div style="font-size: 11px; color: #6c757d; text-align: right;">
            Assessed: {study['assessment_date']}
        </div>
    </div>
    '''
    
    return card_html

def create_publication_ready_table(studies_data):
    """Create a publication-ready summary table"""
    if not studies_data:
        return None
    
    table_data = []
    
    for study in studies_data:
        domain_scores = calculate_domain_scores(study)
        
        authors = study['authors']
        if ',' in authors:
            first_author = authors.split(',')[0].strip()
            author_display = f"{first_author} et al."
        else:
            author_display = authors
        
        row = {
            'Reference': f"{author_display} ({study['publication_year']})",
            'Study Design': study['study_type'],
            'Selection': f"{domain_scores.get('Selection', {}).get('stars', 'N/A')}/{domain_scores.get('Selection', {}).get('max_stars', 'N/A')}",
            'Comparability': f"{domain_scores.get('Comparability', {}).get('stars', 'N/A')}/{domain_scores.get('Comparability', {}).get('max_stars', 'N/A')}",
            'Outcome/Exposure': f"{domain_scores.get('Outcome', domain_scores.get('Exposure', {})).get('stars', 'N/A')}/{domain_scores.get('Outcome', domain_scores.get('Exposure', {})).get('max_stars', 'N/A')}",
            'Total Score': f"{study['total_stars']}/9",
            'Quality Assessment': study['quality_rating']
        }
        
        table_data.append(row)
    
    return pd.DataFrame(table_data)
def show_assessment_form(study_type):
    """Enhanced assessment form with improved UX"""
    st.markdown(f"### 🔍 Assessment Criteria for {study_type}")
    
    assessment = {}
    criteria = NOS_CRITERIA[study_type]
    
    # Create tabs for each domain
    domain_tabs = st.tabs(list(criteria.keys()))
    
    for tab_idx, (domain_name, domain) in enumerate(criteria.items()):
        with domain_tabs[tab_idx]:
            st.markdown(f'<div class="domain-header">{domain_name} Domain</div>', unsafe_allow_html=True)
            
            # Domain description
            domain_descriptions = {
                "Selection": "Evaluates the representativeness and selection methods of study participants",
                "Comparability": "Assesses control for confounding factors in study design or analysis", 
                "Outcome": "Examines the quality of outcome assessment and follow-up",
                "Exposure": "Evaluates the quality of exposure assessment methods"
            }
            
            if domain_name in domain_descriptions:
                st.info(f"**Domain Focus:** {domain_descriptions[domain_name]}")
            
            for criterion_name, criterion in domain.items():
                st.write(f"**{criterion['question']}**")
                
                # Create radio button options with enhanced formatting
                options_display = []
                option_keys = []
                for key, description in criterion['options'].items():
                    stars = criterion['stars'].get(key, 0)
                    if criterion_name == "comparability" and key == "additional_factor":
                        stars = 2
                    
                    star_display = "★" * stars if stars > 0 else "☆"
                    risk_level = "🟢 Low Risk" if stars > 0 else "🔴 High Risk"
                    
                    options_display.append(f"{description} {star_display} | {risk_level}")
                    option_keys.append(key)
                
                # Create columns for better layout
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    selected_idx = st.radio(
                        f"Select assessment for: {criterion['question']}",
                        range(len(options_display)),
                        format_func=lambda x: options_display[x],
                        key=f"{criterion_name}_{domain_name}",
                        help="Select the option that best describes this study"
                    )
                
                with col2:
                    # Show immediate feedback
                    selected_option = option_keys[selected_idx]
                    stars = criterion['stars'].get(selected_option, 0)
                    if criterion_name == "comparability" and selected_option == "additional_factor":
                        stars = 2
                    
                    if stars > 0:
                        st.success(f"✅ {stars} star{'s' if stars > 1 else ''}")
                    else:
                        st.error("❌ 0 stars")
                
                assessment[criterion_name] = option_keys[selected_idx]
                
                st.markdown("---")
    
    return assessment

def create_assessment_progress_bar(assessment, study_type):
    """Create a progress bar for assessment completion"""
    criteria = NOS_CRITERIA[study_type]
    total_criteria = sum(len(domain) for domain in criteria.values())
    completed_criteria = len(assessment)
    
    progress_percentage = (completed_criteria / total_criteria) * 100 if total_criteria > 0 else 0
    
    progress_html = f'''
    <div style="margin: 15px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-weight: bold; color: #2c3e50;">Assessment Progress</span>
            <span style="color: #6c757d;">{completed_criteria}/{total_criteria} criteria completed</span>
        </div>
        <div style="background: #e9ecef; border-radius: 10px; height: 8px; margin: 10px 0;">
            <div style="
                background: linear-gradient(90deg, #28a745, #20c997);
                height: 100%;
                border-radius: 10px;
                width: {progress_percentage}%;
                transition: width 0.3s ease;
            "></div>
        </div>
        <div style="text-align: center; font-size: 12px; color: #6c757d; margin-top: 5px;">
            {progress_percentage:.1f}% complete
        </div>
    </div>
    '''
    
    return progress_html

def create_risk_assessment_summary(studies_data):
    """Create a comprehensive risk assessment summary"""
    if not studies_data:
        return None
    
    stats = generate_summary_statistics(studies_data)
    
    summary_html = f'''
    <div class="summary-container">
        <h3 style="text-align: center; color: #2c3e50; margin-bottom: 25px;">
            📋 Risk of Bias Assessment Summary
        </h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 25px;">
            <div class="metric-card">
                <h2 style="margin: 0; color: #3498db;">{stats['total_studies']}</h2>
                <p style="margin: 5px 0 0 0; color: #6c757d;">Total Studies</p>
            </div>
            
            <div class="metric-card">
                <h2 style="margin: 0; color: #28a745;">{stats['quality_counts']['Good Quality']}</h2>
                <p style="margin: 5px 0 0 0; color: #6c757d;">Good Quality ({stats['quality_percentages']['Good Quality']:.1f}%)</p>
            </div>
            
            <div class="metric-card">
                <h2 style="margin: 0; color: #ffc107;">{stats['quality_counts']['Fair Quality']}</h2>
                <p style="margin: 5px 0 0 0; color: #6c757d;">Fair Quality ({stats['quality_percentages']['Fair Quality']:.1f}%)</p>
            </div>
            
            <div class="metric-card">
                <h2 style="margin: 0; color: #dc3545;">{stats['quality_counts']['Poor Quality']}</h2>
                <p style="margin: 5px 0 0 0; color: #6c757d;">Poor Quality ({stats['quality_percentages']['Poor Quality']:.1f}%)</p>
            </div>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">📊 Domain Performance Analysis</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
    '''
    
    for domain_name, avg_data in stats['domain_averages'].items():
        avg_percentage = avg_data['average_percentage']
        if avg_percentage >= 75:
            status_color = "#28a745"
            status_text = "Strong"
        elif avg_percentage >= 50:
            status_color = "#ffc107" 
            status_text = "Moderate"
        else:
            status_color = "#dc3545"
            status_text = "Weak"
        
        summary_html += f'''
                <div style="border: 2px solid {status_color}; border-radius: 8px; padding: 15px; text-align: center;">
                    <h5 style="margin: 0 0 10px 0; color: #2c3e50;">{domain_name}</h5>
                    <div style="font-size: 24px; font-weight: bold; color: {status_color}; margin-bottom: 5px;">
                        {avg_percentage:.1f}%
                    </div>
                    <div style="font-size: 12px; color: #6c757d;">
                        {status_text} Performance
                    </div>
                </div>
        '''
    
    summary_html += '''
            </div>
        </div>
        
        <div style="background: white; padding: 20px; border-radius: 10px;">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">🎯 Overall Assessment</h4>
            <div style="display: flex; justify-content: center; align-items: center; gap: 30px; flex-wrap: wrap;">
    '''
    
    overall_score = stats['overall_quality_score']
    if overall_score >= 75:
        overall_color = "#28a745"
        overall_status = "High Quality Portfolio"
        overall_icon = "🟢"
    elif overall_score >= 50:
        overall_color = "#ffc107"
        overall_status = "Moderate Quality Portfolio" 
        overall_icon = "🟡"
    else:
        overall_color = "#dc3545"
        overall_status = "Needs Improvement"
        overall_icon = "🔴"
    
    summary_html += f'''
                <div style="text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 10px;">{overall_icon}</div>
                    <div style="font-size: 32px; font-weight: bold; color: {overall_color}; margin-bottom: 5px;">
                        {overall_score:.1f}%
                    </div>
                    <div style="font-size: 16px; color: #2c3e50; font-weight: bold;">
                        {overall_status}
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return summary_html

def create_methodological_recommendations(studies_data):
    """Generate methodological recommendations based on assessment"""
    if not studies_data:
        return None
    
    stats = generate_summary_statistics(studies_data)
    
    # Analyze weak domains
    weak_domains = []
    for domain_name, avg_data in stats['domain_averages'].items():
        if avg_data['average_percentage'] < 50:
            weak_domains.append(domain_name)
    
    rec_html = '''
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #3498db;">
        <h4 style="color: #2c3e50; margin-bottom: 15px;">💡 Methodological Recommendations</h4>
    '''
    
    if weak_domains:
        rec_html += f'''
        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 15px; border-left: 4px solid #ffc107;">
            <h5 style="color: #856404; margin-bottom: 10px;">⚠️ Areas Requiring Attention</h5>
            <p style="margin-bottom: 10px; color: #856404;">
                The following domains showed suboptimal performance across studies:
            </p>
            <ul style="margin: 0; color: #856404;">
        '''
        
        for domain in weak_domains:
            if domain == "Selection":
                rec_html += "<li>Improve participant selection and representativeness documentation</li>"
            elif domain == "Comparability": 
                rec_html += "<li>Enhance control for confounding factors in design or analysis</li>"
            elif domain == "Outcome":
                rec_html += "<li>Strengthen outcome assessment methods and follow-up procedures</li>"
            elif domain == "Exposure":
                rec_html += "<li>Improve exposure assessment reliability and consistency</li>"
        
        rec_html += '''
            </ul>
        </div>
        '''
    
    # Overall recommendations
    if stats['overall_quality_score'] >= 75:
        rec_html += '''
        <div style="background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
            <h5 style="color: #155724; margin-bottom: 10px;">✅ High Quality Evidence Base</h5>
            <p style="margin: 0; color: #155724;">
                The included studies demonstrate good methodological quality. Consider highlighting this strength in your discussion and recommendations.
            </p>
        </div>
        '''
    elif stats['overall_quality_score'] >= 50:
        rec_html += '''
        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
            <h5 style="color: #856404; margin-bottom: 10px;">⚠️ Moderate Quality Evidence</h5>
            <p style="margin: 0; color: #856404;">
                The evidence base shows moderate quality. Consider discussing limitations and the need for higher-quality studies in future research.
            </p>
        </div>
        '''
    else:
        rec_html += '''
        <div style="background: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545;">
            <h5 style="color: #721c24; margin-bottom: 10px;">🔴 Quality Concerns</h5>
            <p style="margin: 0; color: #721c24;">
                Significant methodological limitations identified. Results should be interpreted with caution, and future high-quality studies are needed.
            </p>
        </div>
        '''
    
    rec_html += '</div>'
    return rec_html

def export_to_csv_enhanced(studies_data):
    """Enhanced CSV export with detailed domain analysis"""
    if not studies_data:
        return None
    
    export_data = []
    
    for study in studies_data:
        domain_scores = calculate_domain_scores(study)
        
        base_row = {
            'Study_ID': len(export_data) + 1,
            'Study_Name': study['study_name'],
            'First_Author': study['authors'].split(',')[0] if study['authors'] else '',
            'All_Authors': study['authors'],
            'Publication_Year': study['publication_year'],
            'Journal': study['journal'],
            'DOI': study.get('doi', ''),
            'Study_Type': study['study_type'],
            'Assessment_Date': study['assessment_date'],
            'Total_Stars': study['total_stars'],
            'Max_Possible_Stars': 9 if study['study_type'] in ["Cohort Studies", "Case-Control Studies"] else 8,
            'Quality_Rating': study['quality_rating'],
            'Quality_Percentage': (study['total_stars'] / (9 if study['study_type'] in ["Cohort Studies", "Case-Control Studies"] else 8)) * 100,
            'Notes': study.get('notes', '')
        }
        
        # Add domain scores
        for domain_name, scores in domain_scores.items():
            base_row[f'{domain_name}_Stars'] = scores['stars']
            base_row[f'{domain_name}_Max_Stars'] = scores['max_stars']
            base_row[f'{domain_name}_Percentage'] = scores['percentage']
        
        # Add individual criterion responses
        for criterion, response in study['assessment'].items():
            base_row[f'NOS_{criterion}'] = response
        
        export_data.append(base_row)
    
    return pd.DataFrame(export_data)
def main():
    # Enhanced Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Newcastle-Ottawa Scale Assessment Tool</h1>
        <h3>Advanced Systematic Risk of Bias Assessment for Observational Studies</h3>
        <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 14px;">
            Version 2.0 | Publication-Ready Assessments | Enhanced Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Developer information
    st.markdown("""
    <div class="developer-info">
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; align-items: center;">
            <div>
                <strong>🎓 Developed by:</strong> Muhammad Nabeel Saddique<br>
                <strong>📚 Institution:</strong> 4th Year MBBS Student, King Edward Medical University, Lahore, Pakistan<br>
                <strong>🔬 Research Focus:</strong> Systematic Review, Meta-Analysis, Evidence-Based Medicine<br>
                <strong>🏢 Founder:</strong> Nibras Research Academy - Mentoring young researchers in systematic reviews<br>
                <strong>🛠️ Research Tools Expertise:</strong> Rayyan, Zotero, EndNote, WebPlotDigitizer, Meta-Converter, RevMan, MetaXL, Jamovi, CMA, OpenMeta, R Studio
            </div>
            <div style="text-align: center; background: white; padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #3498db;">
                    {len(st.session_state.studies)}
                </div>
                <div style="font-size: 12px; color: #6c757d;">
                    Studies Assessed
                </div>
            </div>
        </div>
    </div>
    """.format(len=len), unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🎛️ Assessment Controls")
    
    # Quick stats in sidebar
    if st.session_state.studies:
        st.sidebar.markdown("### 📈 Quick Statistics")
        stats = generate_summary_statistics(st.session_state.studies)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total Studies", stats['total_studies'])
            st.metric("Good Quality", stats['quality_counts']['Good Quality'])
        with col2:
            st.metric("Overall Score", f"{stats['overall_quality_score']:.1f}%")
            st.metric("Poor Quality", stats['quality_counts']['Poor Quality'])
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Action",
        [
            "🏠 Dashboard", 
            "📝 Add New Study", 
            "📚 View All Studies", 
            "📊 Generate Report", 
            "📈 Advanced Analytics",
            "🔄 Compare Studies",
            "💾 Export Data",
            "📖 Assessment Guide"
        ]
    )
    
    # Dashboard Page
    if page == "🏠 Dashboard":
        st.header("🏠 Assessment Dashboard")
        
        if st.session_state.studies:
            # Show comprehensive summary
            summary_html = create_risk_assessment_summary(st.session_state.studies)
            st.markdown(summary_html, unsafe_allow_html=True)
            
            # Recent assessments
            st.subheader("📋 Recent Assessments")
            recent_studies = sorted(st.session_state.studies, 
                                  key=lambda x: x['assessment_date'], reverse=True)[:3]
            
            for study in recent_studies:
                study_card = create_study_summary_card(study)
                st.markdown(study_card, unsafe_allow_html=True)
            
            # Quick actions
            st.subheader("🚀 Quick Actions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("➕ Add New Study", type="primary", use_container_width=True):
                    st.session_state.selected_page = "Add New Study"
            
            with col2:
                if st.button("📊 Generate Report", use_container_width=True):
                    st.session_state.selected_page = "Generate Report"
            
            with col3:
                if st.button("📈 Analytics", use_container_width=True):
                    st.session_state.selected_page = "Advanced Analytics"
            
            with col4:
                if st.button("💾 Export Data", use_container_width=True):
                    st.session_state.selected_page = "Export Data"
            
        else:
            # Welcome screen
            st.markdown("""
            <div style="text-align: center; padding: 50px 20px;">
                <h2 style="color: #3498db;">Welcome to the Newcastle-Ottawa Scale Assessment Tool</h2>
                <p style="font-size: 18px; color: #6c757d; margin: 20px 0;">
                    Get started by adding your first study assessment
                </p>
                <div style="margin: 30px 0;">
                    <div style="font-size: 64px;">📊</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Start Your First Assessment", type="primary", use_container_width=True):
                    st.session_state.selected_page = "Add New Study"
    
    # Add New Study Page
    elif page == "📝 Add New Study":
        st.header("📝 Enhanced Study Assessment")
        
        # Study information form
        with st.form("enhanced_study_assessment"):
            # Basic study information
            st.subheader("📋 Study Information")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                study_name = st.text_input("Study Name/Identifier*", 
                                         placeholder="e.g., Smith et al. 2023",
                                         help="Unique identifier for this study")
                study_type = st.selectbox("Study Type*", list(NOS_CRITERIA.keys()),
                                        help="Select the appropriate study design")
            
            with col2:
                authors = st.text_input("Authors*", 
                                      placeholder="Smith J, Brown K, Wilson L",
                                      help="List all authors (separate with commas)")
                publication_year = st.number_input("Publication Year*", 
                                                 min_value=1900, max_value=2024, value=2023)
            
            with col3:
                journal = st.text_input("Journal*", 
                                       placeholder="Journal of Clinical Medicine")
                sample_size = st.number_input("Sample Size", min_value=0, value=0,
                                            help="Total number of participants")
            
            # Additional metadata
            st.subheader("📖 Additional Information")
            col1, col2 = st.columns(2)
            
            with col1:
                doi = st.text_input("DOI", placeholder="10.1000/xyz123")
                country = st.text_input("Country/Region", placeholder="e.g., United States")
                funding = st.text_input("Funding Source", placeholder="e.g., NIH, Industry")
            
            with col2:
                pmid = st.text_input("PubMed ID", placeholder="12345678")
                follow_up = st.text_input("Follow-up Duration", placeholder="e.g., 5 years")
                population = st.text_input("Study Population", placeholder="e.g., Adults >65 years")
            
            # Assessment criteria
            if study_type:
                assessment = show_assessment_form(study_type)
                
                # Show progress
                progress_html = create_assessment_progress_bar(assessment, study_type)
                st.markdown(progress_html, unsafe_allow_html=True)
            
            # Additional assessment details
            st.subheader("📝 Assessment Notes")
            
            col1, col2 = st.columns(2)
            with col1:
                notes = st.text_area("General Notes", 
                                    placeholder="Additional comments about study quality...",
                                    height=100)
                strengths = st.text_area("Study Strengths", 
                                       placeholder="Key methodological strengths...",
                                       height=80)
            
            with col2:
                limitations = st.text_area("Study Limitations", 
                                         placeholder="Key methodological limitations...",
                                         height=80)
                assessor_name = st.text_input("Assessor Name", 
                                            placeholder="Your name")
            
            # Form submission
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("💾 Save Assessment", 
                                                type="primary", 
                                                use_container_width=True)
            
            if submitted:
                if study_name and authors and journal and study_type:
                    total_stars = calculate_total_stars(assessment, study_type)
                    quality_rating, quality_color = get_quality_rating(total_stars, study_type)
                    
                    study_data = {
                        "study_name": study_name,
                        "authors": authors,
                        "publication_year": publication_year,
                        "journal": journal,
                        "doi": doi,
                        "pmid": pmid,
                        "country": country,
                        "sample_size": sample_size,
                        "follow_up": follow_up,
                        "population": population,
                        "funding": funding,
                        "study_type": study_type,
                        "assessment": assessment,
                        "total_stars": total_stars,
                        "quality_rating": quality_rating,
                        "notes": notes,
                        "strengths": strengths,
                        "limitations": limitations,
                        "assessor_name": assessor_name,
                        "assessment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "assessment_version": "2.0"
                    }
                    
                    st.session_state.studies.append(study_data)
                    
                    st.success(f"✅ Assessment saved successfully!")
                    
                    # Show immediate results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Quality Rating", quality_rating)
                    with col2:
                        st.metric("Total Stars", f"{total_stars}/9")
                    with col3:
                        overall_percentage = (total_stars / 9) * 100
                        st.metric("Overall Score", f"{overall_percentage:.1f}%")
                    
                    # Show domain breakdown
                    domain_scores = calculate_domain_scores(study_data)
                    st.subheader("📊 Domain Breakdown")
                    
                    domain_cols = st.columns(len(domain_scores))
                    for idx, (domain_name, scores) in enumerate(domain_scores.items()):
                        with domain_cols[idx]:
                            st.metric(
                                domain_name,
                                f"{scores['stars']}/{scores['max_stars']}",
                                f"{scores['percentage']:.0f}%"
                            )
                    
                else:
                    st.error("Please fill in all required fields marked with *")
    
    # View All Studies Page
    elif page == "📚 View All Studies":
        st.header("📚 Study Portfolio")
        
        if st.session_state.studies:
            # Search and filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_term = st.text_input("🔍 Search studies", placeholder="Enter study name, author, or journal")
            
            with col2:
                quality_filter = st.multiselect("Quality Filter", 
                                              ["Good Quality", "Fair Quality", "Poor Quality"],
                                              default=["Good Quality", "Fair Quality", "Poor Quality"])
            
            with col3:
                type_filter = st.multiselect("Study Type Filter",
                                           list(set(study['study_type'] for study in st.session_state.studies)),
                                           default=list(set(study['study_type'] for study in st.session_state.studies)))
            
            # Filter studies
            filtered_studies = st.session_state.studies
            
            if search_term:
                filtered_studies = [s for s in filtered_studies if 
                                  search_term.lower() in s['study_name'].lower() or
                                  search_term.lower() in s['authors'].lower() or
                                  search_term.lower() in s['journal'].lower()]
            
            if quality_filter:
                filtered_studies = [s for s in filtered_studies if s['quality_rating'] in quality_filter]
            
            if type_filter:
                filtered_studies = [s for s in filtered_studies if s['study_type'] in type_filter]
            
            st.write(f"Showing {len(filtered_studies)} of {len(st.session_state.studies)} studies")
            
            # Sort options
            sort_by = st.selectbox("Sort by", 
                                 ["Assessment Date", "Study Name", "Quality Rating", "Total Stars", "Publication Year"])
            
            if sort_by == "Assessment Date":
                filtered_studies = sorted(filtered_studies, key=lambda x: x['assessment_date'], reverse=True)
            elif sort_by == "Study Name":
                filtered_studies = sorted(filtered_studies, key=lambda x: x['study_name'])
            elif sort_by == "Quality Rating":
                quality_order = {"Good Quality": 3, "Fair Quality": 2, "Poor Quality": 1}
                filtered_studies = sorted(filtered_studies, key=lambda x: quality_order[x['quality_rating']], reverse=True)
            elif sort_by == "Total Stars":
                filtered_studies = sorted(filtered_studies, key=lambda x: x['total_stars'], reverse=True)
            elif sort_by == "Publication Year":
                filtered_studies = sorted(filtered_studies, key=lambda x: x['publication_year'], reverse=True)
            
            # Display studies
            for idx, study in enumerate(filtered_studies):
                with st.expander(f"{study['study_name']} - {study['quality_rating']}", expanded=False):
                    
                    # Study summary card
                    study_card = create_study_summary_card(study)
                    st.markdown(study_card, unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"📋 Duplicate", key=f"duplicate_{idx}"):
                            # Create a copy of the study
                            new_study = study.copy()
                            new_study['study_name'] = f"{study['study_name']} (Copy)"
                            new_study['assessment_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.studies.append(new_study)
                            st.success("Study duplicated successfully!")
                            st.rerun()
                    
                    with col2:
                        if st.button(f"📊 Details", key=f"details_{idx}"):
                            # Show detailed assessment
                            domain_scores = calculate_domain_scores(study)
                            
                            st.subheader("Detailed Assessment")
                            for domain_name, scores in domain_scores.items():
                                st.write(f"**{domain_name} Domain ({scores['stars']}/{scores['max_stars']} stars)**")
                                
                                criteria = NOS_CRITERIA[study['study_type']][domain_name]
                                for criterion_name, criterion in criteria.items():
                                    if criterion_name in study['assessment']:
                                        selected_option = study['assessment'][criterion_name]
                                        option_text = criterion['options'][selected_option]
                                        stars = criterion['stars'].get(selected_option, 0)
                                        
                                        if criterion_name == "comparability" and selected_option == "additional_factor":
                                            stars = 2
                                        
                                        star_display = "★" * stars if stars > 0 else "☆"
                                        st.write(f"- {criterion['question']}: {option_text} {star_display}")
                    
                    with col3:
                        if st.button(f"📤 Export", key=f"export_{idx}"):
                            # Export single study
                            single_study_df = export_to_csv_enhanced([study])
                            if single_study_df is not None:
                                csv_data = single_study_df.to_csv(index=False)
                                st.download_button(
                                    label=f"📥 Download {study['study_name']} Data",
                                    data=csv_data,
                                    file_name=f"{study['study_name'].replace(' ', '_')}_assessment.csv",
                                    mime="text/csv",
                                    key=f"download_{idx}"
                                )
                    
                    with col4:
                        if st.button(f"🗑️ Delete", key=f"delete_{idx}", type="secondary"):
                            if st.checkbox(f"Confirm deletion of {study['study_name']}", key=f"confirm_{idx}"):
                                st.session_state.studies.remove(study)
                                st.success("Study deleted successfully!")
                                st.rerun()
        else:
            st.info("No studies assessed yet. Go to 'Add New Study' to start.")
# Generate Report Page
    elif page == "📊 Generate Report":
        st.header("📊 Publication-Ready Reports")
        
        if st.session_state.studies:
            # Report options
            st.subheader("🎛️ Report Configuration")
            
            col1, col2 = st.columns(2)
            with col1:
                include_summary = st.checkbox("Include Summary Statistics", value=True)
                include_robvis = st.checkbox("Include Risk of Bias Summary", value=True)
                include_heatmap = st.checkbox("Include Domain Heatmap", value=True)
            
            with col2:
                include_table = st.checkbox("Include Publication Table", value=True)
                include_recommendations = st.checkbox("Include Methodological Recommendations", value=True)
                include_charts = st.checkbox("Include Statistical Charts", value=True)
            
            st.markdown("---")
            
            # Generate selected reports
            if include_summary:
                summary_html = create_risk_assessment_summary(st.session_state.studies)
                st.markdown(summary_html, unsafe_allow_html=True)
            
            if include_robvis:
                st.subheader("📈 Risk of Bias Summary")
                robvis_html = create_robvis_visualization(st.session_state.studies)
                if robvis_html:
                    st.markdown(robvis_html, unsafe_allow_html=True)
            
            if include_heatmap:
                st.subheader("🔍 Domain Heatmap")
                heatmap_html = create_domain_heatmap(st.session_state.studies)
                if heatmap_html:
                    st.markdown(heatmap_html, unsafe_allow_html=True)
            
            if include_table:
                st.subheader("📋 Publication-Ready Table")
                pub_table = create_publication_ready_table(st.session_state.studies)
                if pub_table is not None:
                    st.dataframe(pub_table, use_container_width=True)
                    
                    # Download publication table
                    csv_pub = pub_table.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Publication Table (CSV)",
                        data=csv_pub,
                        file_name=f"publication_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            if include_charts:
                st.subheader("📊 Statistical Charts")
                
                # Quality distribution
                stats = generate_summary_statistics(st.session_state.studies)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Quality Distribution**")
                    quality_counts = pd.Series(stats['quality_counts'])
                    st.bar_chart(quality_counts)
                
                with col2:
                    st.write("**Study Type Distribution**")
                    type_counts = pd.Series(stats['study_types'])
                    st.bar_chart(type_counts)
                
                # Domain performance
                st.write("**Average Domain Performance**")
                domain_performance = {k: v['average_percentage'] for k, v in stats['domain_averages'].items()}
                domain_df = pd.Series(domain_performance)
                st.bar_chart(domain_df)
                
                # Stars distribution
                st.write("**Stars Distribution**")
                stars_df = pd.Series(stats['star_distribution']).sort_index()
                st.bar_chart(stars_df)
            
            if include_recommendations:
                st.subheader("💡 Methodological Recommendations")
                rec_html = create_methodological_recommendations(st.session_state.studies)
                if rec_html:
                    st.markdown(rec_html, unsafe_allow_html=True)
            
        else:
            st.info("No studies to generate report. Please assess some studies first.")
    
    # Advanced Analytics Page
    elif page == "📈 Advanced Analytics":
        st.header("📈 Advanced Analytics Dashboard")
        
        if st.session_state.studies:
            stats = generate_summary_statistics(st.session_state.studies)
            
            # Time trend analysis
            st.subheader("📅 Temporal Analysis")
            
            # Create publication year distribution
            pub_years = [study['publication_year'] for study in st.session_state.studies]
            year_quality = {}
            
            for study in st.session_state.studies:
                year = study['publication_year']
                if year not in year_quality:
                    year_quality[year] = {'Good': 0, 'Fair': 0, 'Poor': 0, 'total': 0}
                
                quality = study['quality_rating'].split()[0]  # Get 'Good', 'Fair', or 'Poor'
                year_quality[year][quality] += 1
                year_quality[year]['total'] += 1
            
            if year_quality:
                year_df = pd.DataFrame.from_dict(year_quality, orient='index')
                year_df = year_df.sort_index()
                
                st.write("**Quality Trends by Publication Year**")
                st.bar_chart(year_df[['Good', 'Fair', 'Poor']])
            
            # Domain comparison
            st.subheader("🔄 Domain Performance Analysis")
            
            domain_comparison = {}
            for study in st.session_state.studies:
                domain_scores = calculate_domain_scores(study)
                for domain_name, scores in domain_scores.items():
                    if domain_name not in domain_comparison:
                        domain_comparison[domain_name] = []
                    domain_comparison[domain_name].append(scores['percentage'])
            
            if domain_comparison:
                comparison_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in domain_comparison.items()]))
                
                st.write("**Average Domain Performance**")
                domain_means = comparison_df.mean().sort_values(ascending=False)
                st.bar_chart(domain_means)
                
                # Domain statistics table
                st.write("**Domain Statistics Summary**")
                domain_stats = comparison_df.describe().round(2)
                st.dataframe(domain_stats, use_container_width=True)
            
            # Quality improvement analysis
            st.subheader("🎯 Quality Improvement Analysis")
            
            low_scoring_studies = [s for s in st.session_state.studies if s['total_stars'] < 5]
            if low_scoring_studies:
                st.warning(f"⚠️ {len(low_scoring_studies)} studies scored below 5 stars")
                
                # Analyze common issues
                common_issues = {}
                for study in low_scoring_studies:
                    domain_scores = calculate_domain_scores(study)
                    for domain_name, scores in domain_scores.items():
                        if scores['percentage'] < 50:
                            common_issues[domain_name] = common_issues.get(domain_name, 0) + 1
                
                if common_issues:
                    st.write("**Most Common Issues in Low-Quality Studies:**")
                    for domain, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"- {domain}: {count} studies ({count/len(low_scoring_studies)*100:.1f}%)")
            else:
                st.success("✅ All studies scored 5 or more stars!")
            
            # Advanced metrics
            st.subheader("📊 Advanced Quality Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Calculate median score
                all_scores = [study['total_stars'] for study in st.session_state.studies]
                median_score = np.median(all_scores)
                st.metric("Median Score", f"{median_score:.1f}/9")
            
            with col2:
                # Calculate standard deviation
                std_score = np.std(all_scores)
                st.metric("Score Std Dev", f"{std_score:.2f}")
            
            with col3:
                # High quality percentage
                high_quality_pct = (stats['quality_counts']['Good Quality'] / stats['total_studies']) * 100
                st.metric("High Quality %", f"{high_quality_pct:.1f}%")
            
            # Study characteristics analysis
            st.subheader("🔬 Study Characteristics Analysis")
            
            # Sample size analysis (if available)
            sample_sizes = [study.get('sample_size', 0) for study in st.session_state.studies if study.get('sample_size', 0) > 0]
            if sample_sizes:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Median Sample Size", f"{int(np.median(sample_sizes)):,}")
                with col2:
                    st.metric("Total Participants", f"{sum(sample_sizes):,}")
            
            # Funding analysis (if available)
            funding_studies = [study for study in st.session_state.studies if study.get('funding')]
            if funding_studies:
                st.write(f"**Funding Information Available:** {len(funding_studies)}/{len(st.session_state.studies)} studies")
            
        else:
            st.info("No data available for analytics. Please assess some studies first.")
    
    # Compare Studies Page
    elif page == "🔄 Compare Studies":
        st.header("🔄 Study Comparison")
        
        if len(st.session_state.studies) >= 2:
            # Select studies to compare
            study_names = [study['study_name'] for study in st.session_state.studies]
            
            col1, col2 = st.columns(2)
            with col1:
                study1_name = st.selectbox("Select First Study", study_names, key="compare1")
            with col2:
                study2_name = st.selectbox("Select Second Study", 
                                         [name for name in study_names if name != study1_name], 
                                         key="compare2")
            
            if study1_name and study2_name:
                study1 = next(s for s in st.session_state.studies if s['study_name'] == study1_name)
                study2 = next(s for s in st.session_state.studies if s['study_name'] == study2_name)
                
                # Comparison table
                st.subheader("📊 Head-to-Head Comparison")
                
                comparison_data = {
                    'Metric': ['Study Type', 'Publication Year', 'Total Stars', 'Quality Rating', 'Sample Size'],
                    study1_name: [
                        study1['study_type'],
                        study1['publication_year'],
                        f"{study1['total_stars']}/9",
                        study1['quality_rating'],
                        study1.get('sample_size', 'N/A')
                    ],
                    study2_name: [
                        study2['study_type'],
                        study2['publication_year'],
                        f"{study2['total_stars']}/9",
                        study2['quality_rating'],
                        study2.get('sample_size', 'N/A')
                    ]
                }
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
                
                # Domain comparison
                st.subheader("🔍 Domain-wise Comparison")
                
                domain1 = calculate_domain_scores(study1)
                domain2 = calculate_domain_scores(study2)
                
                all_domains = set(list(domain1.keys()) + list(domain2.keys()))
                
                domain_comp_data = []
                for domain in all_domains:
                    row = {'Domain': domain}
                    
                    if domain in domain1:
                        row[f'{study1_name} Stars'] = f"{domain1[domain]['stars']}/{domain1[domain]['max_stars']}"
                        row[f'{study1_name} %'] = f"{domain1[domain]['percentage']:.1f}%"
                    else:
                        row[f'{study1_name} Stars'] = 'N/A'
                        row[f'{study1_name} %'] = 'N/A'
                    
                    if domain in domain2:
                        row[f'{study2_name} Stars'] = f"{domain2[domain]['stars']}/{domain2[domain]['max_stars']}"
                        row[f'{study2_name} %'] = f"{domain2[domain]['percentage']:.1f}%"
                    else:
                        row[f'{study2_name} Stars'] = 'N/A'
                        row[f'{study2_name} %'] = 'N/A'
                    
                    domain_comp_data.append(row)
                
                domain_comp_df = pd.DataFrame(domain_comp_data)
                st.dataframe(domain_comp_df, use_container_width=True)
                
                # Visual comparison
                st.subheader("📊 Visual Comparison")
                
                # Create comparison chart data
                comparison_chart_data = {}
                for domain in all_domains:
                    if domain in domain1 and domain in domain2:
                        comparison_chart_data[domain] = [domain1[domain]['percentage'], domain2[domain]['percentage']]
                
                if comparison_chart_data:
                    chart_df = pd.DataFrame(comparison_chart_data, index=[study1_name[:20], study2_name[:20]])
                    st.bar_chart(chart_df)
        
        elif len(st.session_state.studies) == 1:
            st.info("You need at least 2 studies to perform comparisons.")
        else:
            st.info("No studies available for comparison. Please assess some studies first.")
    
    # Export Data Page
    elif page == "💾 Export Data":
        st.header("💾 Enhanced Data Export")
        
        if st.session_state.studies:
            # Export options
            st.subheader("📋 Export Configuration")
            
            col1, col2 = st.columns(2)
            with col1:
                export_format = st.selectbox("Export Format", 
                                           ["CSV (Detailed)", "CSV (Summary)", "JSON (Complete)"])
                include_metadata = st.checkbox("Include Metadata", value=True)
            
            with col2:
                include_domain_scores = st.checkbox("Include Domain Scores", value=True)
                include_recommendations = st.checkbox("Include Assessment Notes", value=True)
            
            # Generate export data
            if export_format == "CSV (Detailed)":
                export_df = export_to_csv_enhanced(st.session_state.studies)
                if export_df is not None:
                    st.subheader("📋 Export Preview")
                    st.dataframe(export_df.head(), use_container_width=True)
                    
                    csv_data = export_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Detailed CSV",
                        data=csv_data,
                        file_name=f"nos_detailed_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            elif export_format == "CSV (Summary)":
                summary_df = create_publication_ready_table(st.session_state.studies)
                if summary_df is not None:
                    st.subheader("📋 Export Preview")
                    st.dataframe(summary_df, use_container_width=True)
                    
                    csv_data = summary_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Summary CSV",
                        data=csv_data,
                        file_name=f"nos_summary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            elif export_format == "JSON (Complete)":
                # Enhanced JSON export with metadata
                export_data = {
                    "export_info": {
                        "tool_name": "Newcastle-Ottawa Scale Assessment Tool",
                        "version": "2.0",
                        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_studies": len(st.session_state.studies),
                        "assessor": "Multiple" if len(set(s.get('assessor_name', 'Unknown') for s in st.session_state.studies)) > 1 else st.session_state.studies[0].get('assessor_name', 'Unknown')
                    },
                    "summary_statistics": generate_summary_statistics(st.session_state.studies),
                    "studies": st.session_state.studies
                }
                
                json_data = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    label="📥 Download Complete JSON",
                    data=json_data,
                    file_name=f"nos_complete_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            # Statistics summary
            st.subheader("📈 Export Summary")
            stats = generate_summary_statistics(st.session_state.studies)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Studies", stats['total_studies'])
            with col2:
                st.metric("Good Quality", stats['quality_counts']['Good Quality'])
            with col3:
                st.metric("Fair Quality", stats['quality_counts']['Fair Quality'])
            with col4:
                st.metric("Poor Quality", stats['quality_counts']['Poor Quality'])
            
            # Data management
            st.subheader("🗑️ Data Management")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Backup All Data", type="secondary", use_container_width=True):
                    backup_data = {
                        "studies": st.session_state.studies,
                        "backup_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    backup_json = json.dumps(backup_data, indent=2, default=str)
                    st.download_button(
                        label="💾 Download Backup File",
                        data=backup_json,
                        file_name=f"nos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
                    if st.checkbox("⚠️ I understand this will permanently delete all assessments"):
                        st.session_state.studies = []
                        st.success("All data cleared successfully!")
                        st.rerun()
        
        else:
            st.info("No data to export. Please assess some studies first.")
# Assessment Guide Page
    elif page == "📖 Assessment Guide":
        st.header("📖 Newcastle-Ottawa Scale Assessment Guide")
        
        # Quick reference guide
        st.subheader("🎯 Quick Reference")
        
        guide_tabs = st.tabs(["Overview", "Cohort Studies", "Case-Control Studies", "Cross-Sectional Studies", "Interpretation"])
        
        with guide_tabs[0]:
            st.markdown("""
            ### 📋 Newcastle-Ottawa Scale Overview
            
            The Newcastle-Ottawa Scale (NOS) is a quality assessment tool for non-randomized studies in meta-analyses.
            
            **Key Features:**
            - ⭐ **Star-based scoring system** (maximum 9 stars for cohort/case-control, 8 for cross-sectional)
            - 🏗️ **Three domains:** Selection, Comparability, Outcome/Exposure
            - 📊 **Standardized criteria** for consistent assessment
            
            **Quality Interpretation:**
            - 🟢 **Good Quality:** ≥7 stars (cohort/case-control), ≥6 stars (cross-sectional)
            - 🟡 **Fair Quality:** 5-6 stars (cohort/case-control), 4-5 stars (cross-sectional)
            - 🔴 **Poor Quality:** <5 stars (cohort/case-control), <4 stars (cross-sectional)
            
            **Assessment Tips:**
            - 📖 Read the full paper carefully before assessment
            - 🔍 Look for supplementary materials and protocols
            - 📝 Document your reasoning for each criterion
            - 👥 Consider dual assessment for important decisions
            """)
        
        with guide_tabs[1]:
            st.markdown("""
            ### 🔄 Cohort Studies Assessment
            
            **Selection Domain (4 stars maximum):**
            1. **Representativeness of exposed cohort** - Is the sample representative?
            2. **Selection of non-exposed cohort** - Drawn from same community?
            3. **Ascertainment of exposure** - How reliable is exposure measurement?
            4. **Outcome not present at start** - Temporal relationship established?
            
            **Comparability Domain (2 stars maximum):**
            5. **Comparability of cohorts** - Are confounders controlled?
               - 1 star: Most important factor controlled
               - 2 stars: Additional factors controlled
            
            **Outcome Domain (3 stars maximum):**
            6. **Assessment of outcome** - How reliable is outcome measurement?
            7. **Follow-up length** - Adequate time for outcomes to occur?
            8. **Adequacy of follow-up** - Complete follow-up achieved?
            
            **Common Issues:**
            - ❌ Selection bias in cohort recruitment
            - ❌ Inadequate control for confounding
            - ❌ High loss to follow-up rates
            - ❌ Self-reported outcomes without validation
            """)
        
        with guide_tabs[2]:
            st.markdown("""
            ### 🎯 Case-Control Studies Assessment
            
            **Selection Domain (4 stars maximum):**
            1. **Case definition adequate** - Clear, validated case definition?
            2. **Representativeness of cases** - Consecutive or representative series?
            3. **Selection of controls** - Community vs hospital controls?
            4. **Definition of controls** - No history of outcome?
            
            **Comparability Domain (2 stars maximum):**
            5. **Comparability** - Are confounders controlled?
               - 1 star: Most important factor controlled
               - 2 stars: Additional factors controlled
            
            **Exposure Domain (3 stars maximum):**
            6. **Ascertainment of exposure** - Reliable exposure measurement?
            7. **Same method for cases/controls** - Consistent assessment methods?
            8. **Non-response rate** - Similar response rates?
            
            **Common Issues:**
            - ❌ Hospital-based controls (selection bias)
            - ❌ Recall bias in exposure assessment
            - ❌ Inadequate matching or adjustment
            - ❌ Different assessment methods for cases/controls
            """)
        
        with guide_tabs[3]:
            st.markdown("""
            ### 📊 Cross-Sectional Studies Assessment
            
            **Selection Domain (4 stars maximum):**
            1. **Representativeness** - Representative sample of target population?
            2. **Sample size** - Justified and adequate sample size?
            3. **Non-respondents** - Response rate adequate or non-respondents described?
            4. **Ascertainment of exposure** - Validated measurement tools used?
            
            **Comparability Domain (2 stars maximum):**
            5. **Comparability** - Are confounders controlled?
               - 1 star: Most important factor controlled
               - 2 stars: Additional factors controlled
            
            **Outcome Domain (2 stars maximum):**
            6. **Assessment of outcome** - Reliable outcome measurement?
            7. **Statistical test** - Appropriate statistical methods used?
            
            **Common Issues:**
            - ❌ Convenience sampling without justification
            - ❌ Low response rates without analysis
            - ❌ Self-reported measures without validation
            - ❌ Inadequate statistical analysis
            """)
        
        with guide_tabs[4]:
            st.markdown("""
            ### 📈 Interpretation Guidelines
            
            **Overall Quality Assessment:**
            - 🟢 **7-9 stars (Good):** High-quality study with minimal bias risk
            - 🟡 **5-6 stars (Fair):** Moderate quality with some limitations
            - 🔴 **<5 stars (Poor):** Significant methodological concerns
            
            **Domain-Specific Interpretation:**
            - **Selection:** Foundation of study validity
            - **Comparability:** Critical for causal inference
            - **Outcome/Exposure:** Determines measurement reliability
            
            **Reporting Recommendations:**
            1. 📊 Present overall quality distribution
            2. 🔍 Highlight domain-specific patterns
            3. 📝 Discuss limitations and their impact
            4. 🎯 Consider sensitivity analyses by quality
            
            **Publication Guidelines:**
            - Include detailed assessment criteria
            - Report inter-rater reliability if applicable
            - Discuss quality assessment limitations
            - Consider GRADE approach for evidence synthesis
            
            **Red Flags (Consider Exclusion):**
            - ⚠️ No clear case definition
            - ⚠️ Extremely high loss to follow-up (>50%)
            - ⚠️ Self-reported outcomes without any validation
            - ⚠️ No control for any confounding factors
            """)
        
        # Interactive criteria explorer
        st.subheader("🔍 Interactive Criteria Explorer")
        
        selected_study_type = st.selectbox("Explore criteria for:", list(NOS_CRITERIA.keys()))
        
        if selected_study_type:
            criteria = NOS_CRITERIA[selected_study_type]
            
            for domain_name, domain in criteria.items():
                with st.expander(f"{domain_name} Domain Details"):
                    st.write(f"**Maximum Stars:** {2 if domain_name == 'Comparability' else len(domain)}")
                    
                    for criterion_name, criterion in domain.items():
                        st.write(f"**{criterion['question']}**")
                        
                        # Show scoring options
                        for option_key, option_text in criterion['options'].items():
                            stars = criterion['stars'].get(option_key, 0)
                            if criterion_name == "comparability" and option_key == "additional_factor":
                                stars = 2
                            star_display = "★" * stars if stars > 0 else "☆"
                            st.write(f"  - {option_text} {star_display}")
                        
                        st.write("---")
        
        # Best practices section
        st.subheader("📚 Best Practices")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Assessment Best Practices:**
            - 📋 Use standardized forms
            - 👥 Dual independent assessment
            - 📝 Document decisions clearly
            - 🔄 Regular calibration exercises
            - 📊 Calculate inter-rater reliability
            """)
        
        with col2:
            st.markdown("""
            **Reporting Guidelines:**
            - 📈 Include summary statistics
            - 🎯 Discuss quality patterns
            - ⚖️ Assess impact on results
            - 🔍 Consider sensitivity analyses
            - 📖 Follow PRISMA guidelines
            """)
    
    # Footer with enhanced information
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
        <h4 style="color: #2c3e50; margin-bottom: 15px;">Newcastle-Ottawa Scale Assessment Tool v2.0</h4>
        <p style="margin-bottom: 10px;"><strong>Developed for systematic review and meta-analysis research</strong></p>
        <p style="margin-bottom: 10px;">© 2024 Muhammad Nabeel Saddique | Nibras Research Academy</p>
        <p style="margin-bottom: 15px;"><em>Advanced bias assessment for evidence-based medicine</em></p>
        
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 15px;">
            <span style="background: #3498db; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                🏥 Clinical Research
            </span>
            <span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                📊 Publication Ready
            </span>
            <span style="background: #6f42c1; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                🔬 Evidence-Based
            </span>
            <span style="background: #fd7e14; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">
                ⚡ Advanced Analytics
            </span>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #3498db;">
            <h5 style="color: #2c3e50; margin-bottom: 10px;">📊 Current Session Summary</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; font-size: 14px;">
                <div>
                    <strong>Studies Assessed:</strong><br>
                    <span style="color: #3498db; font-size: 18px; font-weight: bold;">{len(st.session_state.studies)}</span>
                </div>
    """.format(len=len), unsafe_allow_html=True)
    
    if st.session_state.studies:
        stats = generate_summary_statistics(st.session_state.studies)
        st.markdown(f"""
                <div>
                    <strong>Good Quality:</strong><br>
                    <span style="color: #28a745; font-size: 18px; font-weight: bold;">{stats['quality_counts']['Good Quality']}</span>
                </div>
                <div>
                    <strong>Fair Quality:</strong><br>
                    <span style="color: #ffc107; font-size: 18px; font-weight: bold;">{stats['quality_counts']['Fair Quality']}</span>
                </div>
                <div>
                    <strong>Poor Quality:</strong><br>
                    <span style="color: #dc3545; font-size: 18px; font-weight: bold;">{stats['quality_counts']['Poor Quality']}</span>
                </div>
                <div>
                    <strong>Overall Score:</strong><br>
                    <span style="color: #6f42c1; font-size: 18px; font-weight: bold;">{stats['overall_quality_score']:.1f}%</span>
                </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
            </div>
        </div>
        
        <div style="margin-top: 15px; font-size: 11px; color: #6c757d;">
            <p>For support, documentation, or feature requests, contact the development team.</p>
            <p>Built with ❤️ for the research community | Streamlit • Python • Evidence-Based Medicine</p>
            <p><strong>Requirements:</strong> streamlit, pandas, numpy</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

# Requirements for deployment
# Create requirements.txt with:
# streamlit
# pandas  
# numpy