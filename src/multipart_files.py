from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

image_kit = ImageKit(
    os.getenv('IMAGEKIT_PUBLIC_KEY'),
    os.getenv('IMAGEKIT_PRIVATE_KEY'),
    os.getenv('IMAGEKIT_URL')
)
