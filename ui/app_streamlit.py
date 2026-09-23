from pathlib import Path
import streamlit as st

from src.builders.prompt_builder import PromptBuilder
from src.exceptions.exceptions import GraphAPIError
from src.services.facebook_service import FacebookPoster
from src.services.imagen_service import ImagenClientWrapper

# --- 1. Page Configuration ---
st.set_page_config(page_title="AI Content Studio", layout="centered")
st.title(" Zaido Content Generator & Reviewer")

# --- 2. Session State Initialization ---
if "session_negative_prompts" not in st.session_state:
    st.session_state.session_negative_prompts = []

if "approved_history" not in st.session_state:
    st.session_state.approved_history = []  # Stores last 7 approved prompt strings

if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = None

if "credits_remaining" not in st.session_state:
    st.session_state.credits_remaining = 5  # Throttling limit per session

# --- 3. Sidebar Status & Controls ---
with st.sidebar:
    st.header("Session Status")
    st.metric("Credits Remaining", st.session_state.credits_remaining)
    st.write(
        f"**Active Session Negatives:** {len(st.session_state.session_negative_prompts)}"
    )
    st.write(
        f"**Approved Outputs (History):** {len(st.session_state.approved_history)}"
    )

    if st.button("Reset Session State"):
        st.session_state.session_negative_prompts = []
        st.session_state.current_image_path = None
        st.session_state.credits_remaining = 5
        st.rerun()

# --- 4. Main Generation Form ---
user_prompt = st.text_input(
    "Enter Content Concept:",
    placeholder="e.g., Doraemon in Tokyo futuristic street",
)

generate_btn = st.button(
    "Generate Image", disabled=(st.session_state.credits_remaining <= 0)
)

if generate_btn and user_prompt:
    st.session_state.credits_remaining -= 1

    # Call services (Orchestrate -> Generate -> Save to transient)
    # TODO: Connect initialized ImagenClientWrapper and StorageService here
    st.info("Generating candidate image...")

    # Placeholder simulation for wiring verification:
    # st.session_state.current_image_path = Path("storage/transient/latest.png")

# --- 5. Human-in-the-Loop Review Workspace ---
if st.session_state.current_image_path:
    st.divider()
    st.subheader("Review Candidate Output")

    # Display transient image
    st.image(str(st.session_state.current_image_path), use_column_width=True)

    col1, col2 = st.columns(2)

    # APPROVAL PATH
    with col1:
        st.success("Approve Output")
        caption = st.text_area("Facebook Post Caption:", value=user_prompt)
        if st.button("Approve & Post to Facebook"):
            try:
                # 1. Move image from storage/transient -> storage/approved
                # 2. Call facebook_poster.publish_photo_item(approved_path, caption=caption)
                # 3. Update approved_history memory
                st.session_state.approved_history.append(user_prompt)
                st.session_state.current_image_path = None
                st.balloons()
                st.success("Posted successfully to Facebook!")
            except Exception as e:
                st.error(f"Failed to post: {e}")

    # REJECTION PATH
    with col2:
        st.error("Reject Output")
        rating = st.slider("Quality Rating", 1, 5, 2)
        rejection_reason = st.text_input(
            "Why was this rejected?",
            placeholder="e.g., blurry background, extra limbs",
        )

        if st.button("Reject & Refine"):
            if rejection_reason:
                # Convert rejection input to session negative prompt
                st.session_state.session_negative_prompts.append(
                    rejection_reason
                )
                st.session_state.current_image_path = None
                st.warning("Feedback recorded. Retrying generation...")
                st.rerun()