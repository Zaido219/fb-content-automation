import os
from dotenv import load_dotenv
from src.exceptions.exceptions import GraphAPIError
from src.services.facebook_service import FacebookPoster
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent
image_path = project_root / "storage" / "test_images" / "Gemini_Generated_Image_nwq6sanwq6sanwq6.jpg"

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
        if not image_path.is_file():
            raise FileNotFoundError(f"Image file not found on: {image_path}")
        
        print(f"Attempting to post to Page ID: {FB_PAGE_ID}...")
        response = facebook_poster.publish_photo_item(image_path, "hello there")
        
        print("Successfully sent request to Facebook API!")
        print(f"API Response Data: {response}")

    except GraphAPIError as err:
        print(f"\n[GraphAPIError] Facebook posting failed:")
        print(f"Error Message: {err}")
        if hasattr(err, "code") and err.code:
            print(f"Error Code: {err.code}")

    except Exception as err:
        print(f"\n[Unexpected Error] {err}")