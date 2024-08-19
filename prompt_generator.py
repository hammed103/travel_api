import streamlit as st

def prompt_generator():
    st.header("💡 Prompt Generator")
    st.markdown("Generate tailored prompts for your travel content!")

    # Input fields
    promotion_content = st.text_area("What do you want to promote?", 
                                     placeholder="E.g., A luxury beach resort in Bali")
    platform = st.selectbox("Select the platform", 
                            ["ChatGPT", "Claude", "Other AI Assistant"])

    if st.button("Generate Prompt"):
        if promotion_content:
            # Simplified prompt structure
            prompt_template = """
            As a professional travel content writer, create engaging and effective content to promote the following:
            {promotion_content}

            Generate content suitable for use on social media and other marketing channels. The content should be compelling, informative, and designed to attract potential customers. Include key selling points, unique features, and a call-to-action where appropriate.

            In your response, please provide:
            1. A main body of content (around 150-200 words)
            2. 3-5 relevant hashtags for social media use
            3. A short version (under 280 characters) for Twitter
            4. 3 eye-catching headlines we could use for email marketing

            Consider the following in your content:
            - Target audience for this promotion
            - Unique selling points of the offer
            - Emotional appeal and vivid imagery
            - Appropriate tone and style for the platform
            - Any seasonal or timely aspects to emphasize

            Craft the content in a way that's ready to use or easily adapted for various marketing purposes.
            """

            # Generate the final prompt
            final_prompt = prompt_template.format(promotion_content=promotion_content)

            st.subheader("Generated Prompt")
            st.text_area("Copy this prompt to use with your preferred AI assistant:", 
                         final_prompt, height=400)
            
            st.info("Remember to set 'do not train model with my data' in the settings of your AI assistant for privacy.")

            if st.button("Copy to Clipboard"):
                st.write("Prompt copied to clipboard!")
                st.text("You can now paste this prompt into ChatGPT, Claude, or your preferred AI assistant.")
        else:
            st.warning("Please enter what you want to promote before generating a prompt.")

if __name__ == "__main__":
    prompt_generator()