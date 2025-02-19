import os
import json

from typing import Optional, List
from pydantic import BaseModel
from openai import OpenAI
from utility.utility import MODEL, LLM_RETRY

MESSAGE_SEQUENCE_OUTPUT_DIR = "message_sequence_results"

class MessageSequence(BaseModel):
    message_type: List[str]   # 예: "QUERY", "UPDATE", "NOTIFY", 등
    description: str    # 해당 메시지 시퀀스가 달성하는 state coverage에 대한 간략 설명

class MessageSequences(BaseModel):
    protocol: str                       # 프로토콜 이름 (예: "DNS")
    message_sequences: List[MessageSequence]  # 각 메시지 타입별 state coverage를 극대화하는 시퀀스 정보 목록
    references: Optional[List[str]] = None
    notes: Optional[str] = None


MESSAGE_PROMPT = """\
You are a network protocol expert tasked with generating message sequences to maximize state coverage for protocol fuzzing.
You are provided with an input list of protocol message types in JSON format.
Each message type in [TYPES.list] includes a "name" and a "description".
Your goal is to generate a sequence of message types for [PROTOCOL] such that the overall state coverage for the target protocol implementation is maximized.
Note that it is acceptable to use the same message type multiple times within the sequence if doing so contributes to covering different valid states.

Input JSON Type:
[TYPES.json]

Instructions:
1. **Utilize the Input:**
   - Use the provided input list [TYPES.list] of protocol message types. For each message type, refer to its "name" and "description" to guide the generation of the message sequence.
   - It is acceptable to use the same message type multiple times if it helps achieve unique valid states.

2. **Generate Message Sequences:**
   - Create a sequence of message types for [PROTOCOL] that maximizes state coverage for protocol fuzzing.
   - Ensure that each instance of a message type in the sequence contributes to testing a unique valid state.
   - Maintain all protocol requirements for each message type, even when repeated.

3. **Maximize State Coverage:**
   - Generate diverse sequences by varying the order and conditions under which each message type is used.
   - Avoid sequences where repeated message types do not add additional state coverage; each usage must test a distinct state.

4. **Internal Reasoning (Chain-of-Thought):**
   - Internally, use a chain-of-thought process to ensure that each instance of a message type is assigned unique field values or conditions that satisfy the protocol's requirements.

Please generate a message sequence (or sequences) for [PROTOCOL] using the input type list [TYPES.list] that maximizes state coverage.
"""

def using_llm(prompt: str) -> MessageSequences:
    client = OpenAI()
    try:
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format=MessageSequences,
            timeout=15
        )
        response = completion.choices[0].message.parsed
        return response
    except Exception as e:
        print(f"Error processing protocol: {e}")
        return None

def get_message_sequences(protocol: str, message_types: dict) -> dict:
    types_list = [type["name"] for type in message_types["message_types"]]
    prompt = MESSAGE_PROMPT.replace("[PROTOCOL]", protocol)\
                           .replace("[TYPES.list]", json.dumps(types_list))\
                           .replace("[TYPES.json]", json.dumps(message_types))

    for _ in range(LLM_RETRY):
        response = using_llm(prompt)
        if response is not None:
            break

    if response is None:
        raise Exception(f"Failed to generate message sequence for {protocol}")

    # Save the results to a JSON file
    os.makedirs(MESSAGE_SEQUENCE_OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(MESSAGE_SEQUENCE_OUTPUT_DIR, f"{protocol.lower()}_message_sequences.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, indent=4, ensure_ascii=False)    
    print(f"Saved results for {protocol} to {file_path}")

    return response.model_dump()
# … existing code …
