import os
from dotenv import load_dotenv
from src.exceptions.exceptions import GraphAPIError
from src.services.facebook_service import FacebookPoster

load_dotenv()

if __name__ == "__main__":
    FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
    FB_PAGE_ID = os.getenv("FB_PAGE_ID")

    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        raise ValueError("Missing required environment variables: FB_ACCESS_TOKEN or FB_PAGE_ID")

    print("Initializing FacebookPoster...")
    facebook_poster = FacebookPoster(access_token=FB_ACCESS_TOKEN, page_id=FB_PAGE_ID)

    test_message = "Test post from automated pipeline: Text-only connection check."

    try:
        print(f"Attempting to post to Page ID: {FB_PAGE_ID}...")
        response = facebook_poster.publish_post_item(message=test_message)
        
        print("Successfully sent request to Facebook API!")
        print(f"API Response Data: {response}")

    except GraphAPIError as err:
        print(f"\n[GraphAPIError] Facebook posting failed:")
        print(f"Error Message: {err}")
        if hasattr(err, "code") and err.code:
            print(f"Error Code: {err.code}")

    except Exception as err:
        print(f"\n[Unexpected Error] {err}")