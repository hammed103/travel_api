import streamlit as st
import json
from llamaapi import LlamaAPI
from st_copy_to_clipboard import st_copy_to_clipboard
from datetime import date


def json_serialize(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class AdvancedPostGenerator:
    def __init__(self):
        self.llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")

    def generate_post(self, post_type, fields, language, tone, include_cta, hashtags, length, profile):
        system_prompt = self._create_system_prompt(profile)
        user_prompt = f"""
        Task: Generate a social media post for a travel agency.
        Post type: {post_type}
        Details: {json.dumps(fields)}
        Language: {language}
        Tone: {tone}
        {"Include a call-to-action." if include_cta else ""}
        Hashtags: {hashtags}
        Post length: {length} plus or minus  100 characters

        Please create a compelling and engaging post based on the above information. The post should be appropriate for the specified post type, use the given details effectively, be written in the specified language and tone, include a call-to-action if requested, incorporate the provided hashtags naturally, and adhere to the specified character length.
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

    def _create_system_prompt(self, profile):
        return f"""You are an AI assistant creating social media content for a travel agent. 
        Generate content directly without any introductory phrases or meta-commentary. 
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
        
        Incorporate this information naturally into the content where appropriate.
        """

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
    


def advanced_post_generator():
    st.header("Advanced Post Generator")
    st.markdown("Create engaging social media content for your travel agency!")

    # Get profile data
    profile = st.session_state.get('profile', {})

    post_generator = AdvancedPostGenerator()

    # Main options
    post_type = st.selectbox("Select post type", ["Destination Highlight", "Travel Tip", "Client Story", "Itinerary Sample", "Travel Inspiration"])
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("National Flair", ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Japanese", "Chinese (Simplified)"])
        tone = st.selectbox("Post Tone", ["Informative", "Inspirational", "Humorous", "Professional", "Casual & Friendly", "Luxurious & Sophisticated", "Adventurous & Exciting", "Nostalgic & Heartwarming"])
    with col2:
        post_length = st.select_slider("Post Length (characters)", options=[50, 100, 150, 200, 250, 280, 300, 350, 400, 450, 500, 800], value=300)
        hashtags = st.text_input("Hashtags (comma-separated)")

    # Common fields based on post type
    if post_type == "Destination Highlight":
        fields = {
            "Destination Name": st.text_input("Destination Name"),
            "Key Attractions": st.text_area("Key Attractions", height=100)
        }
    elif post_type == "Travel Tip":
        fields = {
            "Tip Title": st.text_input("Tip Title"),
            "Tip Details": st.text_area("Tip Details", height=100)
        }
    elif post_type == "Client Story":
        fields = {
            "Client Name": st.text_input("Client Name (or Anonymous)"),
            "Destination Visited": st.text_input("Destination Visited"),
            "Client Testimonial": st.text_area("Client Testimonial", height=100)
        }
    elif post_type == "Itinerary Sample":
        fields = {
            "Itinerary Title": st.text_input("Itinerary Title"),
            "Destination(s)": st.text_input("Destination(s)"),
            "Duration": st.text_input("Duration (e.g., 7 days)")
        }
    elif post_type == "Travel Inspiration":
        fields = {
            "Inspiration Title": st.text_input("Inspiration Title"),
            "Inspiration Description": st.text_area("Inspiration Description", height=100)
        }

    # Additional options
    with st.expander("➕ Additional Options", expanded=False):
        #if post_type == "Destination Highlight":
        fields["Best Time to Visit"] = st.selectbox("Best Time to Visit", ["Spring", "Summer", "Fall", "Winter", "Year-round"])
        fields["Unique Selling Point"] = st.text_input("Unique Selling Point")
        #elif post_type == "Travel Tip":
        fields["Tip Category"] = st.selectbox("Tip Category", ["Packing Tips", "Safety Tips", "Budget Tips", "Cultural Tips", "Transportation Tips"])
        fields["Relevant Destination(s)"] = st.text_input("Relevant Destination(s)")
        #elif post_type == "Client Story":
        fields["Travel Date"] = st.date_input("Travel Date")
        fields["Trip Type"] = st.selectbox("Trip Type", ["Family Vacation", "Honeymoon", "Adventure Trip", "Luxury Getaway", "Group Tour"])
        fields["Highlight of the Trip"] = st.text_input("Highlight of the Trip")
        #elif post_type == "Itinerary Sample":
        fields["Travel Style"] = st.selectbox("Travel Style", ["Luxury", "Budget", "Adventure", "Cultural", "Relaxation"])
        fields["Day-by-Day Highlights"] = st.text_area("Day-by-Day Highlights")
        fields["Estimated Price Range"] = st.text_input("Estimated Price Range")
        #elif post_type == "Travel Inspiration":
        fields["Theme"] = st.selectbox("Theme", ["Bucket List Destinations", "Hidden Gems", "Seasonal Specials", "Unique Local Experiences", "Foodie Adventures"])
        fields["Featured Destination(s)"] = st.text_input("Featured Destination(s)")

        include_cta = st.checkbox("Include Call-to-Action")
        if include_cta:
            cta_options = [
                "Book Now",
                "Learn More",
                "Contact Us",
                "Visit Our Website",
                "Sign Up for Our Newsletter",
                "Follow Us on Social Media",
                "Share Your Travel Story",
                "Get a Free Quote",
                "Limited Time Offer",
                "Custom CTA"
            ]
            cta_choice = st.selectbox("Choose a Call-to-Action", cta_options)
            if cta_choice == "Custom CTA":
                custom_cta = st.text_input("Enter your custom Call-to-Action")
                cta = custom_cta
            else:
                cta = cta_choice
        else:
            cta = None

    if st.button("Generate Post"):
        with st.spinner("Generating post..."):
            serializable_fields = json.loads(json.dumps(fields, default=json_serialize))
            post_content = post_generator.generate_post(post_type, serializable_fields, language, tone, cta, hashtags, post_length, profile)
        
        if post_content:
            st.session_state.generated_post = post_content
            st.rerun()

    if 'generated_post' in st.session_state:
        st.subheader("Generated Post")
        edited_post = st.text_area("Edit Your Post", value=st.session_state.generated_post, height=300, key="edited_post")
        st.write(f"Character count: {len(edited_post)}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Copy to Clipboard"):
                st_copy_to_clipboard(edited_post)
                st.success("Post copied to clipboard!")
        
        with col2:
            if st.button("Save Post"):
                st.session_state.saved_post = edited_post
                st.success("Post saved successfully!")

        feedback = st.text_area("How can I improve the post? (Anything you want to add/remove?)", 
                                placeholder="E.g., Add more details about local cuisine, make it more exciting")
        
        if st.button("Regenerate Post"):
            if feedback:
                with st.spinner("Regenerating your post..."):
                    serializable_fields = json.loads(json.dumps(fields, default=json_serialize))
                    regenerate_prompt = f"Original post type: {post_type}\nOriginal fields: {json.dumps(serializable_fields)}\nPrevious content: {edited_post}\nFeedback: {feedback}\nPlease regenerate the post incorporating the feedback."
                    regenerated_content = post_generator.generate_post(post_type, {"regenerate_prompt": regenerate_prompt}, language, tone, cta, hashtags, post_length, profile)
                    if regenerated_content:
                        st.session_state.generated_post = regenerated_content
                        st.rerun()
            else:
                st.warning("Please provide feedback for regeneration.")

    if 'saved_post' in st.session_state:
        st.header("Your Saved Post")
        st.write(st.session_state.saved_post)
        st.write(f"Character count: {len(st.session_state.saved_post)}")
        if st.button("Copy Saved Post"):
            st_copy_to_clipboard(st.session_state.saved_post)
            st.success("Saved post copied to clipboard!")




if __name__ == "__main__":
    advanced_post_generator()