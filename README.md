# Mental Health Data Processing App

## Overview
This application retrieves data from Reddit, processes it and provides a searchable interface through a Streamlit web app. 
The goal is to facilitate mental health-related data analysis and insights.

## Components

1. **Data Retrieval from Reddit:**
   - The application fetches data from specific subreddit related to mental health using the Reddit API.

2. **Data Transmission to Spark:**
   - The retrieved data is sent via sockets to a Spark cluster for distributed processing.

3. **Data Processing and Analysis:**
   - Spark processes the incoming data to derive meaningful words related to mental health topics.

4. **Data Storage:**
   - Processed data is saved into a csv file for persistence and further analysis.

5. **Streamlit Web Application:**
   - A Streamlit-based web interface allows users to search and visualize the processed Reddit data. Users can search for specific topics or keywords related to mental health discussions on Reddit.

## Usage
1. Clone the repository:

        git clone https://github.com/ayozmi/SparkStreamingHackathon.git

2. install dependecies: 
 
        pip install -r requirements.txt

3. Setup your reddit API key: Create a folder in root called 'config' and add a json file with your key

        {
          "client_id": "your_client_id",
          "client_secret": "your_key",
          "user_agent": "user_agent"
        }

4. Create the .env file in the root directory like the following:

         MY_PYTHON_PATH=YOUR_PYTHON_PATH

5. Run dataProcessing.py and streamingData.py

        cd ./data
        python streamingData.py
        cd ../processing
        python dataProcessing.py
6. Run streamlit

        cd ../visualization
        streamlit run app.py

## License
This project is licensed under the MIT License - see the LICENSE file for details.