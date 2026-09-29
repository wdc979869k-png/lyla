import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Page configuration
st.set_page_config(
    page_title="LifeHelper AI",
    page_icon="🌱",
    layout="centered"
)

# App title
st.title("🌱 LifeHelper AI")
st.subheader("Your personal AI life assistant")

st.write(
    "Having a problem? Talk to LifeHelper AI. "
    "I'm here to help you think clearly, "
    "find solutions, and take your next step."
)

# AI personality and instructions
SYSTEM_PROMPT = """
You are LifeHelper AI, a friendly, thoughtful, and supportive
personal assistant.

Your mission is to help people solve everyday life problems.

You can help with:
- Personal problems
- School and study challenges
- Work and career decisions
- Relationships and communication
- Goal setting and personal development
- Stress management and emotional support
- Decision-making and problem-solving

Guidelines:
1. Be kind, respectful, and understanding.
2. Listen carefully to the user's problem.
3. Ask clarifying questions when necessary.
4. Break complicated problems into smaller steps.
5. Provide practical and realistic solutions.
6. Explain the advantages and disadvantages of different options.
7. Never judge or shame the user.
8. Encourage the user to make their own decisions.
9. Do not pretend to be a doctor, therapist, or lawyer.
10. For serious emergencies or immediate danger, encourage
    the user to contact local emergency services or a trusted person.
11. Keep responses clear, organized, and easy to understand.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("🌱 About LifeHelper AI")
    st.write(
        "LifeHelper AI helps you understand problems, "
        "explore solutions, and make thoughtful decisions."
    )

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("AI-generated suggestions may not always be accurate.")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input(
    "Tell me what's bothering you..."
)

if user_input:
    # Display user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking about your problem..."):
            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions=SYSTEM_PROMPT,
                    input=st.session_state.messages,
                )

                ai_response = response.output_text

                st.markdown(ai_response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": ai_response
                    }
                )

            except Exception as e:
                st.error(
                    "Something went wrong. Please check your "
                    "API key and internet connection."
                )
