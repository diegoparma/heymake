"""
LLM Service
Servicio para interactuar con LLMs (OpenAI, Anthropic)
"""
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.generation import SceneBreakdown


class LLMService:
    """Servicio para análisis de guiones con LLM"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        
        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def analyze_script(
        self,
        script: str,
        style: str = "cinematic",
        reference_prompt: Optional[str] = None,
        num_scenes: Optional[int] = None,
        duration_target: Optional[int] = None
    ) -> List[SceneBreakdown]:
        """
        Analiza un guión y lo divide en escenas visuales
        """
        
        system_prompt = self._build_system_prompt(style, reference_prompt, num_scenes, duration_target)
        return await self._analyze_with_openai(script, system_prompt)
    
    def _build_system_prompt(
        self,
        style: str,
        reference_prompt: Optional[str],
        num_scenes: Optional[int],
        duration_target: Optional[int]
    ) -> str:
        """Construye el prompt del sistema"""
        
        prompt = f"""Eres un experto en dirección cinematográfica y storyboarding.
        
Tu tarea es analizar guiones y dividirlos en escenas visuales detalladas para crear trailers o publicidades.

Estilo: {style}
"""
        
        if reference_prompt:
            prompt += f"""\nPrompt de referencia (aplicar a todas las escenas):
{reference_prompt}

IMPORTANTE: Debes incorporar los elementos y el estilo del prompt de referencia en el 'image_prompt' de cada escena.
"""
        
        if num_scenes:
            prompt += f"Número aproximado de escenas: {num_scenes}\n"
        
        if duration_target:
            prompt += f"Duración objetivo total: {duration_target} segundos\n"
        
        prompt += """
Para cada escena, debes proporcionar:
1. order: número de orden de la escena
2. title: título breve de la escena
3. description: descripción visual detallada (qué se ve en pantalla)
4. dialogue: diálogo o narración si hay (opcional)
5. image_prompt: prompt optimizado para generar la imagen con IA (muy descriptivo, en inglés)
6. duration: duración estimada en segundos
7. notes: notas adicionales (opcional)

Responde ÚNICAMENTE con un JSON válido con este formato:
{
    "scenes": [
        {
            "order": 1,
            "title": "Título de la escena",
            "description": "Descripción visual detallada",
            "dialogue": "Diálogo o narración",
            "image_prompt": "Detailed visual prompt in English for AI image generation",
            "duration": 3.5,
            "notes": "Notas opcionales"
        }
    ]
}
"""
        return prompt
    
    async def _analyze_with_openai(
        self,
        script: str,
        system_prompt: str
    ) -> List[SceneBreakdown]:
        """Analiza con OpenAI"""
        
        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analiza este guión:\n\n{script}"}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        return [SceneBreakdown(**scene) for scene in data["scenes"]]
    
    async def _analyze_with_anthropic(
        self,
        script: str,
        system_prompt: str
    ) -> List[SceneBreakdown]:
        """Analiza con Anthropic"""
        
        response = await self.client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Analiza este guión:\n\n{script}"}
            ]
        )
        
        content = response.content[0].text
        
        # Extraer JSON de la respuesta
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        
        data = json.loads(json_str)
        
        return [SceneBreakdown(**scene) for scene in data["scenes"]]


# Lazy singleton - don't crash on import if OPENAI_API_KEY is missing
def get_llm_service():
    return LLMService()
