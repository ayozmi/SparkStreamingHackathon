import streamlit as st
import json

# Set the title of the app
st.title('Reddit Data Fetching App')

# Add a header
st.header('Fetch Data from Reddit')

# Add a description
st.write('This app fetches data from a specified subreddit.')

# Load client data
try:
    with open('path/to/your/key.json') as file:
        client_data = json.load(file)
except Exception as e:
    st.error("Error loading API keys. Ensure the key.json file is in the correct path.")
    st.stop()

# Inputs for subreddit and post limit
subreddit = st.text_input('Enter subreddit name:', 'mentalhealth')
post_limit = st.slider('Number of posts to fetch:', 1, 100, 10)

# Button to fetch data
if st.button('Fetch Data'):
    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_data["client_id"],
            client_secret=client_data["client_secret"],
            user_agent=client_data["user_agent"]
        )

        # Function to fetch data
        def fetch_reddit_data(subreddit_name, limit=10):
            data = []
            for submission in reddit.subreddit(subreddit_name).new(limit=limit):
                if submission.selftext == "":
                    continue
                post = {
                    'title': submission.title,
                    'text': submission.selftext,
                    'created_utc': submission.created_utc,
                    'id': submission.id
                }
                data.append(post)
            return data

        # Fetch data
        data = fetch_reddit_data(subreddit, post_limit)
        
        if data:
            st.success(f'Fetched {len(data)} posts from r/{subreddit}')
            st.write(data)
        else:
            st.warning('No posts fetched. Try a different subreddit or adjust the post limit.')
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# Sidebar for additional inputs or options
st.sidebar.title('Options')
st.sidebar.write('You can add additional options here.')
