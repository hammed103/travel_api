import streamlit as st
from llamaapi import LlamaAPI

class WordAlternativeSuggester:
    def __init__(self):
        self.llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")

    def suggest_alternatives(self, word, context):
        system_prompt = "You are an expert linguist and thesaurus. Your task is to suggest alternative words or phrases that could replace the given word in the provided context."
        user_prompt = f"Please suggest alternative words or phrases for '{word}' in the following context:\n\n{context}\n\nProvide a list of alternatives with brief explanations of how they might change the tone or meaning."

        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 500
        }

        try:
            response = self.llama.run(api_request_json)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

def alternative_words_page():
    st.title("Alternative Words")
    st.write("Enter a word and its context to get suggestions for alternative words or phrases.")

    word = st.text_input("Enter the word you want alternatives for:")
    context = st.text_area("Enter the context (sentence or paragraph) where the word is used:", height=100)
    
    if st.button("Suggest Alternatives"):
        if word and context:
            with st.spinner("Generating alternatives..."):
                suggester = WordAlternativeSuggester()
                result = suggester.suggest_alternatives(word, context)
                if result:
                    st.subheader("Alternative Suggestions")
                    st.write(result)
                    edited_post = st.text_area("Edit Content", value=result, height=300)
        else:
            st.warning("Please enter both a word and its context.")

# Add this to your main.py or app.py
# if page == "Alternative Words":
#     alternative_words_page()