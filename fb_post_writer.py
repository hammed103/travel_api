import streamlit as st
from llamaapi import LlamaAPI
import random
from st_copy_to_clipboard import st_copy_to_clipboard
class FacebookPostGenerator:
    def __init__(self):
        self.llama = LlamaAPI("LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW")

    def generate_fb_post(self, post_info, profile, previous_content=None):
        system_prompt = self._create_system_prompt(profile)
        user_prompt = self._create_user_prompt(post_info, previous_content)

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
            content = response.json()['choices'][0]['message']['content']
            return self._post_process_content(content)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

    def _create_system_prompt(self, profile):
        return f"""You are an AI assistant creating a Facebook post for a travel agent. 
        Write in a concise, engaging style suitable for social media. 
        Use the following profile information as context and apply it where relevant:

        Name: {profile.get('name', 'the travel agent')}
        Experience: {profile.get('years_experience', 'Several years')} of experience
        Specialties: {', '.join(profile.get('specialties', ['Various travel experiences']))}
        Travel Style: {profile.get('travel_style', 'Adaptable to client needs')}
        Client Focus: {profile.get('client_focus', 'All types of travelers')}
        Unique Selling Point: {profile.get('unique_selling_point', 'Personalized travel experiences')}

        Incorporate this information naturally into the post where appropriate.
        """

    def _create_user_prompt(self, post_info, previous_content=None):
        prompt = f"""Create a Facebook post for a travel agent with the following details:
        Post Goal: {post_info['post_goal']}
        Target Audience: {post_info['target_audience']}
        Tone: {post_info['tone']}
        Elements to Include: {post_info['include']}
        Elements to Avoid: {post_info['avoid']}

        The post should be engaging, concise, and tailored to Facebook's format. 
        Include a call-to-action appropriate for the post goal.
        """

        if previous_content and 'feedback' in post_info:
            prompt += f"""
            
            Previous post:
            {previous_content}

            Please revise the post based on this feedback:
            {post_info['feedback']}

            Incorporate the feedback while maintaining the overall goal and tone of the post.
            """

        return prompt

    def _post_process_content(self, content):
        lines = content.split('\n')
        while lines and (not lines[0].strip() or ':' in lines[0]):
            lines.pop(0)
        return '\n'.join(lines).strip()

def collect_post_info(profile):
    post_info = {}

    col1, col2 = st.columns(2)
    with col1:
        post_goal_options = ["Promote a travel package", "Share travel tips", "Increase engagement", "Showcase a destination", "Announce a special offer", "Customize"]
        post_info["post_goal"] = st.selectbox(
            "🎯 What is the goal of your post?",
            post_goal_options,
            index=2,
            help="Select the main goal of your post."
        )
        if post_info["post_goal"] == "Customize":
            post_info["post_goal"] = st.text_input(
                "🎯 Customize your goal:",
                placeholder="e.g., Announce a travel event",
                help="Provide a specific goal for your post."
            )
        
        post_info["target_audience"] = st.text_input(
            "👥 Describe your target audience:",
            value=profile.get('client_focus', ''),
            placeholder="e.g., Adventure seekers, Luxury travelers",
            help="Describe the audience you are targeting with this post."
        )
        
        post_info["include"] = st.text_area(
            "📷 What elements do you want to include?",
            placeholder="e.g., Travel package details, Destination highlights, Client testimonial",
            help="Specify any elements you want to include in the post."
        )

    with col2:
        post_tone_options = ["Informative", "Exciting", "Inspirational", "Luxurious", "Adventurous", "Customize"]
        post_info["tone"] = st.selectbox(
            "🎨 What tone do you want to use?",
            post_tone_options,
            index=2,
            help="Choose the tone you want to use for the post."
        )
        if post_info["tone"] == "Customize":
            post_info["tone"] = st.text_input(
                "🎨 Customize your tone:",
                placeholder="e.g., Family-friendly",
                help="Provide a specific tone for your post."
            )
        
        post_info["avoid"] = st.text_area(
            "❌ What elements do you want to avoid?",
            placeholder="e.g., Overly promotional language, Complex itineraries",
            help="Specify any elements you want to avoid in the post."
        )

    return post_info

def fb_post_writer():
    st.title("📱 Facebook Post Writer for Travel Agents")
    st.markdown(
        """
        Create compelling Facebook posts to engage your audience and promote your travel agency.
        Fill in the details below to generate your post.
        """
    )

    # Get profile data
    profile = st.session_state.get('profile', {})

    post_generator = FacebookPostGenerator()

    # Collect post information
    post_info = collect_post_info(profile)

    # Generate post button
    if st.button("🚀 Generate Facebook Post"):
        if not profile.get('name') or not post_info["target_audience"]:
            st.error("🚫 Please complete your profile and provide a target audience.")
        else:
            with st.spinner("Generating your Facebook post..."):
                generated_post = post_generator.generate_fb_post(post_info, profile)
            
            if generated_post:
                st.session_state.current_post = generated_post
                st.session_state.post_info = post_info
                st.rerun()

    # Display generated post and handle regeneration
    if 'current_post' in st.session_state:
        st.subheader("Generated Facebook Post")
        st.markdown(f"```{st.session_state.current_post}```")
        
        edited_post = st.text_area("Edit Your Post", value=st.session_state.current_post, height=300)
        
        if st.button("Copy to Clipboard"):
            st_copy_to_clipboard(st.session_state.current_post)

        feedback = st.text_area("How did I do? (Anything you want to add/remove?)", placeholder="E.g., Add more about our unique travel packages, remove the mention of prices and add more emojis")
        if st.button("Regenerate Post"):
            with st.spinner("Regenerating your Facebook post..."):
                st.session_state.post_info["feedback"] = feedback
                regenerated_post = post_generator.generate_fb_post(st.session_state.post_info, profile, st.session_state.current_post)
                if regenerated_post:
                    st.session_state.current_post = regenerated_post
                    st.rerun()

    if 'saved_fb_post' in st.session_state:
        st.header("Your Saved Facebook Post")
        st.write(st.session_state.saved_fb_post)