import streamlit as st
import openai
from streamlit_option_menu import option_menu
import os
from fpdf import FPDF

# Set page config
st.set_page_config(page_title="Virtual Doctor", page_icon="🩺", layout="wide")

# Initialize OpenAI API
openai.api_key = st.secrets["openai_api_key"]

# Initialize session state for navigation if not exists
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Sidebar
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Doctor Chat", "Nutrition", "About"],
        icons=["house", "chat-dots", "apple", "info-circle"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#1e3d59"},
            "icon": {"color": "#f5f0e1", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#ffc13b"},
            "nav-link-selected": {"background-color": "#ff6e40"},
        }
    )

    if selected:
        st.session_state.page = selected

# Add some CSS to make it attractive
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #1e3d59 0%, #f5f0e1 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #1e3d59 0%, #f5f0e1 100%);
    }
    .stButton>button {
        background-color: #ff6e40;
        color: #f5f0e1;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ffc13b;
        color: #1e3d59;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input {
        background-color: #f5f0e1;
    }
    .rounded-image {
        border-radius: 50%; /* Makes the image round */
        width: 150px; /* Set width */
        height: 150px; /* Set height */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Helper functions
def get_ai_response(prompt, system_role):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in AI response: {str(e)}")
        return "I'm sorry, I couldn't generate a response at this time."

def get_nutrition_plan(age, weight, height, goal, duration):
    bmi = weight / ((height/100)**2)
    prompt = f"Create a nutrition and exercise plan for a {age}-year-old person with a BMI of {bmi:.1f}, aiming to {goal} over {duration}. Include daily meal plans and exercise routines."
    return get_ai_response(prompt, "You are a knowledgeable nutritionist and fitness expert.")

def generate_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(filename)

# Page functions
def home():
    st.title("Welcome to Virtual Doctor 🏥")
    st.write("Are you feeling sick? Let our AI-powered doctor assist you!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Consult Doctor"):
            st.session_state.page = "Doctor Chat"
            st.rerun()
    with col2:
        if st.button("Get Nutrition Advice"):
            st.session_state.page = "Nutrition"
            st.rerun()

    # Add some animations using Lottie
    st.markdown(
        """
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <lottie-player src="https://assets2.lottiefiles.com/packages/lf20_5njp3vgg.json" background="transparent" speed="1" style="width: 300px; height: 300px;" loop autoplay></lottie-player>
        """,
        unsafe_allow_html=True
    )

def doctor_chat():
    st.title("Doctor Chat 👨‍⚕️")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What are your symptoms?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = get_ai_response(prompt, "You are a helpful and knowledgeable doctor.")
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("Generate PDF Report"):
        if st.session_state.messages:
            content = "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
            filename = "doctor_chat_report.pdf"
            generate_pdf(content, filename)
            st.success(f"PDF report generated successfully! Saved as {filename}")
        else:
            st.warning("No chat history to generate a report from.")

def nutrition():
    st.title("Nutrition Planner 🥗")
    
    age = st.number_input("Age", min_value=1, max_value=120, value=30)
    weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
    goal = st.selectbox("Goal", ["lose weight", "gain weight", "maintain weight"])
    duration = st.selectbox("Plan Duration", ["1 week", "2 weeks", "1 month"])

    if st.button("Generate Nutrition Plan"):
        plan = get_nutrition_plan(age, weight, height, goal, duration)
        st.session_state.nutrition_plan = plan
        st.markdown(plan)

        if st.button("Generate PDF Report"):
            if hasattr(st.session_state, 'nutrition_plan'):
                filename = "nutrition_plan_report.pdf"
                generate_pdf(st.session_state.nutrition_plan, filename)
                st.success(f"PDF report generated successfully! Saved as {filename}")
            else:
                st.warning("No nutrition plan to generate a report from.")

def about():
    st.title("About Us 👥")
    st.write("We are a team of six passionate developers working on this Virtual Doctor project.")

    # Add this description and center the content
    
    team_members = [
        {"name": "Muhammad Jawad", "role": "Data Analyst", "image": "https://media.licdn.com/dms/image/v2/D4D03AQGhdbU8hITDEA/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1709276424296?e=1735776000&v=beta&t=UXRAsL9BFiT2m4YbKBs1RdPOBkV1ZT6W6Uj6CEx0xw8", "linkedin": "https://www.linkedin.com/in/muhammad-jawad-86507b201/", "github": "https://github.com/mj-awad17/"},
        {"name": "Tayyab Sajjad", "role": "Full-Stack Developer", "image": "https://media.licdn.com/dms/image/v2/D4E03AQFGCSfC75SgPw/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1725519960647?e=1735776000&v=beta&t=FOrIVMmQlYFY7RTUp4JLNdE5LmHkdTA6E-rLxBpVMtU", "linkedin": "www.linkedin.com/in/devtayyabsajjad", "github": "https://github.com/devtayyabsajjad"},
        {"name": "Asim Khan", "role": "Full-Stack Developer", "image": "https://media.licdn.com/dms/image/v2/D4D03AQGluxA_ik6tyA/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1728585802329?e=1735776000&v=beta&t=JHbLAbAVXJ0O-Blvn29orHEGXKUKntah-k3Mz7vf_Hc", "linkedin": "https://www.linkedin.com/in/asim-khan-baloch/", "github": "https://github.com/Asimbaloch"},
        {"name": "Muhammad Ibrahim Qasmi", "role": "Data Scientist", "image": "https://media.licdn.com/dms/image/v2/D4D03AQFSX9z8C2gRTg/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1722410662066?e=1735776000&v=beta&t=ycgHQ0eCvpjEak9WUUIha1-x--_tgJGWsXxF-hnMGyk", "linkedin": "https://www.linkedin.com/in/muhammad-ibrahim-qasmi-9876a1297/", "github": "https://github.com/muhammadibrahim313"},
        {"name": "Ahmad Fakhar", "role": "Data Analyst", "image": "https://media.licdn.com/dms/image/v2/D5603AQGna-FRibZYXw/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1710361402580?e=1735776000&v=beta&t=T9377zLifYhns1ReLAk0bxi_TtY1cWlnJLqARLfLNnU", "linkedin": "https://www.linkedin.com/in/ahmad-fakhar-357742258/", "github": "https://github.com/Ahmad-Fakhar"},
        {"name": "Muhammad Bilal", "role": "DevOps Engineer", "image": "https://media.licdn.com/dms/image/v2/D4E03AQFyK8SIQkAFpA/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1688370356823?e=1735776000&v=beta&t=1Uo6GsirXGHBxUzxrjJ77x6xBB4uduHmV5uyDaRK5Nw", "linkedin": "https://www.linkedin.com/in/muhammad-bilal-a75782280/", "github": "https://github.com/bilal77511"},
    ]

    cols = st.columns(3)
    for idx, member in enumerate(team_members):
        with cols[idx % 3]:
            st.markdown(f'<div style=><img src="{member["image"]}" style="width: 150px; height: 150px; border-radius: 50%;" /></div>', unsafe_allow_html=True)
            st.subheader(member["name"])
            st.write(member["role"])
            st.write(f"[LinkedIn]({member['linkedin']}) | [GitHub]({member['github']})")

# Main content
if st.session_state.page == "Home":
    home()
elif st.session_state.page == "Doctor Chat":
    doctor_chat()
elif st.session_state.page == "Nutrition":
    nutrition()
elif st.session_state.page == "About":
    about()