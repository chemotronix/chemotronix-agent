import streamlit as st
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os
# import dotenv
from streamlit_option_menu import option_menu




# dotenv.load_dotenv()


st.set_page_config(page_title="Chemotronix Climate Agent", page_icon="🌱", layout="wide")

# Sidebar navigation
st.sidebar.title("🌍 Chemotronix Agent")
# page = st.sidebar.radio("Go to", ["Chat", "About"])
with st.sidebar:
        page = option_menu(
            menu_title=None,
            options = ["Chat", "About"], #"Upload Files", "Manage Documents", 
            icons=["chat-dots", "info-circle"], #"cloud-upload", "file-earmark-diff",
        )

# Azure AI Agent setup
@st.cache_resource
def init_client():
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.environ["AIPROJECT_CONNECTION"]
    )
    agent = project_client.agents.get_agent("asst_JhY1U2DWXy2stH4BCtF8Yfdy")
    thread = project_client.agents.create_thread()
    return project_client, agent, thread

project_client, agent, thread = init_client()

if page == "Chat":
    st.title("💬 Climate Chatbot")
    
    # Clear button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))

        project_client.agents.create_message(thread_id=thread.id, role="user", content=user_input)
        run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

        messages = project_client.agents.list_messages(thread_id=thread.id)
        assistant_message = next((m for m in messages.data if m.role == "assistant"), None)

        if assistant_message:
            reply = assistant_message.content[0].text.value
            st.chat_message("assistant").markdown(reply)
            st.session_state.chat_history.append(("assistant", reply))

elif page == "About":
    st.title("📘 About This Project")
    st.markdown("""
    **Chemotronix Climate Chatbot** is a project developed for the [AI Agents Hackathon 2025](https://microsoft.github.io/AI_Agents_Hackathon/).  
    Our goal is to empower communities and organizations across Africa with accessible, AI-powered tools for:
    
    - 🌿 Emissions education
    - 🔍 Climate insights via RAG (Retrieval-Augmented Generation)
    - 🧠 Agentic support for net-zero transitions

    ### 🔧 Technologies
    - Python 🐍 + Streamlit 🚀
    - Azure AI Agent Service 🤖
    - Azure Cognitive Search + OpenAI for RAG 🧠
    - IoT + Clean energy integration (planned)

    ### 👥 Team Chemotronix
    A passionate group of engineers, developers, and scientists committed to climate action through technology.

    ---
    *Have questions or want to collaborate? Chat with the agent on the left!*
    """)

