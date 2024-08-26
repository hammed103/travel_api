import streamlit as st
from llamaapi import LlamaAPI
import json
from st_copy_to_clipboard import st_copy_to_clipboard

class BlogGenerator:
    def __init__(self):
        self.llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")

    def generate_blog(self, input_type, user_input, profile, add_compliance, region):
        if input_type == "prompt":
            return self._generate_from_prompt(user_input, profile, add_compliance, region)
        elif input_type == "fields":
            return self._generate_from_fields(user_input, profile, add_compliance, region)

    def _generate_from_prompt(self, prompt, profile, add_compliance, region):
        system_prompt = self._create_system_prompt(profile, add_compliance, region)
        
        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a blog article based on this prompt: {prompt}"}
            ],
            "max_tokens": 2000
        }
        
        return self._make_api_call(api_request_json)

    def _generate_from_fields(self, fields, profile, add_compliance, region):
        system_prompt = self._create_system_prompt(profile, add_compliance, region)
        
        user_prompt = f"""Generate a {fields['content_type']} blog article for a travel agent.
        Tone: {fields['tone']}
        Focus: {fields['focus']}
        Target Audience: {fields['target_audience']}
        Language: {fields['language']}
        Length: {fields['length_range']} words
        """
        
        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 2000
        }
        
        return self._make_api_call(api_request_json)

    def _create_system_prompt(self, profile, add_compliance, region):
        spelling_preference = profile.get('spelling_preference', 'American English')
        prompt = f"""You are an AI assistant creating blog content for a travel agent. 
        Generate content directly without any introductory phrases or meta-commentary. 
        Write in the first-person perspective of the travel agent.
        Use {spelling_preference} spelling and vocabulary throughout the content.
        Use the following profile information as context and apply it where relevant:
        
        Name: {profile.get('name', 'the travel agent')}
        Experience: {profile.get('years_experience', 'Several years')} of experience
        Specialties: {', '.join(profile.get('specialties', ['Various travel experiences']))}
        Certifications: {', '.join(profile.get('certifications', ['Professional travel certifications']))}
        Languages: {', '.join(profile.get('languages', ['English']))}
        Favorite Destination: {profile.get('favorite_destination', 'Various exciting destinations')}
        Travel Style: {profile.get('travel_style', 'Adaptable to client needs')}
        Client Focus: {profile.get('client_focus', 'All types of travelers')}
        Unique Selling Point: {profile.get('unique_selling_point', 'Personalized travel experiences')}
        
        Incorporate this information naturally into the blog content where appropriate.
        """

        if add_compliance:
            if region == "UK":
                prompt += """
                Ensure Compliance: When writing content for travel-related posts in the UK, always include necessary disclaimers and comply with the Advertising Standards Authority (ASA) and Committee of Advertising Practice (CAP) guidelines. Use the following guidelines to maintain compliance:
                Pricing Statements: If you mention any prices, include phrases such as "Prices may vary," "Subject to availability," or "Additional charges may apply."
                Offers and Discounts: When discussing offers or discounts, add disclaimers like "Terms and conditions apply" or "Limited time offer."
                Reviews and Endorsements: If the content includes reviews, endorsements, or sponsored content, clearly state "Sponsored," "Ad," or "This is a paid partnership."
                Example: "Book now for just £199! Prices may vary. Terms and conditions apply."
                """
            elif region == "US":
                prompt += """
                Ensure Compliance: When writing content for travel-related posts in the US, adhere to the Federal Trade Commission (FTC) guidelines by including appropriate disclaimers. Use the following guidelines to maintain compliance:
                Pricing Statements: If prices are mentioned, add disclaimers such as "Prices are subject to change" or "Check for latest offers."
                Offers and Discounts: For offers or discounts, include phrases like "Terms and conditions apply," "Offer valid while supplies last," or "Limited time offer."
                Reviews and Endorsements: Clearly disclose sponsored content or endorsements with statements like "Sponsored," "Ad," or "This content is sponsored by [Company Name]."
                Example: "Special deal for $299! Prices are subject to change. Terms and conditions apply."
                """

        return prompt

    def _make_api_call(self, api_request_json):
        try:
            response = self.llama.run(api_request_json)
            content = response.json()['choices'][0]['message']['content']
            return self._post_process_content(content)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

    def _post_process_content(self, content):
        lines = content.split('\n')
        while lines and (not lines[0].strip() or ':' in lines[0]):
            lines.pop(0)
        return '\n'.join(lines).strip()

def ai_blog_writer():
    st.header("AI Blog Writer")
    st.markdown("Create engaging blog content to promote your travel agency!")

    # Initialize session state
    if 'blog_content' not in st.session_state:
        st.session_state.blog_content = ""
    if 'generation_method' not in st.session_state:
        st.session_state.generation_method = "prompt"

    # Get profile data
    profile = st.session_state.get('profile', {})

    blog_generator = BlogGenerator()

    # Method selection
    st.session_state.generation_method = st.radio("Choose generation method:", ("Prompt", "Fields"))

    # Compliance options
    add_compliance = st.checkbox("Add Compliance", value=True)
    region = st.selectbox("Region for Compliance", ["UK", "US"]) if add_compliance else None

    if st.session_state.generation_method == "Prompt":
        prompt_input(blog_generator, profile, add_compliance, region)
    else:
        fields_input(blog_generator, profile, add_compliance, region)

    # Display and edit generated content
    if st.session_state.blog_content:
        display_edit_content()

    # Regeneration and feedback
    if st.session_state.blog_content:
        regenerate_content(blog_generator, profile, add_compliance, region)

def prompt_input(blog_generator, profile, add_compliance, region):
    user_prompt = st.text_area(
        "Describe what you want to create",
        value=st.session_state.get('user_prompt', ''),
        placeholder="Example: Write a blog post about the top 5 hidden gems in Bali, focusing on off-the-beaten-path locations. Include tips for sustainable travel and target adventure seekers. The tone should be exciting and informative, about 500 words long.",
        height=150
    )
    st.session_state.user_prompt = user_prompt

    if st.button("Generate from Prompt"):
        if user_prompt:
            with st.spinner("Generating your blog content..."):
                generated_content = blog_generator.generate_blog("prompt", user_prompt, profile, add_compliance, region)
                if generated_content:
                    st.session_state.blog_content = generated_content
                    st.session_state.edited_content = generated_content
                    st.rerun()
        else:
            st.warning("Please provide a prompt before generating.")

def fields_input(blog_generator, profile, add_compliance, region):
    col1, col2 = st.columns(2)
    with col1:
        content_type_options = ["Destination Guide", "Travel Tips", "Itinerary", "Travel Story", "Hotel Review", "Local Cuisine", "Cultural Insights", "Adventure Activity", "Travel News", "Promotional Offer", "Custom"]
        content_type = st.selectbox("Content Type", options=content_type_options, key="content_type")
        if content_type == "Custom":
            content_type = st.text_input("Custom Content Type", key="custom_content_type")

        length_range_options = {"<100": "less than 100", "100 - 200": "between 100 and 200", "200 - 450": "between 200 and 450", "450 - 800": "between 450 and 800", "800 - 1000": "between 800 and 1000"}
        content_length_range = st.selectbox("Content Length Range", options=list(length_range_options.keys()), key="content_length_range")

        content_tone_options = ["Casual", "Professional", "Inspirational", "Informative", "Adventurous", "Luxury", "Budget-friendly", "Family-oriented", "Customize"]
        content_tone = st.selectbox("Content Tone", options=content_tone_options, key="content_tone")
        if content_tone == "Customize":
            content_tone = st.text_input("Custom Tone", key="custom_tone")

    with col2:
        target_audience = st.text_input("Target Audience", value=profile.get('client_focus', ''), key="target_audience")
        content_focus = st.text_input("Content Focus", value=profile.get('travel_style', ''), key="content_focus")
        content_language = st.selectbox("Content Language", options=["English", "Spanish", "French", "German", "Italian", "Chinese", "Japanese", "Arabic", "Russian", "Portuguese", "Customize"], key="content_language")
        if content_language == "Customize":
            content_language = st.text_input("Custom Language", key="custom_language")

    if st.button("Generate Blog Content"):
        if not profile.get('name') or not target_audience:
            st.error("🚫 Please complete your profile and provide a target audience.")
        else:
            with st.spinner("Generating your blog content..."):
                fields = {
                    "content_type": content_type,
                    "length_range": length_range_options[content_length_range],
                    "tone": content_tone,
                    "focus": content_focus,
                    "target_audience": target_audience,
                    "language": content_language
                }
                generated_content = blog_generator.generate_blog("fields", fields, profile, add_compliance, region)
                if generated_content:
                    st.session_state.blog_content = generated_content
                    st.session_state.edited_content = generated_content
                    st.rerun()

def display_edit_content():
    st.subheader("Generated Blog Content")
    edited_content = st.text_area("Edit Your Content", value=st.session_state.edited_content, height=300)
    st.session_state.edited_content = edited_content

    col1, col2 = st.columns(2)
    
    with col1:
        pass

    with col2:
        if st.button("Save Content"):
            st.session_state.saved_content = edited_content
            st.success("Content saved successfully!")

    if 'saved_content' in st.session_state:
        st.subheader("Your Saved Content")
        st.write(st.session_state.saved_content)
        if st.button("Copy Saved Content"):
            st_copy_to_clipboard(st.session_state.saved_content)
            st.success("Saved content copied to clipboard!")

def regenerate_content(blog_generator, profile, add_compliance, region):
    st.subheader("Regenerate Content")
    feedback = st.text_area("How can I improve the content? (Anything you want to add/remove?)", 
                            value=st.session_state.get('feedback', ''),
                            placeholder="E.g., Add more details about local cuisine, remove the section about hotels")
    st.session_state.feedback = feedback

    if st.button("Regenerate Content"):
        if feedback:
            with st.spinner("Regenerating your blog content..."):
                if st.session_state.generation_method == "Prompt":
                    regenerate_prompt = f"Original prompt: {st.session_state.user_prompt}\n\nPrevious content: {st.session_state.edited_content}\n\nFeedback: {feedback}\n\nPlease regenerate the blog content incorporating the feedback."
                    regenerated_content = blog_generator.generate_blog("prompt", regenerate_prompt, profile, add_compliance, region)
                else:
                    fields = {
                        "content_type": st.session_state.content_type,
                        "length_range": st.session_state.content_length_range,
                        "tone": st.session_state.content_tone,
                        "focus": st.session_state.content_focus,
                        "target_audience": st.session_state.target_audience,
                        "language": st.session_state.content_language
                    }
                    regenerate_prompt = f"Original fields: {json.dumps(fields)}\n\nPrevious content: {st.session_state.edited_content}\n\nFeedback: {feedback}\n\nPlease regenerate the blog content incorporating the feedback."
                    regenerated_content = blog_generator.generate_blog("prompt", regenerate_prompt, profile, add_compliance, region)
                
                if regenerated_content:
                    st.session_state.blog_content = regenerated_content
                    st.session_state.edited_content = regenerated_content
                    st.success("Content regenerated successfully!")
                    st.rerun()
        else:
            st.warning("Please provide feedback for regeneration.")

if __name__ == "__main__":
    ai_blog_writer()