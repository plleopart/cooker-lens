from app.config import MEALIER_URL, MEALIER_API_KEY, MEALIER_DEFAULT_CATEGORIES_ID

import os
import uuid
import requests
import json

CATEGORIES_PATH = "/api/organizers/categories?perPage=-1"
TAGS_PATH = "/api/organizers/tags?perPage=-1"
CREATE_RECIPE_PATH = "/api/recipes"
GET_RECIPE_PATH = "/api/recipes/{slug}"
PATCH_RECIPE_PATH = "/api/recipes/{slug}"
IMAGE_RECIPE_PATH = "/api/recipes/{slug}/image"


class APIController:
    def __init__(self):
        self.url = MEALIER_URL
        self.headers = {
            "Authorization": f"Bearer {MEALIER_API_KEY}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }

        self.miniature = None
        self.tags = self.retrieve_tags()
        self.categories = self.retrieve_categories()
        self.recipe = None
        self.slug = None
        self.source_url = None

    def retrieve_tags(self) -> list:
        response = requests.get(f"{self.url}{TAGS_PATH}", headers=self.headers)

        if response.status_code == 200:
            json_response = response.json()
            return json_response.get("items", [])

        else:
            raise Exception(f"Error ({response.status_code}): {response.text}")

    def set_miniature(self, miniature: str) -> None:
        self.miniature = miniature

    def set_source_url(self, source_url: str) -> None:
        self.source_url = source_url

    def get_tags(self) -> list:
        return self.tags

    def retrieve_categories(self) -> list:
        response = requests.get(f"{self.url}{CATEGORIES_PATH}", headers=self.headers)

        if response.status_code == 200:
            json_response = response.json()
            return json_response.get("items", [])

        else:
            raise Exception(f"Error ({response.status_code}): {response.text}")

    def get_recipe_url(self) -> str:
        return f"{self.url}/g/home/r/{self.slug}"

    def get_categories(self) -> list:
        return self.categories

    def create_recipe(self, name: str) -> str:
        payload = {
            "name": name
        }

        response = requests.post(f"{self.url}{CREATE_RECIPE_PATH}", json=payload, headers=self.headers)

        if response.status_code == 201 or response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error ({response.status_code}): {response.text}")

    def get_recipe(self) -> dict:
        response = requests.get(f"{self.url}{GET_RECIPE_PATH.format(slug=self.slug)}", headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error ({response.status_code}): {response.text}")

    def patch_recipe(self, slug: str, payload: dict) -> dict:
        json_payload = json.dumps(payload, ensure_ascii=False)

        response = requests.patch(f"{self.url}{PATCH_RECIPE_PATH.format(slug=slug)}", data=json_payload,
                                  headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error ({response.status_code}): {response.text}")

    def get_category_by_id(self, category_id: str) -> dict:
        for category in self.categories:
            if category.get("id") == category_id:
                return category
        return {}

    def get_tag_by_id(self, tag_id: str) -> dict:
        for tag in self.tags:
            if tag.get("id") == tag_id:
                return tag
        return {}

    def convert_to_mealier_format(self, payload: dict) -> None:

        self.recipe["orgURL"] = self.source_url

        recipe_categories = payload.get("recipeCategory", [])

        recipe_categories.extend([{"id": p} for p in MEALIER_DEFAULT_CATEGORIES_ID])

        for recipe_category in recipe_categories:
            c = self.get_category_by_id(recipe_category["id"])
            for key, value in c.items():
                recipe_category[key] = value

        tags = payload.get("tags", [])
        for tag in tags:
            t = self.get_tag_by_id(tag["id"])
            for key, value in t.items():
                tag[key] = value

        ingredients = payload.get("recipeIngredient", [])
        ingredients_dict = {}
        for ingredient in ingredients:
            uuid_value = str(uuid.uuid4())
            ingredients_dict[ingredient["referenceId"]] = uuid_value

            ingredient["quantity"] = 1
            ingredient["unit"] = None
            ingredient["food"] = None
            ingredient["isFood"] = False
            ingredient["disableAmount"] = True
            ingredient["display"] = ""
            ingredient["title"] = None
            ingredient["originalText"] = None
            ingredient["referenceId"] = uuid_value

        instructions = payload.get("recipeInstructions", [])
        for instruction in instructions:
            uuid_value = str(uuid.uuid4())

            instruction["id"] = uuid_value
            instruction["title"] = ""
            instruction["summary"] = ""

            ingredient_references = instruction.get("ingredientReferences", [])
            for reference in ingredient_references:
                reference["referenceId"] = ingredients_dict.get(reference["referenceId"])

        for key, value in payload.items():
            if key in self.recipe:
                self.recipe[key] = value

    def upload_image(self) -> dict:

        if self.miniature:
            file_path = self.miniature
            filename = os.path.basename(file_path)

            with open(file_path, "rb") as img_file:
                img_binary = img_file.read()

                headers = {
                    "Authorization": f"Bearer {MEALIER_API_KEY}",
                    "accept": "application/json"
                }

                files = {
                    "image": (filename, img_binary, 'image/png'),
                    "extension": (None, "png")
                }

                response = requests.put(f"{self.url}{IMAGE_RECIPE_PATH.format(slug=self.slug)}", headers=headers,
                                        files=files)

                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Error ({response.status_code}): {response.text}")
        else:
            return {}

    def run(self, name: str, payload: dict):
        self.slug = self.create_recipe(name)
        self.recipe = self.get_recipe()

        self.convert_to_mealier_format(payload)

        self.patch_recipe(self.slug, self.recipe)
        self.upload_image()
