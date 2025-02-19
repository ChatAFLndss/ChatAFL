import os
import json

from typing import Optional, List
from pydantic import BaseModel
from openai import OpenAI
from utility.utility import MODEL, LLM_RETRY

PROTOCOL_TYPE_OUTPUT_DIR = "protocol_type_results"

class MessageType(BaseModel):
    name: str                               # Message type name (e.g., DISCONNECT, KEXINIT)
    description: str                        # Brief description of the message type

class ProtocolMessageTypes(BaseModel):
    protocol: str                           # Protocol name (e.g., SSH, HTTP)
    message_types: List[MessageType]        # List of all message types in the protocol
    references: Optional[List[str]] = None  # List of official documents or RFCs
    notes: Optional[str] = None             # Considerations for future extensibility or additional notes

PROTOCOL_TYPE_PROMPT = """\
You are a network protocol expert with deep understanding of [PROTOCOL]. Your task is to extract all defined client-to-server message types in the [PROTOCOL] protocol. For example, in the SSH protocol, client-to-server message types may include KEXINIT, SERVICE_REQUEST, USERAUTH_REQUEST, etc. It is critical that no valid client-to-server message type is omitted.

Please adhere to the following instructions:

1. **Identify All Client-to-Server Message Types:**
   - List every client-to-server message type defined in the [PROTOCOL] protocol exactly as specified in the official documentation, RFCs, or other verified sources.
   - Ensure that no valid client-to-server message type is missing from your answer.

2. **Source-Based and Accurate:**
   - Base your response strictly on reliable, official documentation or recognized sources.
   - Avoid any subjective interpretation or hallucinated information.

3. **Step-by-Step Reasoning:**
   - Provide a brief explanation of the process used to derive the list of client-to-server message types.
   - Indicate how you ensured the completeness and correctness of the list.

Please extract and list all client-to-server message types for [PROTOCOL] following the above constraints.
"""

def using_llm(prompt: str) -> ProtocolMessageTypes:
    client = OpenAI()
    try:
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format=ProtocolMessageTypes,
            timeout=15
        )
        response = completion.choices[0].message.parsed
        return response
    except Exception as e:
        print(f"Error processing protocol: {e}")
        return None

def get_protocol_message_types(protocol: str) -> dict:
    prompt = PROTOCOL_TYPE_PROMPT.replace("[PROTOCOL]", protocol)

    for _ in range(LLM_RETRY):
        response = using_llm(prompt)
        if response is not None:
            break

    if response is None:
        raise Exception(f"Failed to generate message types for {protocol}")

    # Save the individual protocol result to a JSON file
    os.makedirs(PROTOCOL_TYPE_OUTPUT_DIR, exist_ok=True)    
    protocol_file = os.path.join(PROTOCOL_TYPE_OUTPUT_DIR, f"{protocol.lower()}_types.json")
    with open(protocol_file, "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, indent=4, ensure_ascii=False)
    print(f"Saved results for {protocol} to {protocol_file}")

    return response.model_dump()
