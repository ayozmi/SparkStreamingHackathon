import praw
import socket
import json
import time
import os
import logging
import sys

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate to the root folder by going up one level from the current directory
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

logging_dir = os.path.join(root_dir, "logs/streamingData")
if not os.path.exists(logging_dir):
    os.makedirs(logging_dir)
logging_file = os.path.join(logging_dir, "logs.log")
logging.basicConfig(filename=logging_file, level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get the config dir with the api key
config_dir = os.path.join(root_dir, "config")

try:
    with open(os.path.join(config_dir, "key.json"), "r") as file:
        client_data = json.load(file)
except Exception as e:
    logging.error(
        f"Could not load json data from config folder! "
        f"Are you sure you have created the json file containing your API information? Error: {e}")
    sys.exit(1)

try:
    reddit = praw.Reddit(
        client_id=client_data["client_id"],
        client_secret=client_data["client_secret"],
        user_agent=client_data["user_agent"]
    )
except Exception as e:
    logging.error(f"Could not connect to the Reddit API! Error: {e}")
    sys.exit(1)


def fetch_reddit_data(subreddit_name, limit=10):
    data = []
    for submission in reddit.subreddit(subreddit_name).new(limit=limit):
        # If the text is empty, the post is probably an image or video we skip to the next post
        if submission.selftext == "":
            continue
        post = {
            'text': submission.title + ' ' + submission.selftext,
            'created_utc': submission.created_utc,
            'id': submission.id
        }
        data.append(post)
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            comment_data = {
                'text': comment.body,
                'created_utc': comment.created_utc,
                'id': comment.id
            }
            data.append(comment_data)
    return data


def send_data(data_s, number_tries, host='localhost', port=9999):
    attempts = 0
    while attempts < number_tries:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print("Connection established.")
            break
        except socket.error as socket_error:
            error = f"Could not connect to the socket: {socket_error}"
            attempts += 1
            if attempts == number_tries:
                logging.error(f"Could not connect to the socket after {number_tries}: {socket_error} exiting.")
                sys.exit(error)
            # Log the error wait a bit and try again
            logging.error(error)
            time.sleep(20)
        finally:
            if attempts == number_tries and 's' in locals():
                # The warning is not accurate as you can only reach this statement if the variable "s" is created
                s.close()  # Ensure the socket is closed if it was created
            if attempts == number_tries:
                return False
    try:
        for item in data_s:
            s.sendall((json.dumps(item) + '\n').encode('utf-8'))
            time.sleep(0.1)
    except ConnectionResetError as cre:
        logging.error(f"Connection reset by peer: {cre}")
        sys.exit(str(cre))
    except Exception as exce:
        logging.error(f"An unexpected error occurred: {exce}")
        sys.exit(str(e))
    finally:
        s.close()


if __name__ == '__main__':
    # Name of our subreddit
    subreddit = 'mentalhealth'
    while True:
        data = fetch_reddit_data(subreddit)
        send_data(data, 5)
        # print(data)
        time.sleep(60)
