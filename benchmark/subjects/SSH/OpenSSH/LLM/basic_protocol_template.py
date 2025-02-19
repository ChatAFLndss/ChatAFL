import os
import json

from typing import Optional, List
from pydantic import BaseModel
from openai import OpenAI
from utility.utility import MODEL, LLM_RETRY

BASIC_PROTOCOL_TEMPLATE_OUTPUT_DIR = "basic_protocol_template_results"

# Structured output for the basic structural template of a protocol message
class FieldTemplate(BaseModel):
    name: str                                   # Field name (e.g., header, length, payload)
    function: str                               # Description of the function of the field
    fixed_length: Optional[int] = None          # Fixed byte length (integer value, None if variable)
    variable_conditions: Optional[str] = None   # Description of the conditions for the variable length

class ProtocolTemplate(BaseModel):
    protocol: str                               # Protocol name (e.g., SSH, SMTP)
    overall_outline: str                        # Overall outline of the message template
    fields: List[FieldTemplate]                 # List of fields that make up the protocol message
    references: Optional[List[str]] = None      # List of official documents or RFCs
    extensibility_points: Optional[str] = None  # Considerations for future extensibility

# Prompt for extracting the basic structural template of a protocol message
BASIC_PROTOCOL_TEMPLATE_PROMPT = """\
You are a network protocol expert with deep knowledge of both text-based and binary-based protocols, including [PROTOCOL]. Your task is to extract the basic structural template of a [PROTOCOL] message. Please follow these instructions:

1. **Identify the Basic Structure:**
   - List the main fields (e.g., header, length, payload, etc.) included in a [PROTOCOL] message.
   - For each field, explain its function and specify the fixed byte-length if applicable; if variable, describe the conditions that determine its size.

2. **Provide Accurate, Source-Based Information:**
   - Base your answer on official documentation, RFCs, or other reliable sources.
   - Ensure that your response avoids any subjective speculation or hallucinated details.

3. **Use a Step-by-Step Approach:**
   - Start with an overall outline of the message template, then provide detailed descriptions for each identified field.
   - Where applicable, include references or notes explaining how the information is derived from official sources.

4. **Consider Future Extensibility:**
   - Identify any points where the basic template might be expanded or modified, as this template will later be adapted for specific message types.
   
Please provide the extracted basic template for a [PROTOCOL] message.
"""

def using_llm(prompt: str) -> ProtocolTemplate:
    client = OpenAI()
    try:
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format=ProtocolTemplate,
            timeout=15
        )
        response = completion.choices[0].message.parsed
        return response
    except Exception as e:
        print(f"Error processing protocol: {e}")
        return None

def get_basic_protocol_template(protocol: str) -> dict:    
    prompt = BASIC_PROTOCOL_TEMPLATE_PROMPT.replace("[PROTOCOL]", protocol)

    for _ in range(LLM_RETRY):
        response = using_llm(prompt)
        if response is not None:
            break

    if response is None:
        raise Exception(f"Failed to generate basic template for {protocol}")

    # Save the individual protocol result to a JSON file
    os.makedirs(BASIC_PROTOCOL_TEMPLATE_OUTPUT_DIR, exist_ok=True)
    protocol_file = os.path.join(BASIC_PROTOCOL_TEMPLATE_OUTPUT_DIR, f"{protocol.lower()}_template.json")
    with open(protocol_file, "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, indent=4, ensure_ascii=False)
    print(f"Saved results for {protocol} to {protocol_file}")

    return response.model_dump()