from pydantic import BaseModel
from openai import OpenAI
from typing import List, Dict
from utility import utility
from enum import Enum

import os
import argparse
import json
from pprint import pprint
import collections
import random

global ARGS, PROTOCOL, INPUT, OUTPUT, FILE_PATH

MODEL = "gpt-4o-mini"
LLM_RETRY = 5
MODIFY_RETRY = 3
client = OpenAI()

## Class
# 필드 명을 추출하는데 사용하는 클래스
class FieldName(BaseModel):
    field_name: str
    description: str
class TextProtocolStructure(BaseModel):
    method: str
    field_name: List[FieldName]

# 필드 값을 추출하는데 사용하는 클래스
class FieldValue(BaseModel):
    field_name: str
    value: str
class RequestLine(BaseModel):
    method: str
    parameters: str
class TextProtocolMessage(BaseModel):
    method: str
    request_line: RequestLine
    field_value: List[FieldValue]
    # is_command_based: bool 의미 없음 구분 안됨 (RTSP/SMTP)

## 프로토콜 타입 리스트를 반환하는 함수
def get_protocol_types(protocol: str) -> List[str]:
    class ProtocolType(BaseModel):
        protocol_type_list: List[str]

    # Prompt
    """
    For the DICOM protocol, protocol client request message types include ['A-ASSOCIATE-RQ', 'C-ECHO-RQ', ...].
    For the {PROTOCOL} protocol, all protocol client request message types are:
    """
    prompt = f"For the DICOM protocol, protocol client request message types include "\
            f"[\'A-ASSOCIATE-RQ\', \'A-RELEASE-RQ\', \'C-ECHO-RQ\', \'C-ECHO-RSP\', ...]. "\
            f"For the {PROTOCOL} protocol, all protocol message types sent by client are:"

    temperature = 0.1
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature, # 0.1~0.3 사이로 하는 게 좋아보임
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=ProtocolType,
        timeout=15
    )
    # Parsing response
    response = completion.choices[0].message.parsed

    # Save result using utility function
    utility.save_and_log_result(
        file_path=FILE_PATH,
        model=MODEL,
        temperature=temperature,
        prompt=prompt,
        completion=completion,
        response=response
    )

    return response.protocol_type_list

## 메시지 타입 시퀀스를 반환하는 함수
def get_message_type_sequence(types):
    class MessageTypeSequence(BaseModel):
        message_type_sequence: List[str]
    class MessageTypeSequences(BaseModel):
        message_type_sequences: List[MessageTypeSequence]
    # Prompt
    """
    Given the {PROTOCOL} protocol with client request message types {TYPES},
    generate as many client request message type sequences as possible,
    combining 2 to 5 message types to maximize state coverage.
    """
    prompt = f"Given the {PROTOCOL} protocol with client request message types {types}, "\
            "generate as many client request message type sequences as possible, "\
            "combining 3 to 4 message types to maximize state coverage."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=MessageTypeSequences,
        timeout=30
    )
    response = completion.choices[0].message.parsed

    # Save result using utility function
    utility.save_and_log_result(
        file_path=FILE_PATH,
        model=MODEL,
        temperature=temperature,
        prompt=prompt,
        completion=completion,
        response=response
    )

    return [sequence.message_type_sequence for sequence in response.message_type_sequences]

## 프로토콜 타입 구조를 반환하는 함수
def get_protocol_structure(protocol: str, message_type: str):
    # Prompt
    """
    For the RTSP protocol, the DESCRIBE message type has the following structure:
    ```
    Method: "DESCRIBE"
    Field Name: ["CSeq", "Session", "Content-Type", "Content-Length", "User-Agent", "Accept", "Authorization", "Connection", "Referel", "Range", "Cache-Control"]
    ```
    ^^^^^^^^^^^^^^^^^^^^ 여긴 없어도 될 듯. ^^^^^^^^^^^^^^^^^^^^
    For the {PROTOCOL} protocol, the {message_type} message type's structure is:
    """
    prompt = f"For the {PROTOCOL} protocol, the {message_type} message type's structure is:"
            
    temperature = 0.1
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature, # 0.1~0.3 사이로 하는 게 좋아보임
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=TextProtocolStructure,
        timeout=15
    )
    # Parsing response
    response = completion.choices[0].message.parsed

    # Save result using utility function
    utility.save_and_log_result(
        file_path=FILE_PATH,
        model=MODEL,
        temperature=temperature,
        prompt=prompt,
        completion=completion,
        response=response
    )

    return response.method, response.field_name

def print_text_based_protocol_structure(protocol: str, method: str, field_name: List[FieldName]):
    print(f"\n[{protocol} - {method}]")
    print("-" * 50)
    for idx, field in enumerate(field_name, 1):
        print(f"{idx}. {field.field_name}: {field.description}")
    print("-" * 50)

def generate_protocol_message(protocol: str, method: str, message_description: str) -> TextProtocolMessage:
    # Prompt
    prompt = f"""For the {protocol} protocol, generate a realistic {method} message.
    The message structure is:
    {message_description}
    
    Generate a request line with method and parameters, and then generate values for each field.
    The response should include:
    1. A request line with the method and parameters
    2. Field values that follow the typical format and constraints"""

    temperature = 0.2
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=TextProtocolMessage,
        timeout=15
    )
    response = completion.choices[0].message.parsed

    # Save result using utility function
    utility.save_and_log_result(
        file_path=FILE_PATH,
        model=MODEL,
        temperature=temperature,
        prompt=prompt,
        completion=completion,
        response=response
    )

    return response

def to_str_protocol_message(message: TextProtocolMessage) -> str:
    message_str = f"{message.request_line.method} {message.request_line.parameters}"
    for field in message.field_value:
        message_str += f"\n{field.field_name}: {field.value}"
    return message_str

def main():
    global ARGS, PROTOCOL, INPUT, OUTPUT, FILE_PATH
    PROTOCOL = ARGS.protocol
    INPUT = ARGS.input
    OUTPUT= ARGS.output
    FILE_PATH = utility.get_output_path(PROTOCOL)
    
    ## Step 1
    # 프로토콜 타입 추출
    protocol_types = get_protocol_types(PROTOCOL)

    ## Step 2
    # 프로토콜 구조를 dictionary로 저장
    protocol_structure = {}
    for message_type in protocol_types:
        method, field_name = get_protocol_structure(PROTOCOL, message_type)
        # Dictionary에 저장: key는 method, value는 field_name list
        protocol_structure[method] = field_name
        
        # DEBUG
        print_text_based_protocol_structure(PROTOCOL, method, field_name)

    ## Step 3
    # 프로토콜 메시지 생성
    protocol_messages = {}
    for method, fields in protocol_structure.items():
        message_description = ""
        message_description += f"{method}:"
        for field in fields:
            message_description += f"\n  - {field.field_name}: {field.description}"
        protocol_messages[method] = generate_protocol_message(PROTOCOL, method, message_description)
        

        # DEBUG: Print generated message
        print(to_str_protocol_message(protocol_messages[method])+"\n")

    ## Step 4
    # 프로토콜 메시지 시퀀스 생성
    message_type_sequences = get_message_type_sequence(protocol_types)
    for sequence in message_type_sequences:
        print(sequence)
    
    ## Step 5
    # 프로토콜 메시지 시퀀스 저장
    for i in range(len(message_type_sequences)):
        file_path = utility.get_text_message_output_path(PROTOCOL, OUTPUT)
        message_sequence = []
        for method in message_type_sequences[i]:
            message_sequence.append(to_str_protocol_message(protocol_messages[method]))
        utility.save_text_message_sequence_to_file(message_sequence, file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=False, help='Input file')
    parser.add_argument('-p', '--protocol', required=True, help='Target Protocol')
    parser.add_argument('-o', '--output', required=False, default='results', help='Output Directory')
    ARGS = parser.parse_args()
    main()
