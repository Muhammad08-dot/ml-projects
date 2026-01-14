import streamlit as st
import requests
import base64

st.set_page_config(page_title="Intelligent Bot Finder", layout="centered")

st.title("🔎 Intelligent Bot & Script Finder")
st.markdown("Find and Preview high-quality automation scripts directly from GitHub.")

# Search Input
query = st.text_input("🔍 Search Query (e.g., Discord Music Bot)", "Discord Bot")

# --- Function to Get ReadMe ---
def get_readme_content(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    response = requests.get(url)
    if response.status_code == 200:
        # GitHub sends content in Base64
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return content
    return "❌ No Documentation (README) found for this repository."

if st.button("Search Repositories"):
    with st.spinner("Searching GitHub..."):
        api_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            items = response.json().get('items', [])[:5] # Top 5 results
            st.success(f"✅ Found {len(items)} Top Results")
            
            for item in items:
                repo_name = item['name']
                owner = item['owner']['login']
                stars = item['stargazers_count']
                desc = item['description']
                clone_url = item['clone_url']
                repo_url = item['html_url']
                
                # --- Result Card ---
                with st.expander(f"⭐ {stars} | {repo_name} (by {owner})"):
                    st.write(f"**Description:** {desc}")
                    st.code(f"git clone {clone_url}", language="bash")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"[🔗 View on GitHub]({repo_url})")
                    
                    # --- NEW FEATURE: Live Preview Button ---
                    with c2:
                        # Har button ki unique key honi chahiye
                        if st.button("📖 Read Documentation", key=repo_name):
                            st.info("Fetching Documentation...")
                            readme_text = get_readme_content(owner, repo_name)
                            st.markdown("---")
                            st.markdown(readme_text) # Renders Markdown directly
                            st.markdown("---")
                            
        else:
            st.error("⚠️ API Error! GitHub API limit reached or connection failed.")