import streamlit as st
import json
import random
import pandas as pd
from llamaapi import LlamaAPI
from st_copy_to_clipboard import st_copy_to_clipboard as stc

import asyncio

# Setup or get event loop
def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

get_or_create_eventloop()

class TravelAgentPromotionTool:
    def __init__(self):
        api_token = "LL-DVfPu5BJU8SqjomBN2KLlmYaWIFELl5fAoegicsufcLpraWJ7PiWK4bPCdIcBAbW"
        self.llama = LlamaAPI(api_token)

    def extract_info(self, summary):
        api_request_json = {
            'model': 'llama-70b-chat',
            'functions': [
                {
                    "name": "extract_travel_agent_info",
                    "description": "Extract travel agent information from the provided summary",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the travel agent"},
                            "experience": {"type": "string", "description": "Years of experience"},
                            "specialties": {"type": "array", "items": {"type": "string"}, "description": "List of specialties"},
                            "achievements": {"type": "string", "description": "Key achievements"},
                            "target_audience": {"type": "string", "description": "Target audience description"},
                            "unique_selling_points": {"type": "array", "items": {"type": "string"}, "description": "Unique selling points"},
                            "preferred_destinations": {"type": "array", "items": {"type": "string"}, "description": "Preferred or frequently booked destinations"}
                        },
                        "required": ["name", "experience", "specialties", "target_audience"]
                    }
                }
            ],
            'function_call': {'name': 'extract_travel_agent_info'},
            'messages': [
                {'role': 'user', 'content': f"Extract travel agent information from this summary:\n\n{summary}"}
            ],
        }
        
        response = self.llama.run(api_request_json)
        return response.json()['choices'][0]['message']

    def generate_content(self, agent_info, content_type, content_settings):
        length_range = content_settings['length_range']
        tone = content_settings['tone']
        focus = content_settings['focus']
        language = content_settings['language']

        api_request_json = {
            "model": "llama-70b-chat",
            "messages": [
                {"role": "system", "content": f"You are an AI assistant creating promotional content for travel agents. Generate content directly without any introductory phrases or meta-commentary. Generate content directly in the first-person. Use a {tone} tone, focus on {focus}, and write in {language}."},
                {"role": "user", "content": f"Generate a {content_type} for a travel agent with this information:\n{json.dumps(agent_info, indent=2)}\nThe content should be {length_range} words long. Create the content directly without any introductory phrases."},
            ],
            "max_tokens": 2000
        }
           
        try:
            response = self.llama.run(api_request_json)
            content = response.json()['choices'][0]['message']['content']
            return self.post_process_content(content)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

    def post_process_content(self, content):
        introductory_phrases = [
            "Here's a", "Here is a", "Here's an", "Here is an",
            "This is a", "This is an", "I've created", "I have created",
            "Below is", "The following is"
        ]
        for phrase in introductory_phrases:
            if content.startswith(phrase):
                content = content[len(phrase):].lstrip()
        return content.strip()





def main():
    st.set_page_config(page_title="Travel Agent Promotion Tool", page_icon="✈️", layout="wide")
    tool = TravelAgentPromotionTool()

    st.title("✈️ AI-Powered Travel Agent Promotion Tool")

    page = st.sidebar.selectbox("Choose a page", ["Profile-based Content", "Summary-based Content", "AI FB Post Writer", "Instagram Caption Generator"])

    if page == "Profile-based Content":
        profile_based_content(tool)
    elif page == "Summary-based Content":
        summary_based_content(tool)
    elif page == "AI FB Post Writer":
        facebook_post_writer(tool)
    elif page == "Prompt Generator For ChatGPT":
        prompt_generator_page()
    else:
        instagram_caption_generator(tool)



def generate_prompt(summary, platform):
    # Template for generating the prompt
    system_prompt = "I need you to be a prompt engineer and tailor a good prompt for us. "
    action_prompt = f"The prompt should be tailored for {platform}, focusing on the following summary:\n\n{summary}\n\n"
    final_prompt = system_prompt + action_prompt + "The AI should act as a professional content writer and create engaging content for this platform."

    return final_prompt

def prompt_generator_page():
    st.title("Prompt Generator For ChatGPT")

    st.write("Generate tailored prompts for promoting your posts on different platforms.")

    # Input fields
    summary = st.text_area("What do you want to promote?", help="Enter the details of what you want to promote.")
    platform = st.selectbox("Platform", ["ChatGPT", "Claude", "Other AI Models"], help="Select the platform where you'll use the prompt.")

    if st.button("Generate Prompt"):
        if summary:
            prompt = generate_prompt(summary, platform)
            st.subheader("Your Generated Prompt")
            st.text_area("Generated Prompt", value=prompt, height=200)
        else:
            st.warning("Please enter what you want to promote.")



def summary_based_content(tool):
    def sidebar_configuration():
        st.sidebar.title("🛠️ Content Personalization")

        # Sidebar expands by default
        with st.sidebar.expander("**✈️ Travel Content Settings**", expanded=True):

            # "Your Name" input
            agent_name = st.text_input("Your Name", help="Enter your name as the travel agent.")

            # Years of Experience input
            experience_years = st.number_input("Years of Experience", min_value=0, max_value=50, help="Enter the number of years you've been in the travel industry.")

            # Specialties input
            specialties = st.text_area("Specialties", help="List your specialties, such as adventure travel, luxury trips, family vacations, etc. (comma-separated).")

            # Achievements input
            achievements = st.text_area("Achievements", help="Highlight any key achievements, such as awards, recognitions, or milestones (comma-separated).")

            # Content Length Range
            length_range_options = ["<100", "100 - 200", "200 - 450", "450 - 800", "800 - 1000"]
            length_range = st.selectbox("Content Length Range", options=length_range_options, help="Select the length range for the content you want to generate.")

            # Content Tone Options
            content_tone_options = ["Casual", "Professional", "Inspirational", "Informative", "Adventurous", "Luxury", "Budget-friendly", "Family-oriented", "Customize"]
            content_tone = st.selectbox("Content Tone", options=content_tone_options, help="Choose the tone of your travel content.")
            if content_tone == "Customize":
                custom_tone = st.text_input("Enter custom tone", help="Specify a custom tone for your content.")
                if custom_tone:
                    content_tone = custom_tone
                else:
                    st.warning("Please specify a custom tone for your content.")

            # Target Audience Options
            target_audience_options = ["General Travelers", "Luxury Travelers", "Budget Backpackers", "Family Vacationers", "Adventure Seekers", "Business Travelers", "Honeymooners", "Senior Travelers", "Gen-Z Explorers", "Customize"]
            target_audience = st.selectbox("Target Audience", options=target_audience_options, help="Choose your target audience.")
            if target_audience == "Customize":
                custom_audience = st.text_input("Enter custom target audience", help="Specify your custom target audience.", placeholder="E.g., Eco-conscious travelers, Solo female travelers, etc.")
                if custom_audience:
                    target_audience = custom_audience
                else:
                    st.warning("Please specify your custom target audience.")

            # Content Type Options
            content_type_options = ["Destination Guide", "Travel Tips", "Itinerary", "Travel Story", "Hotel Review", "Local Cuisine", "Cultural Insights", "Adventure Activity", "Travel News", "Promotional Offer"]
            content_type = st.selectbox("Content Type", options=content_type_options, help="Choose the type of travel content.")

            # Content Focus Options
            content_focus_options = ["Beach Getaways", "City Breaks", "Mountain Retreats", "Cultural Experiences", "Adventure Tours", "Luxury Escapes", "Budget Travel", "Eco-Tourism", "Food Tourism", "Historical Sites", "Customize"]
            content_focus = st.selectbox("Content Focus", options=content_focus_options, help="Choose the focus of your travel content.")
            if content_focus == "Customize":
                custom_focus = st.text_input("Enter custom content focus", help="Specify a custom focus for your content.")
                if custom_focus:
                    content_focus = custom_focus
                else:
                    st.warning("Please specify a custom focus for your content.")

            # Content Language
            content_language = st.selectbox("Content Language", options=["English", "Spanish", "French", "German", "Italian", "Chinese", "Japanese", "Arabic", "Russian", "Portuguese", "Customize"], help="Choose the language of the content.")
            if content_language == "Customize":
                custom_lang = st.text_input("Enter custom language", help="Specify the content language.")
                if custom_lang:
                    content_language = custom_lang
                else:
                    st.warning("Please specify the language of your content.")

        return {
            "agent_name": agent_name,
            "experience_years": experience_years,
            "specialties": specialties,
            "achievements": achievements,
            "length_range": length_range,
            "content_tone": content_tone,
            "target_audience": target_audience,
            "content_type": content_type,
            "content_focus": content_focus,
            "content_language": content_language
        }


    st.header("Summary-based Content Generation")
    st.markdown("Enter a summary about yourself as a travel agent, and we'll generate content based on it!")

    summary = st.text_area("Enter your summary:", height=200)
    content_type = st.selectbox(
        "Select Content Type to Generate", 
        ["Social Media Post", "Blog Post", "Promotional Offer", "Website Bio"]
    )

    settings = sidebar_configuration()

    if st.button("Generate Content"):
        if summary:
            with st.spinner("Generating content..."):
                agent_info = tool.extract_info(summary)
                content_settings = {
                    "length_range": settings['length_range'],
                    "tone": settings['content_tone'],
                    "focus": settings['content_focus'],
                    "language": settings['content_language']
                }
                generated_content = tool.generate_content(agent_info, content_type, content_settings)
            
            if generated_content:
                st.subheader("Generated Content")
                st.write(generated_content)

                edited_content = st.text_area("Edit Your Content", value=generated_content, height=300)

                if st.button("Copy Edited Content to Clipboard"):
                    stc.copy_to_clipboard(edited_content)
                    st.success("Content copied to clipboard!")
        else:
            st.warning("Please enter a summary before generating content.")

    if 'saved_content' in st.session_state:
        st.header("Your Saved Content")
        st.write(st.session_state.saved_content)



def facebook_post_writer(tool):
    st.title("📱 AI FB Post Writer for Travel Agents")
    st.markdown(
        """
        This Facebook Post Generator will help you create a compelling Facebook post for your travel agency.
        Please provide the following details to generate your post:
        """
    )
    
    col1, col2 = st.columns(2)
    with col1:
        post_goal_options = ["Promote a travel package", "Share travel tips", "Increase engagement", "Showcase a destination", "Customize"]
        post_goal = st.selectbox(
            "🎯 **What is the goal of your post?**",
            post_goal_options,
            index=2,
            help="Select the main goal of your post."
        )
        if post_goal == "Customize":
            post_goal = st.text_input(
                "🎯 **Customize your goal:**",
                placeholder="e.g., Announce a travel event",
                help="Provide a specific goal if you selected 'Customize'."
            )
        target_audience = st.text_input(
            "👥 **Describe your target audience:**",
            placeholder="e.g., Adventure seekers, Luxury travelers",
            help="Describe the audience you are targeting with this post."
        )
        include = st.text_input(
            "📷 **What elements do you want to include?**",
            placeholder="e.g., Travel package details, Destination highlights",
            help="Specify any elements you want to include in the post (e.g., videos, links, hashtags, questions)."
        )
    with col2:
        post_tone_options = ["Informative", "Exciting", "Inspirational", "Luxurious", "Adventurous", "Customize"]
        post_tone = st.selectbox(
            "🎨 **What tone do you want to use?**",
            post_tone_options,
            index=2,
            help="Choose the tone you want to use for the post."
        )
        if post_tone == "Customize":
            post_tone = st.text_input(
                "🎨 **Customize your tone:**",
                placeholder="e.g., Family-friendly",
                help="Provide a specific tone if you selected 'Customize'."
            )
        travel_agency_name = st.text_input(
            "🏢 **What is your travel agency name?**",
            placeholder="e.g., Wanderlust Adventures",
            help="Provide the name of your travel agency. This will be used in the post."
        )
        avoid = st.text_input(
            "❌ **What elements do you want to avoid?**",
            placeholder="e.g., Overly promotional language, Complex itineraries",
            help="Specify any elements you want to avoid in the post."
        )

    if st.button("🚀 Generate Facebook Post"):
        if not travel_agency_name or not target_audience:
            st.error("🚫 Please provide the required inputs: Travel Agency Name and Target Audience.")
        else:
            with st.spinner("Generating your Facebook post..."):
                generated_post = tool.generate_content(
                    {
                        "name": travel_agency_name,
                        "target_audience": target_audience,
                        "post_goal": post_goal,
                        "include": include,
                        "avoid": avoid
                    },
                    "Facebook Post",
                    {
                        "length_range": "between 100 and 200",
                        "tone": post_tone,
                        "focus": post_goal,
                        "language": "English"
                    }
                )
            
            if generated_post:
                st.subheader("**🧕 Verify: AI can make mistakes. Please review and edit as needed.**")
                st.write("## 📄 Generated Facebook Post:")
                st.write(generated_post)
                
                edited_post = st.text_area("Edit Your Post", value=generated_post, height=300)
                

                if st.button("Copy to Clipboard"):
                    stc.copy_to_clipboard(edited_post)
                    st.success("Content copied to clipboard!")
            else:
                st.error("Error: Failed to generate Facebook Post.")

    if 'saved_fb_post' in st.session_state:
        st.header("Your Saved Facebook Post")
        st.write(st.session_state.saved_fb_post)



def instagram_caption_generator(tool):
    st.title("📸 Instagram Caption Generator for Travel Agents")
    st.markdown(
        """
        Generate engaging Instagram captions for your travel agency posts.
        Provide the following details to create your captions:
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        input_insta_keywords = st.text_area(
            "📝 Keywords",
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
        if not input_insta_keywords:
            st.error('** 🫣 Please provide keywords to generate Instagram captions. Keywords are required!**')
        else:
            with st.spinner("Generating Instagram captions..."):
                insta_captions = tool.generate_instagram_captions(
                    input_insta_keywords,
                    input_insta_type,
                    input_insta_cta,
                    input_insta_audience,
                    input_insta_language
                )
            if insta_captions:
                st.subheader('**👩👩🔬 Go Viral with these Instagram captions! 🎆🎇 🎇**')
                st.code(insta_captions)

                edited_captions = st.text_area("Edit Your Captions", value=insta_captions, height=300)
                
            if st.button("Copy Edited Content to Clipboard"):
                stc.copy_to_clipboard(edited_captions)
                st.success("Content copied to clipboard!")
            else:
                st.error("💥**Failed to generate Instagram Captions. Please try again!**")

    if 'saved_insta_captions' in st.session_state:
        st.header("Your Saved Instagram Captions")
        st.write(st.session_state.saved_insta_captions)


def profile_based_content(tool):
    st.header("Profile-based Content Generation")
    st.markdown("Create engaging content to promote your travel agency!")

    # Sidebar configuration
    st.sidebar.header("Your Profile")
    agent_name = st.sidebar.text_input("Your Name", placeholder="e.g., John Smith", help="Enter your name as the travel agent.")
    experience_years = st.sidebar.number_input("Years of Experience", min_value=0, max_value=50, help="Enter the number of years you've been in the travel industry.")
    specialties = st.sidebar.text_area("Specialties", placeholder="e.g., Adventure travel, Luxury trips, Family vacations", help="List your specialties (comma-separated).")
    achievements = st.sidebar.text_area("Achievements", placeholder="e.g., Top Travel Agent 2023, 1000+ satisfied clients", help="Highlight any key achievements (comma-separated).")

    # Main content area
    col1, col2 = st.columns(2)
    with col1:
        content_type_options = ["Destination Guide", "Travel Tips", "Itinerary", "Travel Story", "Hotel Review", "Local Cuisine", "Cultural Insights", "Adventure Activity", "Travel News", "Promotional Offer"]
        content_type = st.selectbox("Content Type", options=content_type_options, help="Choose the type of travel content.")

        length_range_options = {"<100": "less than 100", "100 - 200": "between 100 and 200", "200 - 450": "between 200 and 450", "450 - 800": "between 450 and 800", "800 - 1000": "between 800 and 1000"}
        content_length_range = st.selectbox("Content Length Range", options=list(length_range_options.keys()), help="Select the length range for the content you want to generate.")

        content_tone_options = ["Casual", "Professional", "Inspirational", "Informative", "Adventurous", "Luxury", "Budget-friendly", "Family-oriented", "Customize"]
        content_tone = st.selectbox("Content Tone", options=content_tone_options, help="Choose the tone of your travel content.")
        if content_tone == "Customize":
            content_tone = st.text_input("Custom Tone", placeholder="e.g., Eco-friendly", help="Specify a custom tone for your content.")

    with col2:
        target_audience = st.text_input("Target Audience", placeholder="e.g., Adventure seekers, Luxury travelers, Families", help="Describe your target audience.")

        content_focus = st.text_input("Content Focus", placeholder="e.g., Beach getaways, Cultural experiences, Food tourism", help="Specify the focus of your content.")

        content_language = st.selectbox("Content Language", options=["English", "Spanish", "French", "German", "Italian", "Chinese", "Japanese", "Arabic", "Russian", "Portuguese", "Customize"], help="Choose the language of the content.")
        if content_language == "Customize":
            content_language = st.text_input("Custom Language", placeholder="e.g., Dutch", help="Specify the content language.")

    if st.button("Generate Content"):
        if not agent_name or not target_audience:
            st.error("🚫 Please provide the required inputs: Your Name and Target Audience.")
        else:
            with st.spinner("Generating your content..."):
                agent_info = {
                    "name": agent_name,
                    "experience": experience_years,
                    "specialties": specialties.split(','),
                    "achievements": achievements.split(','),
                    "target_audience": target_audience,
                }

                content_settings = {
                    "length_range": length_range_options[content_length_range],
                    "tone": content_tone,
                    "focus": content_focus,
                    "language": content_language
                }

                generated_content = tool.generate_content(agent_info, content_type, content_settings)
            
            if generated_content:
                st.subheader("Generated Content")
                st.write(generated_content)

                edited_content = st.text_area("Edit Your Content", value=generated_content, height=300)

            if st.button("Copy Edited Content to Clipboard"):
                stc.copy_to_clipboard(edited_content)
                st.success("Content copied to clipboard!")

    if 'saved_content' in st.session_state:
        st.header("Your Saved Content")
        st.write(st.session_state.saved_content)

    st.header("Additional Tools")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Content Calendar")
        if st.button("Generate Content Calendar"):
            calendar = generate_content_calendar()
            st.write(calendar)

    with col2:
        st.subheader("Hashtag Generator")
        if st.button("Generate Hashtags"):
            hashtags = generate_hashtags()
            st.write(" ".join(hashtags))




def generate_content_calendar():
    content_types = ["Social Media Post", "Blog Post", "Promotional Offer"]
    calendar = {}
    for i in range(7):
        day = (pd.Timestamp.now() + pd.Timedelta(days=i)).strftime("%A")
        calendar[day] = random.choice(content_types)
    return calendar

def generate_hashtags():
    travel_hashtags = ["#TravelAgent", "#Wanderlust", "#TravelTips", "#VacationPlanning", 
                       "#LuxuryTravel", "#AdventureAwaits", "#ExploreTheWorld", "#DreamDestinations"]
    return random.sample(travel_hashtags, 5)

if __name__ == "__main__":
    main()