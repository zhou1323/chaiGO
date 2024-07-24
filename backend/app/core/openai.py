from app.core.config import settings
from openai import OpenAI
import json

receipt_prompt = """
This is a credit card statement or a shopping receipt that contains a lot of transaction information for various items. I would like you to act as a secretary to organize and extract the details for me. I only need the JSON array representation of the receipt data.

The extracted information should be presented in text format that conforms to the following requirements:

[id: (string, unique), description: (string, overall description), date: (string, date), category: (string, category), amount: (number, total price), notes: (string, notes), fileName: (string, name of the uploaded file),
fileUrl: (string, URL of the uploaded file),
// items in details
[id: (string, unique), item: (string, name of the item), quantity: (number), unit: (string), unitPrice: (number, price per unit), discountPrice: (number, price per unit after discount), notes: (string, notes)]]

Note that the text 'description', 'date', etc. in the format is only to help you understand the source of the data, and the final output text does not need to contain these words. An example of extracted data is:
[
["1", "Shopping at Walmart", "2021-01-01", "Shopping", 100.0, "Grocery", "receipt1.jpg", "https://example.com/receipt1.jpg",
[
["1", "Apple", 2, "kg", 5.0, 4.0, "Fresh fruit"],
["2", "Banana", 3, "kg", 3.0, 2.5, "Fresh fruit"]
]
]
]

During the extraction process, the following requirements must be met:
1. If it is a credit card statement:
1.1. Each line is considered a receipt, and its Transaction Date is the date for the entire receipt.
1.2. These receipts won't have detailed items
1.3. When multiple currencies are present, the settlement currency or amount, which is CNY, should be considered.
2. If it is a shopping receipt:
2.1. Each line is a receipt item.
2.2. If there is a discount, the original price information should be stored as unitPrice, and the discounted information should be stored as discountPrice.
2.3. The default unit is "piece".
3. For information that cannot be extracted, default it to "" (empty string).
4. The value for category can be: groceries/transport/entertainment/health/clothing/education/other
5. If the text to be extracted is not in English, it should first be translated into English. All output text should be in English.
6. The extracted data should be in the form of a JSON array.

Note that the request is to directly return the translated English plain text with JSON array format, without needing to write code or elaborate on the implementation process. Just the plain text is enough.
"""

extract_receipt_function = {
    "name": "extract_receipt",
    "description": "Extract useful information from a credit card statement or a shopping receipt and organize it. The following requirements must be met: 1. If it is a credit card statement: 1.1. Each line is a receipt, and its Transaction Date is the date for the entire receipt. 1.2. Each line is also a receipt item for that receipt. 1.3. When multiple currencies are present, the settlement currency or amount, which is CNY, should be considered. 2. If it is a receipt: 2.1. Each line is a receipt item. 2.2. If there is a discount, the original price information should be stored as unitPrice, and the discounted information should be stored as discountPrice. 3. For information that cannot be extracted, default it to ''. 4. If the text to be extracted is not in English, it should first be translated into English. All output text should be in English.",
    "parameters": {
        "type": "object",
        "properties": {
            "receipts": {
                "type": "array",
                "description": "all receipts in the image",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "unique identifier"},
                        "description": {
                            "type": "string",
                            "description": "overall description",
                        },
                        "date": {"type": "string", "description": "date"},
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
                        "notes": {"type": "string", "description": "notes"},
                        "fileName": {
                            "type": "string",
                            "description": "name of the uploaded file",
                        },
                        "fileUrl": {
                            "type": "string",
                            "description": "URL of the uploaded file",
                        },
                        "details": {
                            "type": "array",
                            "description": "items in details",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
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
                                    "notes": {"type": "string", "description": "notes"},
                                },
                            },
                        },
                    },
                },
            }
        },
        "required": [],
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


openai_client = OpenaiClient()
