from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from azure.ai.vision import ImageAnalysisClient
from azure.ai.vision.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

def main():
    try:
        # Load configuration settings
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        
        if not ai_endpoint or not ai_key:
            raise ValueError("AI_SERVICE_ENDPOINT or AI_SERVICE_KEY not set in .env file")

        # Authenticate Azure AI Vision client
        cv_client = ImageAnalysisClient(
            endpoint=ai_endpoint,
            credential=AzureKeyCredential(ai_key)
        )

        # Menu for text reading functions
        print('\n1: Use Read API for image (Lincoln.jpg)')
        print('2: Read handwriting (Note.jpg)')
        print('Any other key to quit\n')
        
        command = input('Enter a number: ')
        if command == '1':
            image_file = os.path.join('images', 'Lincoln.jpg')
            get_text_read(image_file, cv_client)
        elif command == '2':
            image_file = os.path.join('images', 'Note.jpg')
            get_text_read(image_file, cv_client)
        else:
            print("Exiting the program.")

    except Exception as ex:
        print(f"Error: {ex}")

def get_text_read(image_file, cv_client):
    print('\nReading text from:', image_file)
    
    # Open image file and read as bytes
    with open(image_file, "rb") as f:
        image_data = f.read()

    # Use Analyze image function to read text in the image
    result = cv_client.analyze_image(
        image_data=image_data,
        visual_features=[VisualFeatures.read]
    )

    # Display the image and overlay it with the extracted text
    if result.read is not None:
        print("\nText detected in the image:")
        
        # Prepare the image for drawing text annotations
        image = Image.open(image_file)
        fig = plt.figure(figsize=(image.width / 100, image.height / 100))
        plt.axis('off')
        draw = ImageDraw.Draw(image)
        color = 'cyan'

        for line in result.read.blocks[0].lines:
            print(f"\n  {line.text}")  # Print detected text
            
            # Extract bounding polygon for line
            bounding_polygon = [(r.x, r.y) for r in line.bounding_polygon]
            print("   Bounding Polygon:", bounding_polygon)

            for word in line.words:
                # Extract bounding polygon for each word
                word_polygon = [(r.x, r.y) for r in word.bounding_polygon]
                print(f"    Word: '{word.text}', Bounding Polygon: {word_polygon}, Confidence: {word.confidence:.4f}")
                
                # Draw word bounding polygon
                draw.polygon(word_polygon, outline=color, width=3)
            
            # Draw line bounding polygon
            draw.polygon(bounding_polygon, outline=color, width=3)

        # Save and display the image with overlays
        output_file = 'text_overlay.jpg'
        plt.imshow(image)
        plt.tight_layout(pad=0)
        fig.savefig(output_file)
        print(f'\n  Results saved in: {output_file}')
    else:
        print("No text detected in the image.")

if _name_ == "_main_":
    main()