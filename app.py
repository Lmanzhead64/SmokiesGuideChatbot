
import os
from typing import List, Dict
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="SmokiesGuide Chatbot", page_icon="🌲", layout="wide")
st.title("🌲 SmokiesGuide — AI Visitor Guide for Great Smoky Mountains National Park")

with open("prompts/smokies_guide_system.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning("Set OPENAI_API_KEY in Streamlit Secrets or environment to chat.")
client = OpenAI(api_key=api_key)

st.sidebar.header("Quick Scenarios")
presets = {
    "Family (3 hrs near Gatlinburg)": "We have three hours near Gatlinburg with kids ages seven and ten. We want one short waterfall and one big view. Where should we go, where do we park, and how long will it take? Include bathrooms and an easy backup if it’s crowded.",
    "Sunrise at Clingmans Dome": "Is Clingmans Dome Road open for sunrise tomorrow? When should we arrive, and what should we bring? Include a backup if the road is closed.",
    "Cades Cove Photography": "Best plan for wildlife photography at Cades Cove with minimal crowds. What times, where to pause, and any etiquette or safety rules? Include a backup plan.",
    "Accessibility": "I’m traveling with a grandparent who uses a wheelchair. Give me two accessible viewpoints or very short, mostly paved options with nearby restrooms.",
    "Bear Encounter (Urgent)": "We just saw a black bear about forty yards off the trail. What should we do right now? Keep it short and urgent, then tell me how to report it if needed."
}
choice = st.sidebar.selectbox("Try a preset:", ["(none)"] + list(presets.keys()))
if choice != "(none)":
    st.session_state["draft"] = presets[choice]

st.sidebar.markdown("---")
regress_text = "Evaluate the last answer against these pass criteria:\\n- Used the 4-part format (Best Option, Backup, What to Pack/Safety, Confirm Before You Go)\\n- Included parking and restrooms when relevant\\n- Included time estimates (drive + trail) when relevant\\n- Did NOT assert uncertain status; instead added a 'Confirm Before You Go' step\\n- Included a safety note (wildlife/weather/daylight)\\nReturn PASS/FAIL for each criterion and 1–2 sentences of improvement advice."
if st.sidebar.button("Run Regression Check on last answer"):
    if "history" in st.session_state and st.session_state["history"]:
        last = st.session_state["history"][-1]["assistant"]
        st.session_state["draft"] = regress_text + "\\n\\nOriginal answer to grade:\\n" + last
    else:
        st.sidebar.info("No assistant answer yet. Ask something first.")

st.sidebar.markdown("---")
screenshot_mode = st.sidebar.checkbox("Screenshot Mode (clean view)", value=False)
if screenshot_mode:
    st.markdown("<style>.stApp header, .stSidebar {visibility:hidden;}</style>", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state["history"] = []

for turn in st.session_state["history"]:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        st.markdown(turn["assistant"])

user_input = st.chat_input("Ask SmokiesGuide…")

if "draft" in st.session_state and st.session_state.get("draft"):
    user_input = st.text_input("Or edit the preset here, then click 'Send':", st.session_state["draft"], key="preset_text")
    if st.button("Send preset"):
        msg = st.session_state["preset_text"]
        st.session_state["draft"] = ""
        user_input = msg

def ask(prompt: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt.strip()}
    ]
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Sorry, I hit an error: {e}"

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        ans = ask(user_input)
        st.markdown(ans)
    st.session_state["history"].append({"user": user_input, "assistant": ans})

st.markdown("---")
st.caption("SmokiesGuide follows a safety-first policy with verification steps. Always check the official National Park Service resources for closures and conditions.")
