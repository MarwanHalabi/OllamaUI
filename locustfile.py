from locust import HttpUser, task, between
from PIL import Image
import io
import base64

class ChatUser(HttpUser):
    wait_time = between(3, 8)  # Wait 3-8 seconds between tasks
    
    def on_start(self):
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Convert to base64
        encoded = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        self.test_image = f"data:image/png;base64,{encoded}"
        
    @task(1)
    def visit_chat_page(self):
        self.client.get("/")
    
    @task(3)
    def send_image_for_detection(self):        
        payload = {
            "messages": [{ "role": "user", "content": "Detect objects in this image" }],
            "selectedModel": "detection",
            "data": { "images": [self.test_image] }
        }
        headers = {"Content-Type": "application/json"}
        
        with self.client.post("/api/chat", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")