import requests
import json
from src.utils import log_debug

"Client for communicating with Ollama/Mistral 7B"
"""
Initialize Ollama client

Args:
    base_url: Ollama server address
    model_name: Model to use (default: mistral)
"""
class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model_name="mistral"):
        self.base_url = base_url
        self.model_name = model_name
        self.endpoint = f"{base_url}/api/generate"
    
    """Check if Ollama server is running"""
    def is_available(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            log_debug("ERROR: Ollama server not available")
            return False
    
    """
    Generate text using Mistral 7B
    
    Args:
        prompt: The question/prompt to send
        temperature: Creativity level (0.0-1.0, lower=more deterministic)
        num_predict: Max tokens to generate
        timeout: Request timeout in seconds
    
    Returns:
        Generated text or None if error
    """
    def generate(self, prompt, temperature=0.7, num_predict=200, timeout=60):     
        if not self.is_available():
            log_debug("ERROR: Cannot connect to Ollama")
            return None
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": num_predict,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                log_debug(f"ERROR: Ollama returned status {response.status_code}")
                return None
        
        except requests.Timeout:
            log_debug("ERROR: Ollama request timeout")
            return None
        except Exception as e:
            log_debug(f"ERROR: {str(e)}")
            return None
    
    """
    Use LLM to make a question more natural/fluent
    
    Args:
        base_question: Original question template
    
    Returns:
        Enhanced question or original if LLM unavailable
    """
    def enhance_question(self, base_question):  
        prompt = f"""You are a Vietnamese chemistry education expert. Make this question more natural and engaging in Vietnamese: "{base_question}". Return ONLY the improved question, nothing else."""
        
        enhanced = self.generate(prompt, temperature=0.5, num_predict=100)
        
        if enhanced is None or len(enhanced) < 5:
            return base_question
        
        return enhanced

    "Test if Ollama is properly set up"
def test_ollama_connection():
    client = OllamaClient()
    if client.is_available():
        print("✓ Ollama is running and accessible")
        return True
    else:
        print("✗ Ollama is not accessible at http://localhost:11434")
        print("Make sure to run: ollama serve")
        return False
