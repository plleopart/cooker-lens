import json
import uuid
from app.config import AI_PROMPT_DIR, OPENAI_API_KEY, AI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS, \
    INPUT_TOKENS_PRICE_PER_MILLION, OUTPUT_TOKENS_PRICE_PER_MILLION
from openai import OpenAI
import base64
from PIL import Image
import io


def encode_resized_image(image_path, size=(128, 128)):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = img.resize(size)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return base64_image


class AIClient:
    def __init__(self, tags: list, categories: list, description: str, transcript: str, images: list = None):

        self.input_json = {
            "tags": tags,
            "categories": categories,
            "description": description,
            "transcript": transcript,
        }

        self.image_map = {}
        if images:
            for image in images:
                base64_image = encode_resized_image(image)

                data_url = f"data:image/jpg;base64,{base64_image}"
                image_id = str(uuid.uuid4())
                self.image_map[image_id] = {"image_path": image, "base64": data_url}

        # Instantiate OpenAI client with API key
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.ai_response = None
        self.usage = None
        self.image_path = None

        # Load prompt template from file
        with open(AI_PROMPT_DIR, "r", encoding="utf-8") as f:
            self.prompt = f.read()

    def get_suggested_title(self) -> str:
        if not self.ai_response:
            raise ValueError("AI response is not available. Please run the AI client first.")

        return self.ai_response.get("metadata", {}).get("title", "") or str(uuid.uuid4())

    def get_suggested_image(self) -> str:
        return self.image_path

    def get_ai_response(self) -> dict:
        if not self.ai_response:
            raise ValueError("AI response is not available. Please run the AI client first.")

        return self.ai_response.get("response", {})

    def get_ai_metadata(self) -> dict:
        if not self.ai_response:
            raise ValueError("AI response is not available. Please run the AI client first.")

        return self.ai_response.get("metadata", {})

    def estimate_cost(self):
        prompt_tokens = self.usage.prompt_tokens
        completion_tokens = self.usage.completion_tokens
        total_tokens = self.usage.total_tokens

        input_cost = (prompt_tokens / 1_000_000) * float(INPUT_TOKENS_PRICE_PER_MILLION)
        output_cost = (completion_tokens / 1_000_000) * float(OUTPUT_TOKENS_PRICE_PER_MILLION)
        total_cost = input_cost + output_cost

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
        }

    def run(self) -> None:
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": json.dumps(self.input_json, ensure_ascii=False)}
        ]

        if self.image_map:

            messages.append({
                "role": "system",
                "content": "Review the images. Each image represents a different stage or variation of a dish. Analyze all the images and identify the one that best represents the final, fully prepared version of the dish. In the output metadata section, include the id of the selected image under the field selectedImageId"
            })

            for image_id, image_data in self.image_map.items():
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"image with id {image_id}"},
                        {"type": "image_url", "image_url": {"url": image_data['base64'], "detail": "high"}}
                    ]
                })

        response = self.client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=AI_TEMPERATURE,
            max_tokens=int(AI_MAX_TOKENS),
            response_format={"type": "json_object"}
        )

        result_content = response.choices[0].message.content
        self.usage = response.usage

        try:
            self.ai_response = json.loads(result_content)

            if self.ai_response.get("metadata", {}).get("selectedImageId") is not None:
                selected_image_id = self.ai_response["metadata"]["selectedImageId"]
                if selected_image_id in self.image_map:

                    self.image_path = self.image_map[selected_image_id]["image_path"]
                else:
                    raise ValueError(f"Selected image ID {selected_image_id} not found in image map.")


        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON returned from OpenAI:\n{result_content}")
