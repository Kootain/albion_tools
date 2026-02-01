import cv2
import os
import sys
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision.game.map_analyzer import MapAnalyzer

def test_map_analyzer():
    # Load the uploaded image
    # Note: You need to copy the image to this path or update the path
    image_path = r"C:\Users\admin\.gemini\antigravity\brain\8dc79eb8-f17f-40e6-9186-02cb8caba4e1\uploaded_image_1765777331315.jpg"
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    image = cv2.imread(image_path)
    if image is None:
        print("Failed to load image")
        return

    analyzer = MapAnalyzer()
    
    print("Processing image...")
    result = analyzer.process(image)
    
    print("-" * 30)
    print("Analysis Result:")
    print(f"Name/Tier Info: {result.get('name_tier')}")
    print(f"Hostile Info: {result.get('hostile_info')}")
    print(f"Exits Found: {len(result.get('exits', []))}")
    print(f"Paths/Blobs Found: {result.get('path_count')}")
    print("-" * 30)
    
    # Visualize results
    for x, y in result.get('exits', []):
        cv2.circle(image, (x, y), 10, (0, 0, 255), -1)
    
    # Save result for inspection
    output_path = "map_analysis_result.jpg"
    cv2.imwrite(output_path, image)
    print(f"Result image saved to {output_path}")

if __name__ == "__main__":
    test_map_analyzer()
