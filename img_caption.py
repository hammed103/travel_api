import streamlit as st
import requests
from llamaapi import LlamaAPI

class PromptGenerator:
    def __init__(self, llama_api_token, hf_api_token):
        self.llama = LlamaAPI(llama_api_token)
        self.hf_api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
        self.hf_api_token = hf_api_token

    def generate_caption(self, image):
        headers = {"Authorization": f"Bearer {self.hf_api_token}"}
        try:
            response = requests.post(self.hf_api_url, headers=headers, data=image)
            response.raise_for_status()
            return response.json()[0]['generated_text']
        except requests.exceptions.RequestException as e:
            st.error(f"Error generating image caption: {str(e)}")
            return None

    def generate_instagram_caption(self, image_caption):
        prompt = f"""
        I am a travel agent that uses Instagram to promote myself and the trips that I promote. 
        I need a caption for Instagram. My image is described as: "{image_caption}"

        Please create an engaging Instagram caption based on this image description. The caption should:
        1. Be attention-grabbing and creative
        2. Highlight the appeal of the destination or travel experience
        3. Include a call-to-action (e.g., encouraging followers to book a trip or ask for more information)
        4. Incorporate 3-5 relevant hashtags

        Keep the caption concise (around 150-200 characters, excluding hashtags) to fit Instagram's style.
        """

        api_request = {
            "model": "llama-70b-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200
        }

        try:
            response = self.llama.run(api_request)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            st.error(f"An error occurred while generating Instagram caption: {str(e)}")
            return None

def prompt_generatorx():
    st.header("💡 Travel Agent Instagram Caption Generator")
    st.markdown("Upload an image to generate an Instagram-ready caption!")

    # Try to get API tokens from secrets, if not available, use input fields
    try:
        llama_api_token = st.secrets["LLAMA_API_TOKEN"]
        hf_api_token = st.secrets["HF_API_TOKEN"]
    except FileNotFoundError:
        st.warning("No secrets file found. Please enter your API tokens manually.")
        llama_api_token = st.text_input("Enter your LlamaAPI token:", type="password")
        hf_api_token = st.text_input("Enter your Hugging Face API token:", type="password")

    if not llama_api_token or not hf_api_token:
        st.error("Please provide both API tokens to proceed.")
        return

    generator = PromptGenerator(llama_api_token, hf_api_token)

    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        if st.button("Generate Caption"):
            with st.spinner("Generating caption..."):
                image_bytes = uploaded_file.getvalue()
                image_caption = generator.generate_caption(image_bytes)
                
                if image_caption:
                    st.write(f"Image Description: {image_caption}")
                    instagram_caption = generator.generate_instagram_caption(image_caption)
                    
                    if instagram_caption:
                        st.subheader("Generated Instagram Caption:")
                        st.text_area("Copy this caption for your Instagram post:", instagram_caption, height=200)

                        if st.button("Copy to Clipboard"):
                            st.write("Caption copied to clipboard!")
                            st.text("You can now paste this caption into your Instagram post.")

    st.markdown("---")
    st.subheader("How to use this tool:")
    st.markdown("""
    1. Enter your API tokens if prompted.
    2. Upload an image of the travel destination or experience you want to promote.
    3. Click on "Generate Caption" to create an Instagram-ready caption.
    4. The tool will first describe your image, then use that description to create an engaging caption.
    5. You can copy the generated caption and use it for your Instagram post.
    6. Feel free to edit the caption to add your personal touch!
    """)

if __name__ == "__main__":
    prompt_generator()