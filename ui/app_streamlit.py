from pathlib import Path
from src.builders.prompt_builder import PromptBuilder
from src.exceptions.exceptions import GraphAPIError
from src.services.facebook_service import FacebookPoster
from src.services.imagen_service import ImagenClientWrapper
from src.services.storage_service import ImageSaver
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

genai_api_key = os.getenv("GEMINI_API_KEY")
fb_access_token = os.getenv("FB_ACCESS_TOKEN")
fb_page_id = os.getenv("FB_PAGE_ID")

@st.cache_resource
def load_classes(genai_api_key:str):

    prompt_builder = PromptBuilder()
    image_gen = ImagenClientWrapper(genai_api_key)
    storage_service = ImageSaver()
    facebook_poster = FacebookPoster(fb_access_token, fb_page_id)

    return prompt_builder, image_gen, storage_service, facebook_poster

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

    prompt_builder, image_gen, storage_service, facebook_poster = load_classes(genai_api_key)

    with st.spinner("Orchestrating prompt and generating image..."):
        try:
            # make the payload
            payload = prompt_builder.orchestrate(
                query=user_prompt,
                session_negative_prompts=st.session_state.session_negative_prompts,
                few_shot_examples=st.session_state.approved_history
            )
            # generate image
            image_bytes = image_gen.generate_image_from_payload(payload)

            if not image_bytes:
                raise Exception("Missing image bytes")
            # persist image and update session state
            transient_path = storage_service.save(image_bytes)
            st.session_state.current_image_path = transient_path

            st.success("Candidate image generated!")
            st.rerun()

        except Exception as e:
            st.error(f"Generation failed: {e}")


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
   # APPROVAL PATH
    with col1:
        st.success("Approve Output")
        caption = st.text_area("Facebook Post Caption:", value=user_prompt)

        if st.button("Approve & Post to Facebook"):
            try:
                with st.spinner("Publishing photo to Facebook Page..."):
                    # 1. Publish candidate image binary using FacebookPoster
                    response = facebook_poster.publish_photo_item(
                        image_path=st.session_state.current_image_path,
                        caption=caption,
                    )

                    # 2. Append to approved prompt history (sliding window of 7)
                    st.session_state.approved_history.append(user_prompt)
                    st.session_state.approved_history = (
                        st.session_state.approved_history[-7:]
                    )

                    # 3. Clear active transient image & celebrate
                    st.session_state.current_image_path = None
                    st.balloons()
                    st.success(
                        f"Successfully posted to Facebook! (Post ID: {response.get('id')})"
                    )

            except GraphAPIError as err:
                st.error(f"Facebook Graph API Error: {err}")
            except Exception as err:
                st.error(f"Unexpected error while posting: {err}")

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