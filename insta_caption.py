import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard as stc

class InstagramCaptionGenerator:
    def __init__(self, llama_api):
        self.llama = llama_api

    def generate_instagram_captions(self, keywords, tone, cta, audience, language):
        system_prompt = "You are an expert social media marketer specializing in creating engaging Instagram captions for travel agencies."
        user_prompt = f"""Generate 3 Instagram captions based on the following details:
        Keywords: {keywords}
        Tone: {tone}
        Call-to-Action: {cta}
        Target Audience: {audience}
        Language: {language}

        Each caption should be engaging, include relevant hashtags, and incorporate the specified call-to-action.
        """

        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000
        }

        try:
            response = self.llama.run(api_request_json)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

def instagram_caption_generator_page(tool):
    st.title("📸 Instagram Caption Generator for Travel Agents")
    st.markdown(
        """
        Generate engaging Instagram captions for your travel agency posts.
        Provide the following details to create your captions:
        """
    )

    # Initialize session state
    if 'insta_keywords' not in st.session_state:
        st.session_state.insta_keywords = ""
    if 'insta_captions' not in st.session_state:
        st.session_state.insta_captions = ""

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.insta_keywords = st.text_area(
            "📝 Keywords",
            value=st.session_state.insta_keywords,
            placeholder="e.g., Bali, beach vacation, luxury resort",
            help="Enter keywords related to your Instagram post"
        )
        input_insta_type = st.selectbox(
            "🎨 Caption Tone",
            ["Inspirational", "Informative", "Humorous", "Adventurous", "Luxurious", "Casual", "Customize"],
            help="Select the tone for your captions"
        )
        if input_insta_type == "Customize":
            input_insta_type = st.text_input("Custom Tone", placeholder="e.g., Eco-friendly")

    with col2:
        input_insta_cta = st.selectbox(
            "🎯 Call-to-Action (CTA)",
            ["Book Now", "Learn More", "Visit Our Website", "Contact Us", "Share Your Experience", "Customize"],
            help="Choose the primary action you want your audience to take"
        )
        if input_insta_cta == "Customize":
            input_insta_cta = st.text_input("Custom CTA", placeholder="e.g., Join Our Travel Club")

        input_insta_audience = st.text_input(
            "👥 Target Audience",
            placeholder="e.g., Young adventurers, Luxury travelers, Family vacationers",
            help="Describe your target audience for this post"
        )
        input_insta_language = st.selectbox(
            "🌐 Language",
            ["English", "Spanish", "French", "German", "Italian", "Customize"],
            help="Select the language for your captions"
        )
        if input_insta_language == "Customize":
            input_insta_language = st.text_input("Custom Language", placeholder="e.g., Portuguese")

    if st.button('**Get Instagram Captions**'):
        if not st.session_state.insta_keywords:
            st.error('** 🫣 Please provide keywords to generate Instagram captions. Keywords are required!**')
        else:
            with st.spinner("Generating Instagram captions..."):
                st.session_state.insta_captions = tool.generate_instagram_captions(
                    st.session_state.insta_keywords,
                    input_insta_type,
                    input_insta_cta,
                    input_insta_audience,
                    input_insta_language
                )
            st.rerun()

    if st.session_state.insta_captions:
        st.subheader('**👩👩🔬 Go Viral with these Instagram captions! 🎆🎇 🎇**')
        st.code(st.session_state.insta_captions)

        edited_captions = st.text_area("Edit Your Captions", value=st.session_state.insta_captions, height=300)
        
        if st.button("Copy Edited Content to Clipboard"):
            stc(edited_captions)
            st.success("Content copied to clipboard!")

        if st.button("Save Captions"):
            st.session_state.saved_insta_captions = edited_captions
            st.success("Captions saved successfully!")

    if 'saved_insta_captions' in st.session_state:
        st.header("Your Saved Instagram Captions")
        st.write(st.session_state.saved_insta_captions)
        if st.button("Copy Saved Captions"):
            stc(st.session_state.saved_insta_captions)
            st.success("Saved captions copied to clipboard!")

if __name__ == "__main__":
    # For testing purposes, you might want to create a mock LlamaAPI class
    class MockLlamaAPI:
        def run(self, api_request_json):
            class MockResponse:
                def json(self):
                    return {"choices": [{"message": {"content": "Mock Instagram caption"}}]}
            return MockResponse()

    tool = InstagramCaptionGenerator(MockLlamaAPI())
    instagram_caption_generator_page(tool)