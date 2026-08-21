import streamlit as st
import random

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Dream Guesser | Sleep Score Game",
    page_icon="🌙",
    layout="centered"
)

# --- CUSTOM VIBEY CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .stat-pill {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        padding: 6px 14px;
        border-radius: 999px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c084fc 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- GAME LOGIC INITIALIZATION ---
MAX_ATTEMPTS = 5

def init_game(secret_score=None):
    st.session_state.target_score = secret_score if secret_score else random.randint(45, 98)
    st.session_state.attempts_left = MAX_ATTEMPTS
    st.session_state.guesses = []
    st.session_state.game_over = False
    st.session_state.won = False

if "target_score" not in st.session_state:
    init_game()

# --- SIDEBAR: SETTINGS / DEV MODE ---
with st.sidebar:
    st.header("⚙️ Secret Settings")
    st.caption("Customize the target score or let the app randomize it.")
    custom_score = st.number_input(
        "Override Real Sleep Score (1–100)",
        min_value=1,
        max_value=100,
        value=st.session_state.target_score,
        step=1
    )
    if st.button("Apply & Reset Game", use_container_width=True):
        init_game(secret_score=custom_score)
        st.rerun()

# --- HEADER SECTION ---
st.markdown("""
<div class="glass-card">
    <span class="stat-pill">✨ DAILY REST VIBE CHECK</span>
    <h1 style="margin: 8px 0; color: #f8fafc;">Guess My Sleep Score</h1>
    <p style="color: #94a3b8; margin: 0; font-size: 0.95rem;">
        Tracked between <b>1</b> (zombie) and <b>100</b> (optimal restorative slumber).
    </p>
</div>
""", unsafe_allow_html=True)

# --- STATS BAR ---
col1, col2 = st.columns(2)
with col1:
    hearts = "🟣 " * st.session_state.attempts_left + "⚪ " * (MAX_ATTEMPTS - st.session_state.attempts_left)
    st.metric(label="Attempts Remaining", value=f"{st.session_state.attempts_left} / {MAX_ATTEMPTS}")
    st.caption(f"Status: {hearts}")

with col2:
    last_guess = st.session_state.guesses[-1]["guess"] if st.session_state.guesses else "—"
    st.metric(label="Last Guess", value=last_guess)

# --- INPUT & SUBMISSION ---
if not st.session_state.game_over:
    with st.form(key="guess_form", clear_on_submit=True):
        user_guess = st.slider("Select your guess:", min_value=1, max_value=100, value=75)
        submitted = st.form_submit_button("Submit Guess 🚀", use_container_width=True)

        if submitted:
            st.session_state.attempts_left -= 1
            diff = abs(user_guess - st.session_state.target_score)
            
            if user_guess == st.session_state.target_score:
                st.session_state.won = True
                st.session_state.game_over = True
                feedback = "🎯 Spot on! That was my exact score."
                vibe = "perfect"
            elif user_guess < st.session_state.target_score:
                hint = "Much higher!" if diff > 15 else "A bit higher!"
                feedback = f"📈 Too low! {hint}"
                vibe = "low"
            else:
                hint = "Much lower!" if diff > 15 else "A bit lower!"
                feedback = f"📉 Too high! {hint}"
                vibe = "high"

            st.session_state.guesses.append({
                "guess": user_guess,
                "feedback": feedback,
                "diff": diff,
                "vibe": vibe
            })

            if st.session_state.attempts_left == 0 and not st.session_state.won:
                st.session_state.game_over = True

            st.rerun()

# --- GAME OUTCOME BANNER ---
if st.session_state.game_over:
    if st.session_state.won:
        st.balloons()
        st.success(f"🎉 **You nailed it!** My actual sleep score was **{st.session_state.target_score}**.")
    else:
        st.error(f"💀 **Game Over!** You ran out of energy. The true sleep score was **{st.session_state.target_score}**.")

    if st.button("🔄 Play Again", use_container_width=True, type="primary"):
        init_game()
        st.rerun()

# --- GUESS HISTORY FEED ---
if st.session_state.guesses:
    st.write("---")
    st.subheader("📜 Guess History")
    for idx, item in enumerate(reversed(st.session_state.guesses), 1):
        proximity = "🔥 Boiling Hot" if item["diff"] <= 3 else "🌡️ Warm" if item["diff"] <= 10 else "🧊 Cold"
        st.markdown(
            f"**Attempt {MAX_ATTEMPTS - len(st.session_state.guesses) + idx}:** "
            f"Guessed **{item['guess']}** → {item['feedback']} `({proximity})`"
        )
