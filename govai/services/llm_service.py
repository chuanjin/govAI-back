import json
import logging
import litellm
from govai.config import settings
from govai.services.prompt_builder import SYSTEM_PROMPT, GUIDANCE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Ensure litellm uses the API key from settings
litellm.api_key = settings.gemini_api_key

async def generate_answer(
    augmented_prompt: str,
    conversation_history: list[dict],
    is_guidance_mode: bool = False,
) -> dict:
    """
    Send the augmented prompt to Gemini via LiteLLM with fallback logic.
    Returns parsed JSON dict with the structured answer.
    """
    system_prompt = GUIDANCE_SYSTEM_PROMPT if is_guidance_mode else SYSTEM_PROMPT

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history for context
    for msg in conversation_history:
        messages.append(msg)

    # Add the current augmented prompt
    messages.append({"role": "user", "content": augmented_prompt})

    try:
        # Using LiteLLM's built-in fallback functionality
        response = await litellm.acompletion(
            model=settings.primary_model,
            fallbacks=[settings.fallback_model],
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
            api_key=settings.gemini_api_key
        )

        content = response.choices[0].message.content
        
        # Extract JSON object using string manipulation to handle extra text
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx+1]
        else:
            # Fallback cleanup
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
        
        parsed = json.loads(content.strip())

        # Validate required fields
        if "summary" not in parsed:
            parsed["summary"] = "I couldn't generate a proper response. Please try again."
        if "steps" not in parsed:
            parsed["steps"] = []
        if "sources" not in parsed:
            parsed["sources"] = []

        return parsed

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return {
            "summary": "I encountered an error processing your request. Please try again.",
            "eligibility": None,
            "steps": [],
            "notes": None,
            "sources": [],
        }
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return {
            "summary": "I'm temporarily unable to process your request. Please try again in a moment.",
            "eligibility": None,
            "steps": [],
            "notes": f"Service temporarily unavailable: {str(e)}",
            "sources": [],
        }
