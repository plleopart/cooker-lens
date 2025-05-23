from telegram import Update

from app.ai.ai_client import AIClient
from app.api.api_controller import APIController
from app.garbage.garbage import Garbage
from app.media.media_processor import MediaProcessor
from app.downloader.media_downloader import MediaDownloader

import os

from app.config import TEMP_BASE_DIR, AI_CONFIDENCE_THRESHOLD, TELEGRAM_MASTER_ID


class MainController:

    def __init__(self, source_url, context, update: Update):
        self.source_url = source_url
        self.update = update
        self.context = context

        # Ensure the temporary directory exists
        if not os.path.exists(TEMP_BASE_DIR):
            os.makedirs(TEMP_BASE_DIR)

    async def run(self):
        user_full_name = self.update.message.from_user.full_name
        user_id = self.update.message.from_user.id
        try:
            print(f"[{user_full_name}] ▶️ Process started for URL: {self.source_url}")

            await self.update.message.reply_text("🔗 Starting process for the provided URL")

            downloader = MediaDownloader(self.source_url)
            await self.update.message.reply_text("📥 Downloading media from URL...")

            filename = downloader.download()
            description = downloader.get_description()

            print(f"[{user_full_name}] ✅ Media downloaded: {filename}")

            await self.update.message.reply_text(f"✅ Media downloaded", parse_mode="Markdown")

            await self.update.message.reply_text("🧠 Transcribing audio to text...")
            media_processor = MediaProcessor(filename)
            media_name = media_processor.get_media_name()
            transcript = media_processor.speech_to_text()
            print(f"[{user_full_name}] 🗣️ Transcription completed for: {media_name}")

            await self.update.message.reply_text("🖼️ Extracting frames from video...")
            images = media_processor.extract_frames()
            print(f"[{user_full_name}] 🎞️ Extracted {len(images)} frames")

            miniature = downloader.get_miniature()
            if miniature:
                images.append(miniature)
                print(f"[{user_full_name}] 🖼️ Miniature added to the list of images")
                await self.update.message.reply_text("🖼️ Miniature added to the list of images")

            api = APIController()
            api.set_source_url(self.source_url)

            tags = api.get_tags()
            categories = api.get_categories()

            await self.update.message.reply_text("🤖 Running AI analysis...")

            ai = AIClient(tags=tags, categories=categories, description=description, transcript=transcript,
                          images=images)
            ai.run()

            cost = ai.estimate_cost()
            metadata = ai.get_ai_metadata()
            api.set_miniature(ai.get_suggested_image())

            suggested_title = ai.get_suggested_title()
            ai_response = ai.get_ai_response()

            print(f"[{user_full_name}] 💡 Suggested title: {suggested_title}")
            print(f"[{user_full_name}] 💸 Estimated total cost: ${cost['total_cost_usd']}")
            print(f"[{user_full_name}] 📝 AI metadata: {metadata}")

            await self.update.message.reply_text(f"💡 Suggested Title: *{suggested_title}*", parse_mode="Markdown")
            cost_text = f"""💸 *Estimated AI Cost Breakdown:*

🧾 *Prompt tokens:* `{cost['prompt_tokens']}`
🧠 *Completion tokens:* `{cost['completion_tokens']}`
🧮 *Total tokens:* `{cost['total_tokens']}`

💰 *Input cost:* `${cost['input_cost_usd']}`
💬 *Output cost:* `${cost['output_cost_usd']}`
📊 *Total cost:* `${cost['total_cost_usd']}`
                    """

            await self.update.message.reply_text(
                cost_text,
                parse_mode="Markdown"
            )

            if TELEGRAM_MASTER_ID != 0 and str(user_id) != TELEGRAM_MASTER_ID:
                await self.context.bot.send_message(chat_id=TELEGRAM_MASTER_ID,
                                                    text=f"📩 Processed request from user {user_full_name} - {user_id}:\n\n")
                await self.context.bot.send_message(chat_id=TELEGRAM_MASTER_ID,
                                                    text=cost_text, parse_mode="Markdown")

            process_confidence = metadata.get("processConfidenceScore", "N/A")
            processing_notes = metadata.get("processingNotes", "No notes available.")
            title_meta = metadata.get("title", "No title provided.")

            metadata_message = (
                f"📝 *AI Metadata Summary:*\n\n"
                f"⭐ *Confidence Score:* `{process_confidence}`\n"
                f"🗒️ *Processing Notes:* {processing_notes}\n"
                f"🏷️ *Title from AI:* *{title_meta}*"
            )
            await self.update.message.reply_text(metadata_message, parse_mode="Markdown")

            if int(process_confidence) < int(AI_CONFIDENCE_THRESHOLD):
                await self.update.message.reply_text(
                    "⚠️ *Warning:* The AI confidence score is low. This video cannot be processed.",
                    parse_mode="Markdown"
                )
            else:
                print(f"[{user_full_name}] 🍽️ Creating recipe in Mealier...")
                await self.update.message.reply_text("🍽️ Creating recipe in Mealier...")

                api.run(suggested_title, ai_response)

                await self.update.message.reply_text("✅ Recipe created successfully!")

                recipe_url = api.get_recipe_url()
                await self.update.message.reply_text(f"🔗 Your recipe is ready: [View Recipe]({recipe_url})",
                                                     parse_mode="Markdown")

            print(f"[{user_full_name}] 🧹 Cleaning up temporary files: {media_name}")
            garbage = Garbage(media_name)
            garbage.clean()

        except Exception as e:
            print(f"[{user_full_name}] ❌ Error during process: {e}")
            await self.update.message.reply_text(
                "⚠️ Oops! Something went wrong during the process. Please try again later.\n\n"
                "📞 If the problem persists, contact support."
            )
