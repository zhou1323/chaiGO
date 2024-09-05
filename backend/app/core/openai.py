from datetime import datetime
from app.core.config import settings
from openai import OpenAI
import json

receipt_prompt = """
This is a credit card statement or a shopping receipt that contains a lot of transaction information for various items. I would like you to act as a secretary to organize and extract the details for me.

During the extraction process, the following requirements must be met:
1. Dates should be in the format YYYY-MM-DD.
2. For information that cannot be extracted, default it to "" (empty string).
3. If the text to be extracted is not in English, it MUST firstly be translated into English. All output text MUST be in English.
4. If it is a credit card statement: (1)Each line is considered a receipt, and its Transaction Date is the date for the entire receipt. (2)These receipts won't have detailed items. (3)When multiple currencies are present, the settlement currency or amount, which is CNY, should be considered.
5. If it is a shopping receipt: (1)Each line is a receipt item. (2)If there is a discount, unitPrice stores the original unit price, and discountPrice stores the discounted unit price. Discount price <= unit price. (3)The default unit is "piece". (4) The sum of the quantity of each product multiplied by the discounted unit price MUST be equal to the total price of the receipt.

"""

shopping_list_system_prompt = """

Here’s a simplified English translation while keeping the original meaning:

There are various discounted food items at different stores this week. I’d like you to act like a professional secretary and help me choose food that fits my needs while staying within my weekly budget, with the goal of saving as much as possible.

When planning, the following needs must be met:

I’m a single adult male living alone, and the food choices should support a healthy lifestyle. Suggested daily intake: salt <5g, oil 25-30g, dairy 300-500g, soy products 25-35g, animal protein 120-200g, seafood twice a week, no more than 1 egg per meal, vegetables 300-500g, fruit 200-350g, grains 200-300g, whole grains 50-150g, starchy foods 50-100g, water 1500-1700ml.
Consider the current day when planning meals from today to Sunday, specifying ingredients and portions for each meal. Don’t repeat the same dish two days in a row, and ensure variety. You don’t have to use up every ingredient in one meal; leftovers can be saved for other days. All purchased food should be consumed by the end of the week, with a maximum of 15 items in total.
The total cost must stay under my weekly budget, and aim to keep it as low as possible.
Consider value for money and try to buy the most cost-effective items.
If the budget allows, add some snacks to make the meals more enjoyable.
Try to buy everything from one store to save time.
You can complete this task in two steps: first, plan based on the discounts I provide to select the items that meet my needs; then, list the selected discount IDs and the quantities to purchase.
"""

shopping_list_user_prompt = """
Today is {weekday}, and below is this week’s budget and the discounts found:

Weekly Budget: {budget_string}

Offers: {offers_string}
"""

extract_receipt_function = {
    "name": "extract_receipt",
    "description": "Extract useful information from a credit card statement or a shopping receipt and organize it. The following requirements must be met: 1. If it is a credit card statement: 1.1. Each line is a receipt, and its Transaction Date is the date for the entire receipt. 1.2. Each line is also a receipt item for that receipt. 1.3. When multiple currencies are present, the settlement currency or amount, which is CNY, should be considered. 2. If it is a receipt: 2.1. Each line is a receipt item. 2.2. If there is a discount, the original price information should be stored as unitPrice, and the discounted information should be stored as discountPrice. 3. For information that cannot be extracted, default it to ''. 4. If the text to be extracted is not in English, it should first be translated into English. All output text should be in English.",
    "parameters": {
        "type": "object",
        "additionalProperties": False,
        "required": ["receipts"],
        "properties": {
            "receipts": {
                "type": "array",
                "description": "all receipts in the image",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "description",
                        "date",
                        "category",
                        "amount",
                        "notes",
                        "details",
                    ],
                    "properties": {
                        "id": {
                            "type": ["string", "null"],
                            "description": "unique identifier",
                        },
                        "description": {
                            "type": "string",
                            "description": "overall description",
                        },
                        "date": {
                            "type": "string",
                            "description": "date with format YYYY-MM-DD",
                        },
                        "category": {
                            "type": "string",
                            "enum": [
                                "groceries",
                                "transport",
                                "entertainment",
                                "health",
                                "clothing",
                                "education",
                                "other",
                            ],
                            "description": "category",
                        },
                        "amount": {"type": "number", "description": "total price"},
                        "notes": {"type": ["string", "null"], "description": "notes"},
                        # "fileName": {
                        #     "type": ["string", "null"],
                        #     "description": "name of the uploaded file",
                        # },
                        # "fileUrl": {
                        #     "type": ["string", "null"],
                        #     "description": "URL of the uploaded file",
                        # },
                        "details": {
                            "type": ["array", "null"],
                            "description": "items in details",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": [
                                    "id",
                                    "item",
                                    "quantity",
                                    "unit",
                                    "unitPrice",
                                    "discountPrice",
                                    "notes",
                                ],
                                "properties": {
                                    "id": {
                                        "type": ["string", "null"],
                                        "description": "unique identifier",
                                    },
                                    "item": {
                                        "type": "string",
                                        "description": "name of the item",
                                    },
                                    "quantity": {
                                        "type": "number",
                                        "description": "quantity",
                                    },
                                    "unit": {
                                        "type": "string",
                                        "description": "unit. Default value is 'piece'",
                                    },
                                    "unitPrice": {
                                        "type": "number",
                                        "description": "price per unit",
                                    },
                                    "discountPrice": {
                                        "type": "number",
                                        "description": "price per unit after discount",
                                    },
                                    "notes": {
                                        "type": ["string", "null"],
                                        "description": "notes",
                                    },
                                },
                            },
                        },
                    },
                },
            }
        },
    },
}

shopping_list_parameters = {
    "type": "object",
    "additionalProperties": False,
    "required": ["offers"],
    "properties": {
        "offers": {
            "type": "array",
            "description": "list of offers",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "quantity"],
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "unique identifier of the offer",
                    },
                    "quantity": {
                        "type": "number",
                        "description": "quantity of the some specific offer",
                    },
                },
            },
        }
    },
}


class OpenaiClient:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.OPENAI_KEY,
        )
        self.thread = self.client.beta.threads.create()

    def gpt_4o_analyse_image_with_completion(self, image_url: str):
        """
        Data format:
        - [id, description, date, category, amount, notes, fileName, fileUrl, details]
        - details: [id, item, quantity, unit, unitPrice, discountPrice, notes]
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": receipt_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                },
                            },
                        ],
                    },
                ],
                temperature=0.2,
                # Define the schema manually to adjust to function calling
                # otherwise, the schema can be generated from the model, e.g.:
                # response_format=Receipt
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "receipt_response",
                        "strict": True,
                        "schema": extract_receipt_function.get("parameters"),
                    },
                },
            )
            content = response.choices[0].message.content
            content = (
                content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
            )
            extracted_data = json.loads(content)
            return extracted_data
        except Exception as e:
            print("Unable to generate ChatCompletion response", e)
            return None

    # TODO: Don't support system message in Assistant API now.
    def gpt_4o_analyse_image_with_assistant(self, image_url: str):
        try:
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            )
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=None,  # TODO
                instructions="Extract information from English or swedish file and translate them into English.",
            )

            content = run.required_action.submit_tool_outputs.tool_calls[
                0
            ].function.arguments

            content = content.replace("```json\n", "").replace("\n```", "")
            extracted_data = json.loads(content)

            return extracted_data
        except Exception as e:
            print("Unable to generate response", e)
            return None

    def gpt_4o_generate_shopping_list_with_completion(
        self, budget_string: str, offers_string: str
    ):
        weekday = datetime.now().strftime("%A")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": shopping_list_system_prompt,
                    },
                    {
                        "role": "user",
                        "content": shopping_list_user_prompt.format(
                            weekday=weekday,
                            budget_string=budget_string,
                            offers_string=offers_string,
                        ),
                    },
                ],
                temperature=0.2,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "shopping_list_response",
                        "strict": True,
                        "schema": shopping_list_parameters,
                    },
                },
            )
            content = response.choices[0].message.content
            content = (
                content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
            )
            extracted_data = json.loads(content)
            return extracted_data
        except Exception as e:
            print("Unable to generate shopping list recommendation", e)
            return None


openai_client = OpenaiClient()
