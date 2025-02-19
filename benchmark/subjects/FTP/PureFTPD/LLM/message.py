import os
import json

from typing import Optional, List
from pydantic import BaseModel
from openai import OpenAI
from utility.utility import MODEL, LLM_RETRY

MESSAGE_OUTPUT_DIR = "message_results"

class GeneratedField(BaseModel):
    name: str                         # 예: [STRUCTURE.specialized_structure.fields.name]
    value: Optional[str] = None       # 해당 필드의 생성된 값 (예: "Generated value for this field")
    is_binary: bool                   # 해당 필드가 이진 데이터인지 여부
    # children: Optional[List["GeneratedField"]] = None  # 재귀적 하위 필드

class GeneratedMessage(BaseModel):
    description: str                  # 메시지의 상태나 시나리오 설명
    payload: List[GeneratedField]     # 재귀적 구조의 최상위 필드 목록

class ProtocolGeneratedMessage(BaseModel):
    message_type: str                 # 예: [STRUCTURE.message_type]
    generated_message: List[GeneratedMessage]  # 생성된 메시지 구조

# GeneratedField.update_forward_refs()

MESSAGE_PROMPT = """\
You are a [PROTOCOL] network protocol expert tasked with generating valid messages for protocol fuzzing. Your goal is to generate a set of diverse, valid messages for a specific message type based on the provided specialized structure. Please strictly follow the instructions and constraints below:

1. **Utilize the Provided Structure:**
   - Base your message generation on the provided specialized structure details:
     - Message Type: [[STRUCTURE.message_type]]
     - Overall Outline: [[STRUCTURE.specialized_structure.overall_outline]]
     - Field Details:
       - Field Name: [[STRUCTURE.specialized_structure.fields.name]]
       - Field Function: [[STRUCTURE.specialized_structure.fields.function]]
       - Field Fixed Length: [[STRUCTURE.specialized_structure.fields.fixed_length]]
       - Field Variable Conditions: [[STRUCTURE.specialized_structure.fields.variable_conditions]]
   - Use these values exactly as provided to ensure consistency.

2. **Message Validity and Length Accuracy:**
   - Ensure that all fixed-length and variable-length fields are generated according to the specified byte sizes.
   - Critical fields such as length must accurately reflect the byte-size of their associated data.
   - For binary-based protocols, represent the message as a sequence of bytes in hex format seperated in spaces (e.g., "0x1a 0x00 0x00 0x00").
   - For text-based protocols, generate the message in plain ASCII text seperated in spaces or newlines according to the protocol specification (e.g., "GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/7.68.0\r\nAccept: application/json\r\n\r\n").

3. **State Coverage and Message Diversity:**
   - Generate multiple messages that collectively achieve high state coverage.
   - Ensure that no two messages represent the same state coverage; each message must be unique in its field values and conditions.
   - Vary the field values sufficiently to cover diverse valid states as defined by the provided structure.

4. **Structured Output Format:**
   - Format your final output as a JSON structure following this template:
    {
        "message_type": "[STRUCTURE.message_type]",
        "generated_message": {
            "description": "A brief description of the scenario or state covered by this message",
            "payload": [
                {
                    "name": "[STRUCTURE.specialized_structure.fields.name]",
                    "value": "Generated value for this field"
                }
                // Additional fields as specified by the structure
            ]
        }
    }

5. **Internal Reasoning (Chain-of-Thought):**
   - Internally, use a chain-of-thought reasoning process to ensure that each fixed and variable field is correctly generated and that the overall message is valid.
   - Do not include the internal reasoning in the final JSON output.

Please generate multiple valid messages for [STRUCTURE.message_type] based on the above requirements and constraints.
"""

def using_llm(prompt: str) -> ProtocolGeneratedMessage:
    client = OpenAI()
    try:
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format=ProtocolGeneratedMessage,
            timeout=90
        )
        response = completion.choices[0].message.parsed
        return response
    except Exception as e:
        print(f"Error processing protocol: {e}")
        return None

def get_message(protocol: str, specialized_structure: dict) -> None:
    fields_names = ", ".join([field["name"] for field in specialized_structure["specialized_structure"]["fields"]])
    fields_functions = ", ".join([field["function"] for field in specialized_structure["specialized_structure"]["fields"]])
    fields_fixed_lengths = ", ".join([str(field["fixed_length"]) for field in specialized_structure["specialized_structure"]["fields"]])
    fields_variable_conditions = ", ".join([str(field["variable_conditions"]) for field in specialized_structure["specialized_structure"]["fields"]])
    prompt = MESSAGE_PROMPT.replace("[PROTOCOL]", protocol)\
                           .replace("[STRUCTURE.message_type]", specialized_structure["message_type"])\
                           .replace("[STRUCTURE.specialized_structure.overall_outline]", specialized_structure["specialized_structure"]["overall_outline"])\
                           .replace("[STRUCTURE.specialized_structure.fields.name]", fields_names)\
                           .replace("[STRUCTURE.specialized_structure.fields.function]", fields_functions)\
                           .replace("[STRUCTURE.specialized_structure.fields.fixed_length]", fields_fixed_lengths)\
                           .replace("[STRUCTURE.specialized_structure.fields.variable_conditions]", fields_variable_conditions)

    for _ in range(LLM_RETRY):
        response = using_llm(prompt)
        if response is not None:
            break

    if response is None:
        raise Exception(f"Failed to generate message for {specialized_structure['message_type']} in {protocol}")

    return response.model_dump()

def get_messages(protocol: str, specialized_structure: dict) -> None:
    messages = {}

    for message_type in specialized_structure:
        try:
            print(f"Processing message type: {message_type}")
            messages[message_type] = get_message(protocol, specialized_structure[message_type])
        except Exception as e:
            print(f"Error processing message type {message_type} in {protocol}: {e}")
    
    # Save the results to a JSON file
    os.makedirs(MESSAGE_OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(MESSAGE_OUTPUT_DIR, f"{protocol.lower()}_messages.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)    
    print(f"Saved results for {protocol} to {file_path}")

    return messages
