import streamlit as st
from llamaapi import LlamaAPI
from st_copy_to_clipboard import st_copy_to_clipboard

class ToneStyleChanger:
    def __init__(self):
        self.llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")

    def change_tone_style(self, text, new_tone, new_style):
        system_prompt = "You are an expert writer capable of adapting text to different tones and styles. Your task is to rewrite the given text to match the specified tone and style while preserving the core message."
        user_prompt = f"Please rewrite the following text to match a {new_tone} tone and {new_style} style:\n\n{text}\n\nEnsure that the core message remains intact while adapting the language, sentence structure, and word choice to fit the new tone and style."

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

def change_tone_style_page():
    st.title("Change Tone and Style")
    st.write("Enter your text and select the desired tone and style for the rewrite.")

    # Initialize session state
    if 'text_to_change' not in st.session_state:
        st.session_state.text_to_change = ""
    if 'rewritten_text' not in st.session_state:
        st.session_state.rewritten_text = ""

    st.session_state.text_to_change = st.text_area("Enter your text here:", value=st.session_state.text_to_change, height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        new_tone = st.selectbox("Select the desired tone:", 
                                ["Professional", "Casual", "Formal", "Friendly", "Enthusiastic", 
                                 "Serious", "Humorous", "Inspirational", "Authoritative"])
    with col2:
        new_style = st.selectbox("Select the desired style:", 
                                 ["Concise", "Descriptive", "Persuasive", "Informative", "Narrative", 
                                  "Technical", "Conversational", "Poetic", "Journalistic"])
    
    if st.button("Change Tone and Style"):
        if st.session_state.text_to_change:
            with st.spinner("Rewriting..."):
                changer = ToneStyleChanger()
                st.session_state.rewritten_text = changer.change_tone_style(st.session_state.text_to_change, new_tone, new_style)
                if st.session_state.rewritten_text:
                    st.rerun()
        else:
            st.warning("Please enter some text to rewrite.")

    if st.session_state.rewritten_text:
        st.subheader("Rewritten Text")
        st.write(st.session_state.rewritten_text)
        if st.button("Copy Rewritten Text"):
            st_copy_to_clipboard(st.session_state.rewritten_text)
            st.success("Rewritten text copied to clipboard!")

if __name__ == "__main__":
    change_tone_style_page()