import os
import json

from typing import Optional, List
from pydantic import BaseModel
from openai import OpenAI
from utility.utility import MODEL, LLM_RETRY

PROTOCOL_SPECIALIZED_STRUCTURE_OUTPUT_DIR = "protocol_specialized_structure_results"

class SpecializedField(BaseModel):
    name: str                           # Field name (e.g., Header, Question Section, etc.)
    function: str                       # The role and description of the field, modified for the [TYPE] message
    fixed_length: Optional[int] = None  # The fixed byte length (if applicable)
    variable_conditions: Optional[str] = None  # The specialized variable conditions for the [TYPE]

class SpecializedStructure(BaseModel):
    overall_outline: str                # The overall outline reflecting [TYPE].description and the basic template ([TEMPLATE.overall_outline])
    fields: List[SpecializedField]      # The list of all fields included in the [TYPE] message type (the field name and function are modified based on [TEMPLATE.fields] information)
    additional_notes: Optional[str] = None  # The differences from the basic template or additional information

class ProtocolSpecializedStructure(BaseModel):
    protocol: str                       # The protocol name (e.g., DNS, SSH, etc.)
    message_type: str                   # The specific message type ([TYPE])
    specialized_structure: SpecializedStructure  # The specialized structure template
    references: Optional[List[str]] = None         # The list of official documents or RFCs

PROTOCOL_SPECIALIZED_STRUCTURE_PROMPT = """\
You are a network protocol expert with in-depth knowledge of [PROTOCOL]. You have already extracted a base protocol template for [PROTOCOL] which is provided as follows:
- Protocol: [TEMPLATE.protocol]
- Overall Outline: [TEMPLATE.overall_outline]
- Fields: [TEMPLATE.fields]

Your next task is to generate a specialized structure template for a specific message type, denoted as [TYPE.name]. The [TYPE.name] message is a client-to-server message whose characteristics are described as: [TYPE.description].

Please perform the following steps:

1. **Utilize the Base Template:**
   - Reference the base protocol template details ([TEMPLATE.protocol], [TEMPLATE.overall_outline], [TEMPLATE.fields] and their subfields) to guide the specialization process.
   - Modify, extend, or annotate the base fields as necessary to accurately represent the [TYPE.name] message type.

2. **Specialize the Template for [TYPE.name]:**
   - Clearly indicate any changes, additional fields, or constraints that are unique to the [TYPE.name] message.
   - Explain briefly how the [TYPE.description] influences these modifications.

3. **Source-Based and Accurate:**
   - Base your response on official documentation, RFCs, or other verified sources.
   - Ensure that your answer is complete, without omitting any necessary details, and avoid any subjective interpretation or hallucinated information.

Please extract and provide the specialized structure template for the [TYPE.name] message type for [PROTOCOL] following the above instructions.
"""

def using_llm(prompt: str) -> ProtocolSpecializedStructure:
    client = OpenAI()
    try:
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format=ProtocolSpecializedStructure,
            timeout=15
        )
        response = completion.choices[0].message.parsed
        return response
    except Exception as e:
        print(f"Error processing protocol: {e}")
        return None

def get_specialized_structure(protocol: str, base_template: dict, message_type: dict) -> None:
    prompt = PROTOCOL_SPECIALIZED_STRUCTURE_PROMPT.replace("[PROTOCOL]", protocol)\
                                                  .replace("[TYPE.name]", message_type["name"])\
                                                  .replace("[TYPE.description]", message_type["description"])\
                                                  .replace("[TEMPLATE.protocol]", base_template["protocol"])\
                                                  .replace("[TEMPLATE.overall_outline]", base_template["overall_outline"])\
                                                  .replace("[TEMPLATE.fields]", json.dumps(base_template["fields"]))
    
    for _ in range(LLM_RETRY):
        response = using_llm(prompt)
        if response is not None:
            break

    if response is None:
        raise Exception(f"Failed to generate specialized structure for {message_type['name']} in {protocol}")

    return response.model_dump()

def get_specialized_structures(protocol: str, base_template: dict, message_types: dict) -> None:
    structures = {}

    for message_type in message_types["message_types"]:
        try:
            structures[message_type["name"]] = get_specialized_structure(protocol, base_template, message_type)
        except Exception as e:
            print(f"Error processing message type {message_type['name']} in {protocol}: {e}")
    
    # Save the results to a JSON file
    os.makedirs(PROTOCOL_SPECIALIZED_STRUCTURE_OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(PROTOCOL_SPECIALIZED_STRUCTURE_OUTPUT_DIR, f"{protocol.lower()}_specialized_structures.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(structures, f, indent=4, ensure_ascii=False)    
    print(f"Saved results for {protocol} to {file_path}")

    return structures
