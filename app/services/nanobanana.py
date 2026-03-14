import httpx
from app.core.config import settings
from typing import Optional

async def generate_3d_model(image_url: str) -> Optional[str]:
    """
    Call Nanobanana API to generate a 3D model from an image URL.
    Returns the URL of the generated GLB model.
    """
    api_url = "https://api.nanobanana.ai/v1/generate-3d"
    headers = {
        "Authorization": f"Bearer {settings.NANOBANANA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "image_url": image_url,
        "format": "glb"
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("model_url")
    except Exception as e:
        print(f"Nanobanana API error: {e}")
        return None
