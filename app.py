import streamlit as st
from groq import Groq

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="LifeHelper AI",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CUSTOM CSS
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #f7f9fc;
    }

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: #2d6a4f;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        color: #606c76;
        margin-bottom: 25px;
    }

    .welcome-box {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: #24553b;
    }

    .stChatMessage {
        border-radius: 12px;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. TITLE
# ==========================================

st.markdown(
    '<div class="main-title">🌱 LifeHelper AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your Personal AI Life Assistant'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="welcome-box">
    <h3>Welcome to LifeHelper AI 💚</h3>
    <p>
        Everyone faces challenges in life.
        Whether you are dealing with school, work,
        relationships, or personal problems,
        I am here to help you find clarity and
        take your next step.
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. GROQ API CONFIGURATION
# ==========================================

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)

except Exception:
    st.error(
        "Groq API key is missing. "
        "Please configure GROQ_API_KEY in Streamlit Secrets."
    )
    st.stop()

# ==========================================
# 5. AI PERSONALITY
# ==========================================

SYSTEM_PROMPT = """
You are LifeHelper AI, a supportive and thoughtful
AI assistant designed to help people solve
problems in their daily lives.

YOUR MAIN PURPOSE:
Help users understand their problems, explore
possible solutions, and take practical steps
toward improving their lives.

YOU CAN HELP WITH:

1. Personal challenges
2. School and study problems
3. Career and workplace challenges
4. Relationships and communication
5. Emotional support and stress management
6. Goal setting and personal development
7. Decision-making and planning
8. Time management and productivity

YOUR PERSONALITY:

- Warm, kind, patient, and understanding.
- Respectful and nonjudgmental.
- Encouraging without being overly positive.
- Honest about uncertainty.
- Practical and solution-oriented.

HOW TO RESPOND:

1. Understand the user's situation.
2. Acknowledge their feelings when appropriate.
3. Ask clarifying questions if necessary.
4. Identify the main problem.
5. Offer realistic and practical solutions.
6. Explain the pros and cons of different options.
7. Break difficult situations into manageable steps.
8. End with a small, achievable next step when appropriate.

IMPORTANT RULES:

- Never judge or shame the user.
- Never force the user to follow your advice.
- Respect the user's personal decisions.
- Do not pretend to be a doctor, therapist, or lawyer.
- Do not make promises about outcomes.
- If the user is in immediate danger, encourage them
  to contact local emergency services or a trusted person.
- Avoid asking for unnecessary sensitive information.
- Protect the user's privacy.
- Respond in the same language as the user.
- Keep answers clear, helpful, and easy to understand.

Your goal is to help users feel understood,
think clearly, and find their own solutions.
"""

# ==========================================
# 6. SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "started" not in st.session_state:
    st.session_state.started = False

# ==========================================
# 7. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🌱 LifeHelper AI")

    st.markdown("---")

    st.subheader("💡 What can I help you with?")

    st.markdown("""
    - 🧠 Personal problems
    - 📚 Study and school
    - 💼 Work and career
    - ❤️ Relationships
    - 🎯 Goals and planning
    - 🌈 Emotional support
    """)

    st.markdown("---")

    st.caption(
        "Your personal AI assistant for "
        "everyday challenges and personal growth."
    )

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.session_state.started = False
        st.rerun()

    st.markdown("---")

    st.caption(
        "LifeHelper AI provides general information "
        "and suggestions, not professional advice."
    )

# ==========================================
# 8. SUGGESTED QUESTIONS
# ==========================================

if not st.session_state.started:

    st.markdown("### 💬 What is on your mind today?")

    st.write(
        "Choose a topic below or type your own question."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "📚 I have a study problem",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "I have a problem with my studies. "
                "Can you help me find a solution?"
            )
            st.session_state.started = True
            st.rerun()

        if st.button(
            "❤️ I have a relationship problem",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "I have a relationship problem "
                "and need some advice."
            )
            st.session_state.started = True
            st.rerun()

        if st.button(
            "🎯 I want to achieve a goal",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "I have a personal goal and would "
                "like help creating an action plan."
            )
            st.session_state.started = True
            st.rerun()

    with col2:
        if st.button(
            "💼 I have a work problem",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "I have a problem at work "
                "and need help finding a solution."
            )
            st.session_state.started = True
            st.rerun()

        if st.button(
            "🌈 I feel stressed",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "I have been feeling stressed lately. "
                "Can you help me understand why "
                "and what I can do?"
            )
            st.session_state.started = True
            st.rerun()

        if st.button(
            "🤔 I need help making a decision",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "I need to make an important decision. "
                "Can you help me compare my options?"
            )
            st.session_state.started = True
            st.rerun()

# ==========================================
# 9. DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 10. CHAT INPUT
# ==========================================

user_input = st.chat_input(
    "Tell me what is bothering you..."
)

# Handle suggested prompts
if "pending_prompt" in st.session_state:

    user_input = st.session_state.pending_prompt

    del st.session_state.pending_prompt

# ==========================================
# 11. GENERATE AI RESPONSE
# ==========================================

if user_input:

    st.session_state.started = True

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner(
            "LifeHelper AI is thinking..."
        ):

            try:

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        *st.session_state.messages
                    ],
                    temperature=0.7,
                    max_tokens=1200
                )

                ai_response = (
                    response.choices[0].message.content
                )

                st.markdown(ai_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })

            except Exception as e:

                st.error(
                    "Sorry, something went wrong. "
                    "Please check your Groq API key, "
                    "model availability, or API usage limits."
                )

                st.caption(
                    "Please check the Streamlit Cloud logs "
                    "for more details."
                )
```
