import streamlit as st
from llamaapi import LlamaAPI
from st_copy_to_clipboard import st_copy_to_clipboard
class Proofreader:
    def __init__(self):
        self.llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")

    def proofread(self, text):
        system_prompt = "You are an expert proofreader and editor. Your task is to identify and correct any errors in grammar, spelling, punctuation, and style. Also, suggest improvements for clarity and conciseness."
        user_prompt = f"Please proofread and edit the following text:\n\n{text}"

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

def proofreader_page():
    st.title("Proofreader")
    st.write("Paste your text below for proofreading and editing suggestions.")

    text_to_proofread = st.text_area("Enter your text here:", height=200)
    
    if st.button("Proofread"):
        if text_to_proofread:
            with st.spinner("Proofreading..."):
                proofreader = Proofreader()
                result = proofreader.proofread(text_to_proofread)
                if result:
                    st.subheader("Proofreading Results")
                    st.write(result)
                    if st.button("Copy Edited Text"):
                        st_copy_to_clipboard(result)
        else:
            st.warning("Please enter some text to proofread.")

# Add this to your main.py or app.py
# if page == "Proofreader":
#     proofreader_page()