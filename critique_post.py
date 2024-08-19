import streamlit as st
from llamaapi import LlamaAPI

class PostCritic:
    def __init__(self):
        self.llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")

    def critique_post(self, post, platform):
        system_prompt = f"You are an expert social media consultant specializing in {platform}. Your task is to provide a constructive critique of the given post, highlighting strengths and suggesting improvements."
        user_prompt = f"Please critique the following {platform} post:\n\n{post}\n\nProvide feedback on engagement potential, clarity, tone, and any platform-specific optimizations."

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

def critique_post_page():
    st.title("Critique My Post")
    st.write("Paste your social media post below for a constructive critique.")

    platform = st.selectbox("Select the platform:", ["Facebook", "Instagram", "Twitter", "LinkedIn"])
    post_to_critique = st.text_area("Enter your post here:", height=150)
    
    if st.button("Critique Post"):
        if post_to_critique:
            with st.spinner("Analyzing your post..."):
                critic = PostCritic()
                result = critic.critique_post(post_to_critique, platform)
                if result:
                    st.subheader("Post Critique")
                    st.write(result)
                    edited_post = st.text_area("Edit Content", value=result, height=300)
                    #
        else:
            st.warning("Please enter a post to critique.")

# Add this to your main.py or app.py
# if page == "Critique My Post":
#     critique_post_page()