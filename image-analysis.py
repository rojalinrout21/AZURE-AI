from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw
import sys
from matplotlib import pyplot as plt
from azure.core.exceptions import HttpResponseError
import requests
from azure.ai.vision import ImageAnalysisClient
from azure.ai.vision.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

def main():
    global cv_client
    try:
        # Load configuration settings from .env file
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')

        # Get image file path from command line or use default
        image_file = 'images/street.jpg'
        if len(sys.argv) > 1:
            image_file = sys.argv[1]

        # Read image data
        with open(image_file, "rb") as f:
            image_data = f.read()

        # Authenticate Azure AI Vision client
        cv_client = ImageAnalysisClient(
            endpoint=ai_endpoint,
            credential=AzureKeyCredential(ai_key)
        )

        # Analyze the image
        AnalyzeImage(image_file, image_data, cv_client)

        # Remove background/foreground
        BackgroundForeground(ai_endpoint, ai_key, image_file)

    except Exception as ex:
        print(f"An error occurred: {ex}")

def AnalyzeImage(image_filename, image_data, cv_client):
    print('\nAnalyzing image...')
    try:
        # Get result with specified features
        result = cv_client.analyze(
            image_data=image_data,
            visual_features=[
                VisualFeatures.CAPTION,
                VisualFeatures.DENSE_CAPTIONS,
                VisualFeatures.TAGS,
                VisualFeatures.OBJECTS,
                VisualFeatures.PEOPLE
            ]
        )

        # Process analysis results
        if result.caption:
            print(f"\nCaption: '{result.caption.text}' (confidence: {result.caption.confidence * 100:.2f}%)")

        if result.dense_captions:
            print("\nDense Captions:")
            for caption in result.dense_captions:
                print(f" Caption: '{caption.text}' (confidence: {caption.confidence * 100:.2f}%)")

        if result.tags:
            print("\nTags:")
            for tag in result.tags:
                print(f" Tag: '{tag.name}' (confidence: {tag.confidence * 100:.2f}%)")

        if result.objects:
            print("\nObjects in image:")
            image = Image.open(image_filename)
            fig = plt.figure(figsize=(image.width / 100, image.height / 100))
            plt.axis('off')
            draw = ImageDraw.Draw(image)
            color = 'cyan'

            for detected_object in result.objects:
                print(f" {detected_object.tags[0].name} (confidence: {detected_object.tags[0].confidence * 100:.2f}%)")
                r = detected_object.bounding_box
                bounding_box = ((r.x, r.y), (r.x + r.width, r.y + r.height))
                draw.rectangle(bounding_box, outline=color, width=3)
                plt.annotate(detected_object.tags[0].name, (r.x, r.y), backgroundcolor=color)

            plt.imshow(image)
            plt.tight_layout(pad=0)
            outputfile = 'objects.jpg'
            fig.savefig(outputfile)
            print(f"  Results saved in {outputfile}")

        if result.people:
            print("\nPeople in image:")
            image = Image.open(image_filename)
            fig = plt.figure(figsize=(image.width / 100, image.height / 100))
            plt.axis('off')
            draw = ImageDraw.Draw(image)
            color = 'cyan'

            for detected_person in result.people:
                r = detected_person.bounding_box
                bounding_box = ((r.x, r.y), (r.x + r.width, r.y + r.height))
                draw.rectangle(bounding_box, outline=color, width=3)

            plt.imshow(image)
            plt.tight_layout(pad=0)
            outputfile = 'people.jpg'
            fig.savefig(outputfile)
            print(f"  Results saved in {outputfile}")

    except HttpResponseError as e:
        print(f"Error during image analysis: Status code: {e.status_code}, Reason: {e.reason}, Message: {e.error.message}")

def BackgroundForeground(endpoint, key, image_file):
    api_version = "2023-02-01-preview"
    foregroundMatting = "backgroundRemoval"  # Can be "foregroundMatting" or "backgroundRemoval"
    print('\nRemoving background from image...')

    url = f"{endpoint}/computervision/imageanalysis:segment?api-version={api_version}&mode={foregroundMatting}"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }

    # Assuming image_file is a local path, convert it to the raw URL or base64 if necessary
    image_url = f"https://your-image-server/{image_file}"

    body = {"url": image_url}
    try:
        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            image = response.content
            with open("background.png", "wb") as file:
                file.write(image)
            print('  Results saved in background.png \n')
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error in background removal: {e}")

if _name_ == "_main_":
    main()
