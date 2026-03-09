import streamlit as st

st.set_page_config(page_title="AI Recruitment Agent", page_icon=":robot_face:", layout="wide")
st.title("AI Recruitment Agent")

import ui
from agents import ResumeAnalysisAgent
import atexit

ROLE_REQUIREMENTS = {
    "AI/ML Engineer": [
        "Python", "PyTorch", "TensorFlow", "Scikit-learn", "Data Analysis", 
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", 
        "Model Deployment", "AWS", "GCP", "Azure", "Git", "Problem-Solving", 
        "Communication", "Jupyter", "Pandas", "NumPy"
    ],
    "Data Scientist": [
        "Python", "R", "SQL", "Data Visualization", "Statistical Analysis", 
        "Machine Learning", "Deep Learning", "NLP", "Hadoop", "Spark", 
        "AWS", "GCP", "Azure", "Git", "Tableau", "Power BI"
    ],
    "Software Engineer": [
        "Python", "Java", "C++", "C#", "Software Development", 
        "Data Structures", "Algorithms", "System Design", "Git", 
        "SOLID Principles", "Design Patterns", "Testing", "CI/CD"
    ],
    "Backend Engineer": [
        "Python", "Java", "C++", "Node.js", "Django", "Flask", "FastAPI",
        "SQL", "NoSQL", "MongoDB", "PostgreSQL", "API Development",
        "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Microservices"
    ],
    "Frontend Engineer": [
        "HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js", "TypeScript",
        "Responsive Design", "Redux", "REST API", "GraphQL", "Git",
        "Web Performance", "Accessibility", "SASS", "Webpack"
    ],
    "Data Engineer": [
        "Python", "SQL", "Apache Spark", "Hadoop", "ETL", "Data Warehousing",
        "PostgreSQL", "MySQL", "MongoDB", "AWS", "GCP", "Azure",
        "Airflow", "Kafka", "Docker", "Big Data"
    ],
    "Product Manager": [
        "Product Management", "Market Research", "User Experience", "Agile",
        "Scrum", "Project Management", "Analytics", "Roadmapping",
        "Stakeholder Management", "Communication", "Leadership"
    ],
    "UX/UI Designer": [
        "UX Design", "UI Design", "Prototyping", "Figma", "Adobe XD",
        "Adobe Creative Suite", "Usability Testing", "User Research",
        "Wireframing", "Design Systems", "Interaction Design"
    ],
    "Data Analyst": [
        "SQL", "Excel", "Power BI", "Tableau", "Python", "R",
        "Data Visualization", "Statistical Analysis", "Data Cleaning",
        "Google Analytics", "Looker", "Problem-Solving"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "Jenkins", "Git", "AWS", "GCP", "Azure",
        "Linux", "Python", "Terraform", "CI/CD", "Monitoring", "Logging"
    ],
    "Security Engineer": [
        "Cybersecurity", "Network Security", "Encryption", "Penetration Testing",
        "Python", "Linux", "SQL", "OWASP", "AWS", "Azure", "Firewalls"
    ],
    "Cloud Architect": [
        "AWS", "GCP", "Azure", "Cloud Architecture", "Microservices",
        "Docker", "Kubernetes", "Terraform", "Scalability", "Security"
    ]
}

if 'resume_agent' not in st.session_state:
    st.session_state.resume_agent = None

if 'resume_analyzed' not in st.session_state:
    st.session_state.resume_analyzed = False

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None



#Important part to check
def setup_agent(config):
    """setup the resume analysis agent with the provided configuration"""

    if not config["api_key"]:
        st.error("Please enter your GROQ API key to proceed.")
        return None
    
    #initialize or update the agent with API key
    if st.session_state.resume_agent is None:
        st.session_state.resume_agent = ResumeAnalysisAgent(config["api_key"])
    else:
        st.session_state.resume_agent.api_key = config["api_key"]

    return st.session_state.resume_agent

def analyze_resume(agent, resume_file, role, custom_jd):
    if not resume_file:
        st.error("Please upload a resume file to proceed.")
        return None
    try:
        with st.spinner("Analyzing resume..."):
            if custom_jd:
                result = agent.analyze_resume(resume_file, role, custom_jd=custom_jd)
            else:
                result = agent.analyze_resume(resume_file, role_requirements=ROLE_REQUIREMENTS[role])

        st.session_state.resume_analyzed = True
        st.session_state.analysis_results = result
        return result
    except Exception as e:
        st.error(f"Error analyzing resume: {e}")
        return None
    

def ask_questions(agent, question):
    if not question:
        st.error("Please enter some questions to ask the agent.")
        return None
    try:
        with st.spinner("Asking questions..."):
            response = agent.ask_question(question)
        return response
    except Exception as e:
        st.error(f"Error asking questions: {e}")
        return None

def generate_interview_questions(agent, question_types, difficulty, num_questions, target_role=""):
    """Generate interview questions based on the resume"""
    try:
        with st.spinner("Generating interview questions..."):
            questions = agent.generate_interview_questions(question_types, difficulty, num_questions, target_role)
        return questions
    except Exception as e:
        st.error(f"Error generating interview questions: {e}")
        return None

def improve_resume(agent, improvement_areas, target_role):
    """Generate resume improvement suggestions based on the analysis results"""
    try:
        with st.spinner("Generating resume improvement suggestions..."):
            suggestions = agent.improve_resume(improvement_areas, target_role)
        return suggestions
    except Exception as e:
        st.error(f"Error generating resume improvement suggestions: {e}")
        return None


def cleanup():
    """Clean up temporary files"""
    if st.session_state.resume_agent:
        st.session_state.resume_agent.cleanup()

#register cleanup function to run on exit
atexit.register(cleanup)

def main():
    #setup page UI
    ui.setup_page()
    ui.display_header()

    # setup sidebar and get configuration
    config = ui.setup_sidebar()

    #setup the agent
    agent = setup_agent(config)

    #create tabs for different functionalities
    tabs = ui.create_tabs()

    # tab 1 : resume analysis
    with tabs[0]:
        role, custom_jd = ui.role_selection_section(ROLE_REQUIREMENTS)
        uploaded_resume = ui.resume_upload_section()

        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button("ANALYZE RESUME", type="primary"):
                if agent and uploaded_resume:
                    analyze_resume(agent, uploaded_resume, role, custom_jd)

        # display analysis results
        if st.session_state.analysis_results:
            ui.display_analysis_results(st.session_state.analysis_results)

    # tab 2 : resume q and a
    with tabs[1]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.resume_qa_section(
                has_resume=True,
                ask_questions_fn=lambda q: ask_questions(st.session_state.resume_agent, q)
            )
        else:
            st.warning("Please analyze a resume first to enable the Q&A section.")

    # tab 3 : interview questions
    with tabs[2]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.interview_question_generation_section(
                has_resume=True,
                generate_questions_func=lambda types, diff, num, role_target="":
                    generate_interview_questions(st.session_state.resume_agent, types, diff, num, role_target),
                role_list=list(ROLE_REQUIREMENTS.keys())
            )
        else:
            st.warning("Please analyze a resume first to enable the interview question generation section.")

    # tab 4 : resume improvement suggestions
    with tabs[3]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.resume_improvement_section(
                has_resume=True,
                improvement_fn=lambda areas, role:
                    improve_resume(st.session_state.resume_agent, areas, role),
                analysis_results=st.session_state.analysis_results
            )
        else:
            st.warning("Please analyze a resume first to enable the resume improvement section.")

        
if  __name__ == "__main__":
    main()