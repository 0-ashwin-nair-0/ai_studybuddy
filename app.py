import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PyPDF2 import PdfReader
from gtts import gTTS
import os
import base64
import re
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()
# -----------------------------
# Configure Gemini API
# -----------------------------
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(page_title="AI-Powered Study Buddy", page_icon="📚", layout="wide")

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>
    /* Import a modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    :root{
        --accent-1: #60a5fa; /* lighter blue */
        --accent-2: #a78bfa; /* soft purple */
        --bg: linear-gradient(180deg, #0b1220 0%, #071023 100%);
        --card-bg: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
        --muted: #94a3b8;
        --text: #e6eef8;
        --subtext: #aab7c9;
    }

    html, body, [class*="css"]  {
        font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }

    .stApp {
        background: var(--bg);
        padding: 28px 32px;
        color: var(--text);
    }

    .main-title {
        font-size: 44px;
        color: var(--accent-1);
        text-align: center;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
        text-shadow: 0 8px 30px rgba(9,30,66,0.25);
    }

    .subtitle {
        text-align: center;
        font-size: 15px;
        color: var(--subtext);
        margin-bottom: 28px;
    }

    /* Typing animation for subtitle */
    .typing {
        display: inline-block;
        white-space: nowrap;
        overflow: hidden;
        border-right: .12em solid rgba(255,255,255,0.6);
        box-sizing: content-box;
        max-width: 0ch; /* will be animated */
        /* slower typing: longer duration and steps */
        animation: typing 8.5s steps(80, end) forwards, blink 1s step-end infinite;
        letter-spacing: 0.2px;
        font-weight: 500;
    }

    @keyframes typing {
        from { max-width: 0ch; }
        to { max-width: 120ch; }
    }

    @keyframes blink {
        50% { border-color: transparent; }
    }

    /* Thinking animation box */
    .thinking-box { display:flex; gap:12px; align-items:center; padding:14px; border-radius:12px; background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px solid rgba(255,255,255,0.03); }
    .thinking-wave { width:60px; height:40px; }
    .thinking-content { flex:1; }
    .thinking-icon { font-size:22px; margin-right:6px; }
    .thinking-quotes { position:relative; height:44px; overflow:hidden; color:var(--subtext); }
    .thinking-quotes span { position:absolute; left:0; right:0; opacity:0; transform:translateY(6px); animation: quoteFade 9s infinite; padding-right:8px; }
    .thinking-quotes span:nth-child(1){ animation-delay: 0s; }
    .thinking-quotes span:nth-child(2){ animation-delay: 3s; }
    .thinking-quotes span:nth-child(3){ animation-delay: 6s; }
    @keyframes quoteFade {
        0% { opacity: 0; transform: translateY(8px); }
        10% { opacity: 1; transform: translateY(0); }
        33% { opacity: 1; transform: translateY(0); }
        43% { opacity: 0; transform: translateY(-8px); }
        100% { opacity: 0; }
    }

    /* Page container for content cards */
    .content-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 18px;
    }

    /* Card style used throughout */
    .ui-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 8px 30px rgba(2,6,23,0.6);
        transition: transform 0.22s cubic-bezier(.2,.9,.3,1), box-shadow 0.2s;
        border: 1px solid rgba(255,255,255,0.03);
    }
    .ui-card:hover { transform: translateY(-6px); box-shadow: 0 20px 60px rgba(2,6,23,0.7); }

    /* Buttons */
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(90deg,var(--accent-1),var(--accent-2));
        color: #051029;
        border-radius: 10px;
        padding: 8px 18px;
        border: none;
        font-weight: 700;
        box-shadow: 0 10px 30px rgba(8,18,36,0.6);
    }
    .stButton>button:active { transform: translateY(1px); }

    /* Sidebar enhancements */
    .css-1d391kg { /* Streamlit sidebar container class may vary; these are safe, minimal overrides */
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius: 12px;
        padding: 14px !important;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.03);
        color: var(--subtext);
    }

    /* Flashcards */
    .flash-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); gap: 16px; }
    .flashcard {
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
        border-radius: 12px;
        padding: 16px;
        color: var(--text);
        position: relative;
        overflow: hidden;
        transition: transform 0.28s ease, box-shadow 0.28s ease;
        box-shadow: 0 8px 30px rgba(2,6,23,0.6);
        border: 1px solid rgba(255,255,255,0.03);
    }
    .flashcard:before {
        content: "";
        position: absolute;
        left: -40px; top: -40px; width: 140px; height: 140px;
        background: radial-gradient(circle at 30% 30%, rgba(37,99,235,0.12), transparent 30%), radial-gradient(circle at 70% 70%, rgba(124,58,237,0.08), transparent 30%);
        transform: rotate(20deg);
        opacity: 0.9;
    }
    .flashcard:hover { transform: translateY(-8px); box-shadow: 0 22px 50px rgba(2,6,23,0.12); }
    .flashcard .q { font-weight:700; color: var(--accent-1); margin-bottom: 10px; font-size:15px; }
    .flashcard .a { background: linear-gradient(90deg, rgba(255,230,150,0.07), rgba(255,230,150,0.03)); color: var(--text); padding: 10px; border-radius: 8px; border-left: 4px solid rgba(167,139,250,0.25); font-size:14px; }

    /* Small helpers */
    .muted { color: var(--muted); }
    hr.custom-hr { border: none; height: 2px; background: linear-gradient(90deg,var(--accent-1),var(--accent-2)); margin: 18px 0; border-radius: 2px; }

    /* Sidebar card and radio tweaks */
    .sidebar-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.03);
    }
    .sidebar-title { font-weight:800; color: var(--accent-1); font-size:18px; }
    .sidebar-sub { color: var(--subtext); font-size:13px; margin-top:4px; }

    /* Make radio groups more readable in sidebar */
    [data-testid="stSidebar"] .stRadio, [data-testid="stSidebar"] .stRadio > div {
        color: var(--text) !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: var(--text) !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] .stRadio .css-1l02zno, [data-testid="stSidebar"] .stRadio .css-1kyxreq {
        gap: 6px;
    }

    /* Radio option card styling (sidebar) - more airy and readable */
    [data-testid="stSidebar"] .stRadio label {
        display: block;
        padding: 12px 14px;
        margin-bottom: 12px;
        border-radius: 12px;
        background: linear-gradient(180deg, rgba(255,255,255,0.005), rgba(255,255,255,0.002));
        border: 1px solid rgba(255,255,255,0.02);
        transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
        cursor: pointer;
        line-height: 1.1;
        font-size: 15px;
    }
    [data-testid="stSidebar"] .stRadio label:hover { transform: translateY(-3px); box-shadow: 0 6px 22px rgba(2,6,23,0.35); }
    /* Highlight selected option (uses :has where available) */
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(90deg,var(--accent-1),var(--accent-2));
        color: #051029 !important;
        font-weight: 700;
        box-shadow: 0 10px 30px rgba(8,18,36,0.5);
    }
    [data-testid="stSidebar"] .stRadio label .stMarkdown {
        display: block;
    }
    /* Reduce radio group container density */
    [data-testid="stSidebar"] .stRadio > div { gap: 10px; }

    /* Responsive tweaks */
    @media (max-width: 700px) {
        .main-title { font-size: 30px; }
        .subtitle { font-size: 14px; }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("<h1 class='main-title'>🤖 AI-Powered Study Buddy</h1>", unsafe_allow_html=True)
components.html("""
<div class='subtitle' style='text-align:center;'>
    <span id='hero' aria-live='polite'></span>
</div>
<style>
    /* Ensure iframe content matches app theme: transparent background and light text */
    html, body { background: transparent !important; color: #e6eef8 !important; font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
    #hero { color: #e6eef8; font-weight:500; opacity: 0; transition: opacity 900ms ease-in-out, transform 900ms ease-in-out; transform: translateY(4px); display:inline-block; }
    /* caret removed for calmer visuals */
    #hero::after{ content: ''; display:none !important; }
</style>
<script>
(() => {
    const el = document.getElementById('hero');
    if (!el) return;
    const phrases = [
        "Want to learn more in less time? Use 'Summarize Notes' to condense long readings.",
        "Stuck on a tough idea? Use 'Explain Concept' for clear examples and step-by-step explanations.",
        "Make revision fast — 'Create Flashcards' turns topics into ready-to-use Q&A.",
        "Have a PDF? 'Upload PDF & Summarize' extracts the key points quickly.",
        "Test yourself with 'Interactive Quiz Mode' — auto-generate MCQs and check your score.",
    ];

    // Timings (slower, smoother)
    const fadeIn = 700; // ms
    const hold = 4500 + Math.floor(Math.random()*1500); // 4.5-6s (shorter)
    const fadeOut = 600; // ms
    const between = 220; // ms small gap (shorter)

    let idx = 0;

    function show(text){
        el.textContent = text;
        el.style.opacity = '0';
        el.style.transform = 'translateY(4px)';
        // force reflow then transition in
        void el.offsetWidth;
        el.style.transition = `opacity ${fadeIn}ms ease-in-out, transform ${fadeIn}ms ease-in-out`;
        el.style.opacity = '1';
        el.style.transform = 'translateY(0px)';
    }

    function hide(){
        el.style.transition = `opacity ${fadeOut}ms ease-in-out, transform ${fadeOut}ms ease-in-out`;
        el.style.opacity = '0';
        el.style.transform = 'translateY(4px)';
    }

    async function cycle(){
        while(true){
            show(phrases[idx]);
            await new Promise(r => setTimeout(r, fadeIn + hold));
            hide();
            await new Promise(r => setTimeout(r, fadeOut + between));
            idx = (idx + 1) % phrases.length;
        }
    }

    // Start after a short delay so initial page layout stabilizes
    setTimeout(() => { cycle().catch(e=>console.error(e)); }, 200);
})();
</script>
""", height=90, scrolling=False)

# -----------------------------
# Sidebar Options (styled)
# -----------------------------
st.sidebar.markdown("""
<div class="sidebar-card">
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="font-size:20px; background:linear-gradient(90deg,var(--accent-1),var(--accent-2)); -webkit-background-clip:text; color:transparent; font-weight:900;">📘</div>
        <div>
            <div class="sidebar-title">Features</div>
            <div class="sidebar-sub">Pick a tool to get started</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

options = [
    "Explain Concept",
    "Summarize Notes",
    "Create Flashcards",
    "Upload PDF & Summarize",
    "Interactive Quiz Mode",
]

# prettier labels shown in the sidebar (keeps original values for logic)
pretty_labels = {
    "Explain Concept": "💡 Explain Concept",
    "Summarize Notes": "📝 Summarize Notes",
    "Create Flashcards": "🎴 Create Flashcards",
    "Upload PDF & Summarize": "📂 Upload PDF & Summarize",
    "Interactive Quiz Mode": "🧠 Interactive Quiz Mode",
}

def _format_option(opt):
    # Streamlit's radio supports format_func to display custom labels for values
    return pretty_labels.get(opt, opt)

task = st.sidebar.radio("Select an option:", options, format_func=_format_option)

# Single dynamic description under options to avoid clutter
description_map = {
    "Explain Concept": "Get a clear, example-driven explanation of any topic.",
    "Summarize Notes": "Paste long notes and get concise bullet summaries.",
    "Create Flashcards": "Generate ready-to-use Q/A flashcards for study.",
    "Upload PDF & Summarize": "Upload PDFs and extract short academic summaries.",
    "Interactive Quiz Mode": "Auto-generate quizzes to test and track your knowledge.",
}

st.sidebar.markdown("<div style='margin-top:10px; padding:10px 6px; border-radius:8px; color:var(--subtext)'>" +
                    f"<small>{description_map.get(task,'')}</small></div>", unsafe_allow_html=True)

# -----------------------------
# Helper Functions
# -----------------------------
def clean_text_for_tts(raw_text):
    text = re.sub(r"```.*?```", "", raw_text, flags=re.DOTALL)
    text = re.sub(r"[*_#`~>\-•+]", "", text)
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    if text and text[-1] not in ".!?":
        text += "."
    return text.strip()

def text_to_audio(text):
    cleaned = clean_text_for_tts(text)
    # Create a temporary file without delete=True
    tmp_path = os.path.join(tempfile.gettempdir(), "temp_audio.mp3")
    tts = gTTS(cleaned)
    tts.save(tmp_path)
    
    # Read and encode audio for Streamlit
    with open(tmp_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio controls src="data:audio/mp3;base64,{b64}"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)


def thinking_html():
        # Small animated thinking/wave + rotating educational quotes
        return """
        <div class="thinking-box ui-card">
            <div class="thinking-wave">
                <svg width="60" height="40" viewBox="0 0 60 40" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 30 C10 10, 25 10, 35 30 C45 50, 60 30, 60 30" fill="none" stroke="rgba(167,139,250,0.4)" stroke-width="3">
                        <animate attributeName="d" dur="3s" repeatCount="indefinite" values="M0 30 C10 10, 25 10, 35 30 C45 50, 60 30, 60 30; M0 28 C12 8, 24 12, 36 28 C48 44, 60 22, 60 22; M0 30 C10 10, 25 10, 35 30 C45 50, 60 30, 60 30"/>
                    </path>
                </svg>
            </div>
            <div class="thinking-content">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;"><div class="thinking-icon">🤖</div><div style="font-weight:700;">Thinking...</div></div>
                <div class="thinking-quotes">
                    <span>“Education is the passport to the future.” — Malcolm X</span>
                    <span>“The beautiful thing about learning is nobody can take it away from you.” — B. B. King</span>
                    <span>“Tell me and I forget. Teach me and I remember. Involve me and I learn.” — Benjamin Franklin</span>
                </div>
            </div>
        </div>
        """

# Safe wrapper for generative calls to handle network or API failures gracefully
def safe_generate(prompt, placeholder=None):
    try:
        resp = model.generate_content(prompt)
        # model.generate_content may return an object with .text
        return resp.text if hasattr(resp, 'text') else (resp or '')
    except Exception as e:
        # clear any transient UI and show a friendly error
        if placeholder is not None:
            try:
                placeholder.empty()
            except Exception:
                pass
        st.error("⚠️ Unable to reach the AI service — please check your internet connection.\n" + str(e))
        return None

# -----------------------------
# Feature 1: Explain Concept
# -----------------------------
if task == "Explain Concept":
    topic = st.text_input("Enter a topic to understand better:")
    if st.button("Explain"):
        if topic:
            with st.spinner("🤔 Thinking..."):
                placeholder = st.empty()
                placeholder.markdown(thinking_html(), unsafe_allow_html=True)
                prompt = f"Explain '{topic}' in simple and clear language with real-life examples suitable for college students."
                response_text = safe_generate(prompt, placeholder)
                placeholder.empty()
                if response_text is None:
                    # already reported error by safe_generate
                    st.stop()
                st.success("✅ Explanation:")
                st.write(response_text)
                st.markdown("🎧 **Listen to this explanation:**")
                try:
                    text_to_audio(response_text)
                except Exception as e:
                    st.error("⚠️ Failed to generate audio: " + str(e))
        else:
            st.warning("Please enter a topic.")

# -----------------------------
# Feature 2: Summarize Notes
# -----------------------------
elif task == "Summarize Notes":
    notes = st.text_area("Paste your study notes:")
    if st.button("Summarize"):
        if notes:
            with st.spinner("🧠 Summarizing..."):
                placeholder = st.empty()
                placeholder.markdown(thinking_html(), unsafe_allow_html=True)
                prompt = f"Summarize these notes in clear and concise bullet points:\n{notes}"
                response_text = safe_generate(prompt, placeholder)
                placeholder.empty()
                if response_text is None:
                    st.stop()
                st.success("✅ Summary:")
                st.write(response_text)
                st.markdown("🎧 **Listen to the summary:**")
                try:
                    text_to_audio(response_text)
                except Exception as e:
                    st.error("⚠️ Failed to generate audio: " + str(e))
        else:
            st.warning("Please enter notes.")

# -----------------------------
# Feature 3: Flashcards (Clean & Attractive)
# -----------------------------
elif task == "Create Flashcards":
    topic = st.text_input("Enter topic for flashcards:")
    num_cards = st.slider("Select number of flashcards:", 3, 10, 5)
    if st.button("Create Flashcards"):
        if topic:
            with st.spinner("🎴 Creating flashcards..."):
                placeholder = st.empty()
                placeholder.markdown(thinking_html(), unsafe_allow_html=True)
                prompt = f"Create {num_cards} flashcards with 'Question' and 'Answer' on '{topic}'. Use 'Q:' for question and 'A:' for answer, one flashcard per block."
                response_text = safe_generate(prompt, placeholder)
                placeholder.empty()
                if response_text is None:
                    st.stop()
                response = response_text

                # Split by Q: pattern, remove empty and header blocks
                flashcards = [fc.strip() for fc in re.split(r"\n?Q\d*[:.]\s*", response) if fc.strip()]
                # Use a grid container for flashcards for nicer layout
                st.markdown('<div class="flash-grid">', unsafe_allow_html=True)
                for card in flashcards:
                    # Extract answer
                    parts = re.split(r"A[:.]\s*", card)
                    if len(parts) < 2:
                        continue  # Skip blocks without proper answer
                    question_text = parts[0].strip()
                    answer_text = parts[1].strip()

                    # Render flashcard using CSS classes defined above
                    st.markdown(f"""
                        <div class="flashcard ui-card">
                            <div class="q">❓ {question_text}</div>
                            <div class="a"><b>💡 Answer:</b> {answer_text}</div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Enter a topic.")


# -----------------------------
# Feature 4: Upload PDF & Summarize
# -----------------------------
elif task == "Upload PDF & Summarize":
    uploaded_pdf = st.file_uploader("📂 Upload your study PDF", type="pdf")
    if uploaded_pdf:
        with st.spinner("📖 Reading your PDF..."):
            try:
                reader = PdfReader(uploaded_pdf)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception as e:
                st.error("⚠️ Failed to read PDF: " + str(e))
                text = None
        if st.button("Summarize PDF"):
            with st.spinner("⚙️ Summarizing PDF content..."):
                if not text:
                    st.warning("No valid text extracted from the PDF to summarize.")
                else:
                    placeholder = st.empty()
                    placeholder.markdown(thinking_html(), unsafe_allow_html=True)
                    prompt = f"Summarize the following academic text in short key points:\n\n{text[:6000]}"
                    response_text = safe_generate(prompt, placeholder)
                    placeholder.empty()
                    if response_text is None:
                        st.stop()
                    st.success("✅ Summary:")
                    st.write(response_text)
                    st.markdown("🎧 **Listen to the summary:**")
                    try:
                        text_to_audio(response_text)
                    except Exception as e:
                        st.error("⚠️ Failed to generate audio: " + str(e))

# -----------------------------
# Feature 5: Interactive Quiz Mode
# -----------------------------
elif task == "Interactive Quiz Mode":
    st.title("📝 Interactive AI Quiz")
    
    # 1️⃣ Ask for user name
    user_name = st.text_input("Enter your name:")
    
    topic = st.text_input("Enter a topic for your quiz:")
    num_q = st.slider("Number of questions:", 3, 10, 5)
    difficulty = st.selectbox("Select difficulty:", ["Easy", "Medium", "Hard"])
    marks_per_q = st.number_input("Marks per question:", min_value=1, max_value=10, value=1)

    # Stop if user has not entered their name
    if not user_name:
        st.warning("Please enter your name to start the quiz.")
        st.stop()

    # Generate Quiz
    if st.button("Generate Quiz"):
        if topic:
            with st.spinner("🎯 Generating quiz..."):
                placeholder = st.empty()
                placeholder.markdown(thinking_html(), unsafe_allow_html=True)
                prompt = f"""
                Create {num_q} multiple-choice questions on '{topic}'.
                Each question should have 4 options labeled A/B/C/D.
                Difficulty: {difficulty}.
                Only provide questions and options, do NOT include answers.
                Format:
                Q1: Question text
                A) Option1
                B) Option2
                C) Option3
                D) Option4
                dont paste the option number or letter 2 times, also for the questions with code snippet the code should also be shown in the question. 
                """
                quiz_text = safe_generate(prompt, placeholder)
                placeholder.empty()
                if quiz_text is None:
                    st.stop()

                # Parse questions properly
                quiz_questions = []
                for block in quiz_text.split("\n\n"):
                    raw_lines = [line.rstrip() for line in block.splitlines()]
                    # remove empty lines but keep indentation for code blocks
                    lines = [line for line in raw_lines if line.strip() != ""]
                    if len(lines) < 2:
                        continue
                    # find where options start (first line that looks like A) ...)
                    opt_start = None
                    for idx, ln in enumerate(lines):
                        if re.match(r'^[A-D]\)', ln.strip()):
                            opt_start = idx
                            break
                    if opt_start is None:
                        continue
                    question_lines = lines[:opt_start]
                    options = [ln.strip() for ln in lines[opt_start:] if re.match(r'^[A-D]\)', ln.strip())]
                    question_text = "\n".join(question_lines).strip()
                    if options:
                        quiz_questions.append({"question": question_text, "options": options})

                st.session_state.quiz_questions = quiz_questions
                st.session_state.user_answers = {}
                st.session_state.generated_quiz_text = quiz_text
                st.session_state.quiz_generated = True
                st.success(f"✅ Quiz Generated, {user_name}!")

    # Display Quiz
    if st.session_state.get("quiz_generated", False):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 📝 Quiz Questions:")

        for i, q in enumerate(st.session_state.quiz_questions):
            key = f"q{i}"
            # Add placeholder so nothing is pre-selected
            options_with_placeholder = ["--Select an answer--"] + q["options"]
            st.session_state.user_answers[key] = st.selectbox(
                q["question"], options_with_placeholder, index=0, key=key
            )

        # Submit answers
        if st.button("Submit Answers"):
            with st.spinner("📊 Checking your answers..."):
                placeholder = st.empty()
                placeholder.markdown(thinking_html(), unsafe_allow_html=True)
                # Generate correct answers
                ans_prompt = f"""
                Provide correct answers for the following questions in format Q1:A, Q2:B:
                {st.session_state.generated_quiz_text}
                """
                correct_response = safe_generate(ans_prompt, placeholder)
                placeholder.empty()
                if correct_response is None:
                    st.stop()

                correct_dict = {}
                # Robust parsing: accept formats like 'Q1: A', '1:A', 'Q1 - A', 'Q1.A', or 'Q1:A) Option'
                if correct_response:
                    for m in re.finditer(r'(?:Q\s*(\d+)|\b(\d+)\b)\s*[:\.\-]?\s*([A-D])', correct_response, flags=re.IGNORECASE):
                        num = m.group(1) or m.group(2)
                        letter = m.group(3).upper()
                        correct_dict[f"Q{int(num)}"] = letter
                    if not correct_dict:
                        for line in correct_response.splitlines():
                            if ":" in line:
                                parts = line.split(":", 1)
                                qn = parts[0].strip()
                                ans = parts[1].strip().upper()
                                m2 = re.search(r'([A-D])', ans)
                                if m2:
                                    correct_dict[qn] = m2.group(1)

                st.session_state.correct_answers = correct_dict

                # Grade and provide feedback per question
                score = 0
                total_marks = marks_per_q * len(st.session_state.quiz_questions)
                st.markdown("### ✅ Results:")
                for i, q in enumerate(st.session_state.quiz_questions):
                    q_key = f"Q{i+1}"
                    user_sel = st.session_state.user_answers.get(f"q{i}", "--Select an answer--")
                    correct_letter = correct_dict.get(q_key)

                    # Map letter to option text
                    option_map = {}
                    for opt in q['options']:
                        m = re.match(r'^([A-D])\)\s*(.*)$', opt)
                        if m:
                            option_map[m.group(1)] = m.group(2)

                    user_letter = None
                    if user_sel and user_sel != "--Select an answer--":
                        msel = re.match(r'^([A-D])', user_sel)
                        if msel:
                            user_letter = msel.group(1)

                    is_correct = (user_letter is not None and correct_letter is not None and user_letter == correct_letter)
                    if is_correct:
                        score += marks_per_q
                        st.markdown(f"**{q_key}** — {q['question']}  \n\n ✅ Your answer: **{user_letter}) {option_map.get(user_letter, '')}** — Correct")
                    else:
                        user_disp = (f"{user_letter}) {option_map.get(user_letter,'')}" if user_letter else "No answer selected")
                        correct_disp = (f"{correct_letter}) {option_map.get(correct_letter,'(text not available)')}") if correct_letter else "(not available)"
                        st.markdown(f"**{q_key}** — {q['question']}  \n\n ❌ Your answer: **{user_disp}**  \n\n ✅ Correct answer: **{correct_disp}**")

                # 2️⃣ Personalized results
                st.success(f"🎉 {user_name}, your score: {score}/{total_marks}")

                # Motivational feedback
                percentage = (score / total_marks) * 100
                if percentage >= 80:
                    st.info(f"Excellent work, {user_name}! 🌟 You have a strong grasp of {topic}. Keep it up!")
                elif percentage >= 50:
                    st.info(f"Good job, {user_name}. 👍 You have some understanding of {topic}, but consider revising the weaker areas.")
                else:
                    st.info(f"{user_name}, it seems you need to strengthen your knowledge in {topic}. 📚 Try reviewing the main concepts and practice more questions.")
                    
                    # 3️⃣ Optional: AI-generated study suggestion
                    with st.spinner("🤖 Generating study suggestion..."):
                        suggestion_prompt = f"Suggest a simple sentence telling a student to study key points about '{topic}' because they are struggling."
                        suggestion_text = safe_generate(suggestion_prompt)
                        if suggestion_text:
                            st.markdown(f"💡 Study Tip: {suggestion_text}")



