from pydantic import BaseModel
from openai import OpenAI
from typing import List
from utility import utility
from enum import Enum
from typing import Dict
from os import path

import argparse
import re

from pprint import pprint

global ARGS, PROTOCOL, INPUT, OUTPUT, FILE_PATH, VERBOSE

MODEL = "gpt-4o-mini"

client = OpenAI()

class Section(BaseModel):
    section_name: str
    byte_length: str
    subsection: List["Section"]

    def display_tree(self, indent: int = 0) -> str:
        # 기본 정보 출력
        tree_str = " " * indent + f"|-- {self.section_name} (Length: {self.byte_length})\n"
        # 하위 섹션이 있는 경우 재귀적으로 탐색
        for sub in self.subsection:
            tree_str += sub.display_tree(indent + 4)  # 들여쓰기 레벨 추가
        return tree_str
    
Section.model_rebuild() # This is required to enable recursive types

class ProtocolStructure(BaseModel):
    protocol_structure: Section

    def display_tree(self) -> str:
        return self.protocol_structure.display_tree()


## Helper Function
def section_to_dict(section: Section) -> Dict:
    # 현재 섹션을 'section_name': 'byte_sequence' 형식으로 변환
    section_dict = {section.section_name: section.byte_length}
    # 하위 섹션이 있을 경우 재귀적으로 변환 후 추가
    if section.subsection:
        section_dict["subsection"] = [section_to_dict(sub) for sub in section.subsection]
    return section_dict

def structure_to_json(structure: ProtocolStructure) -> Dict:
    # Message 객체의 protocol_structure를 JSON으로 변환
    return section_to_dict(structure.protocol_structure)


## LLM
# 프로토콜의 구조를 가져오는 함수
def get_protocol_structure_recursive(protocol: str) -> List[str]:
    # Prompt
    """
    For DICOM protocol, protocol message's structure is
    [("PDU Header", length=6 bytes, 
        subsection=[("PDU Type", length=1 byte),
                    ("Reserved", length=1 byte),
                    ("Length", length=4 bytes)]),
    ("PDU Data", length=variable,
        subsection=[("Data Elements", length=variable)])]
    For the {PROTOCOL} protocol, network protocol message's structure is: 
    """
    prompt = f"For DICOM protocol, protocol message's structure is "\
        "[(\"PDU Header\", length=6 bytes, subsection=[(\"PDU Type\", length=1 byte), (\"Reserved\", length=1 byte), (\"Length\", length=4 bytes)]), "\
        "(\"PDU Data\", length=variable, subsection=[(\"Data Elements\", length=variable)])]."\
        f"For the {PROTOCOL} protocol, protocol message's structure is: "

    temperature = 0.1
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature, # 0.1~0.3 사이로 하는 게 좋아보임
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=ProtocolStructure,
        timeout=15
    )
    response = completion.choices[0].message.parsed
    
    # Save result
    result = ""
    result += "============ Setup ============\n"
    result += f"Model:          {MODEL}\n"
    result += f"Temperature:    {temperature}\n"
    result += "============ Prompt ============\n"
    result += f"{prompt}\n"
    result += "============ Tokens ============\n"
    result += f"Total Tokens:       {completion.usage.total_tokens}\n"
    result += f"Prompt Tokens:      {completion.usage.prompt_tokens}\n"
    result += f"Completion Tokens:  {completion.usage.completion_tokens}\n"
    result += "============ Response ============\n"
    result += f"{response}\n"
    result += f"{response.protocol_structure.display_tree()}\n"

    utility.write_to_file(file_path=FILE_PATH, string=result)

    # DEBUG
    if VERBOSE:
        print(result)

    return structure_to_json(response)


# 프로토콜 메시지가 가질 수 있는 타입을 반환하는 함수
def get_protocol_types(protocol: str) -> List[str]:
    class ProtocolType(BaseModel):
        protocol_type_list: List[str]

    # Prompt
    """
    For the DICOM protocol, protocol message types include ['A-ASSOCIATE-RQ', 'C-ECHO-RQ', ...].
    For the {PROTOCOL} protocol, all protocol client request message types are:
    """
    prompt = f"For DICOM protocol, protocol message types include [\'A-ASSOCIATE-RQ\', \'C-ECHO-RQ\', ...]."\
            f"For {PROTOCOL} protocol, all protocol client request message types are:"

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

    # Save result
    result = ""
    result += "============ Setup ============\n"
    result += f"Model:          {MODEL}\n"
    result += f"Temperature:    {temperature}\n"
    result += "============ Prompt ============\n"
    result += f"{prompt}\n"
    result += "============ Tokens ============\n"
    result += f"Total Tokens:       {completion.usage.total_tokens}\n"
    result += f"Prompt Tokens:      {completion.usage.prompt_tokens}\n"
    result += f"Completion Tokens:  {completion.usage.completion_tokens}\n"
    result += "============ Response ============\n"
    result += f"{response}\n"

    utility.write_to_file(file_path=FILE_PATH, string=result)

    # DEBUG
    if VERBOSE:
        print(result)

    return response.protocol_type_list

def get_specified_protocol_structure(structure, type):
    # Prompt
    """
    For the {PROTOCOL} protocol, the base protocol message structure is {PROTOCOL STRUCTURE}.
    A specialized protocol message structure for the message type {TYPE} based on this structure with header is:
    """
    prompt = f"For the {PROTOCOL} protocol, the base protocol message structure is {structure}. "\
            f"A specialized protocol message structure for the message type {type} based on this structure is:"

    temperature = 0.1
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature, # 0.1~0.3 사이로 하는 게 좋아보임
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=ProtocolStructure,
        timeout=15
    )
    response = completion.choices[0].message.parsed

    # Save result
    result = ""
    result += "============ Setup ============\n"
    result += f"Model:          {MODEL}\n"
    result += f"Temperature:    {temperature}\n"
    result += "============ Prompt ============\n"
    result += f"{prompt}\n"
    result += "============ Tokens ============\n"
    result += f"Total Tokens:       {completion.usage.total_tokens}\n"
    result += f"Prompt Tokens:      {completion.usage.prompt_tokens}\n"
    result += f"Completion Tokens:  {completion.usage.completion_tokens}\n"
    result += "============ Response ============\n"
    result += f"{response}\n"
    result += f"{response.protocol_structure.display_tree()}\n"

    utility.write_to_file(file_path=FILE_PATH, string=result)

    # DEBUG
    if VERBOSE:
        print(result)

    return structure_to_json(response)

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

    # Save result
    result = ""
    result += "============ Setup ============\n"
    result += f"Model:          {MODEL}\n"
    result += f"Temperature:    {temperature}\n"
    result += "============ Prompt ============\n"
    result += f"{prompt}\n"
    result += "============ Tokens ============\n"
    result += f"Total Tokens:       {completion.usage.total_tokens}\n"
    result += f"Prompt Tokens:      {completion.usage.prompt_tokens}\n"
    result += f"Completion Tokens:  {completion.usage.completion_tokens}\n"
    result += "============ Response ============\n"
    result += f"{response}\n"

    utility.write_to_file(file_path=FILE_PATH, string=result)

    # DEBUG
    if VERBOSE:
        print(result)

    return [sequence.message_type_sequence for sequence in response.message_type_sequences]

def get_structured_message(structure, type):
    ## CLASS
    class Section(BaseModel):
        section_name: str
        byte_sequence: str
        subsection: List["Section"]

        def display_tree(self, indent: int = 0) -> str:
            # 기본 정보 출력
            tree_str = " " * indent + f"|-- {self.section_name} (Byte sequence: {self.byte_sequence})\n"
            # 하위 섹션이 있는 경우 재귀적으로 탐색
            for sub in self.subsection:
                tree_str += sub.display_tree(indent + 4)  # 들여쓰기 레벨 추가
            return tree_str
    
    Section.model_rebuild() # This is required to enable recursive types

    class Message(BaseModel):
        protocol_structure: Section

        def display_tree(self) -> str:
            return self.protocol_structure.display_tree()
    
    ## Helper Function
    def section_to_dict(section: Section) -> Dict:
        # 현재 섹션을 'section_name': 'byte_sequence' 형식으로 변환
        section_dict = {section.section_name: section.byte_sequence}
        # 하위 섹션이 있을 경우 재귀적으로 변환 후 추가
        if section.subsection:
            section_dict["subsection"] = [section_to_dict(sub) for sub in section.subsection]
        else:
            section_dict["subsection"] = []
        return section_dict

    def message_to_json(message: Message) -> Dict:
        # Message 객체의 protocol_structure를 JSON으로 변환
        return section_to_dict(message.protocol_structure)

    # Prompt
    """
    For {PROTOCOL} protocol, the message structure with the message type {type} is {structure}.
    Generate a {type} byte sequence message according to the structure.
    Format the byte sequence output as a string with hex bytes separated by spaces, in the format '00 01 ... fe fd'.
    Message's byte sequences are MUST reveal message type."
    """
    prompt = f"For {PROTOCOL} protocol, the message structure with the message type {type} is {structure}. "\
            f"Generate a {type} byte sequence message according to the structure. "\
            "Format the byte sequence output as a string with hex bytes separated by spaces, in the format '00 01 ... fe fd'. "
            # "Message's byte sequences are MUST reveal message type."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=Message,
        timeout=15
    )
    response = completion.choices[0].message.parsed

    # Save result
    result = ""
    result += "============ Setup ============\n"
    result += f"Model:          {MODEL}\n"
    result += f"Temperature:    {temperature}\n"
    result += "============ Prompt ============\n"
    result += f"{prompt}\n"
    result += "============ Tokens ============\n"
    result += f"Total Tokens:       {completion.usage.total_tokens}\n"
    result += f"Prompt Tokens:      {completion.usage.prompt_tokens}\n"
    result += f"Completion Tokens:  {completion.usage.completion_tokens}\n"
    result += "============ Response ============\n"
    result += f"{response}\n"

    utility.write_to_file(file_path=FILE_PATH, string=result)

    # DEBUG
    if VERBOSE:
        print(result)

    return message_to_json(response)

def get_modified_structured_message(message, structure, type):
    ## CLASS
    class Section(BaseModel):
        section_name: str
        byte_sequence: str
        subsection: List["Section"]

        def display_tree(self, indent: int = 0) -> str:
            # 기본 정보 출력
            tree_str = " " * indent + f"|-- {self.section_name} (Byte sequence: {self.byte_sequence})\n"
            # 하위 섹션이 있는 경우 재귀적으로 탐색
            for sub in self.subsection:
                tree_str += sub.display_tree(indent + 4)  # 들여쓰기 레벨 추가
            return tree_str
    
    Section.model_rebuild() # This is required to enable recursive types

    class Message(BaseModel):
        protocol_structure: Section

        def display_tree(self) -> str:
            return self.protocol_structure.display_tree()
    
    ## Helper Function
    def section_to_dict(section: Section) -> Dict:
        # 현재 섹션을 'section_name': 'byte_sequence' 형식으로 변환
        section_dict = {section.section_name: section.byte_sequence}
        # 하위 섹션이 있을 경우 재귀적으로 변환 후 추가
        if section.subsection:
            section_dict["subsection"] = [section_to_dict(sub) for sub in section.subsection]
        else:
            section_dict["subsection"] = []
        return section_dict

    def message_to_json(message: Message) -> Dict:
        # Message 객체의 protocol_structure를 JSON으로 변환
        return section_to_dict(message.protocol_structure)

    # Prompt
    """
    If the message {message} in the {PROTOCOL} protocol does not match the {type} format,
    please modify it to conform to the {type} structure.
    """
    prompt = f"```\n"\
            f"{message}\n"\
            f"```\n"\
            f"If the message byte sequence in the {PROTOCOL} protocol does not match the message type '{type}' format, especially type and length, "\
            f"please modify this message to conform th the {type} message format according to structure {structure}."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=Message,
        timeout=15
    )
    response = completion.choices[0].message.parsed

    # Save result
    result = ""
    result += "============ Setup ============\n"
    result += f"Model:          {MODEL}\n"
    result += f"Temperature:    {temperature}\n"
    result += "============ Prompt ============\n"
    result += f"{prompt}\n"
    result += "============ Tokens ============\n"
    result += f"Total Tokens:       {completion.usage.total_tokens}\n"
    result += f"Prompt Tokens:      {completion.usage.prompt_tokens}\n"
    result += f"Completion Tokens:  {completion.usage.completion_tokens}\n"
    result += "============ Response ============\n"
    result += f"{response}\n"

    utility.write_to_file(file_path=FILE_PATH, string=result)

    # DEBUG
    if VERBOSE:
        print(result)

    return message_to_json(response)

def main():
    global ARGS, PROTOCOL, INPUT, OUTPUT, FILE_PATH, VERBOSE
    PROTOCOL = ARGS.protocol
    INPUT = ARGS.input
    OUTPUT= ARGS.output
    FILE_PATH = utility.get_output_path(PROTOCOL)
    VERBOSE = ARGS.verbose
    
    # 프로토콜 구조 겟또다제
    protocol_structure = get_protocol_structure_recursive(PROTOCOL)

    # 프로토콜 타입 겟또다제
    protocol_types = get_protocol_types(PROTOCOL)
    protocol_type_sequences = get_message_type_sequence(protocol_types)
    
    specified_protocol_structures = {}
    protocol_structured_messages = {}
    idx = 0
    for type in protocol_types:
        ## DEBUG
        # if idx == 3:
        #     break
        # 구체화된 프로토콜 구조 겟또다제
        try:
            specified_protocol_structure = get_specified_protocol_structure(protocol_structure, type)
            specified_protocol_structures[type] = specified_protocol_structure
        except Exception as e:
            print(f"Error in get_specified_protocol_structure(): {e}")
        # 프로토콜 메시지 겟또다제
        try:
            protocol_structured_message = get_structured_message(specified_protocol_structure, type)
            protocol_structured_messages[type] = protocol_structured_message
        except Exception as e:
            print(f"Error in get_structured_message(): {e}")
        # 프로토콜 메시지 수정본 겟또다제
        try:
            protocol_modified_structured_message = get_modified_structured_message(utility.concatenate_values(protocol_structured_message), specified_protocol_structure, type)
            protocol_structured_messages[type] = protocol_modified_structured_message
        except Exception as e:
            print(f"Error in get_modified_structured_message(): {e}")
        idx += 1

    pprint(specified_protocol_structures)
    pprint(protocol_structured_messages)

    # 메시지 시퀀스에 따른 시드 입력 생성
    for type_sequence in protocol_type_sequences:
        byte_sequence = ""
        for type in type_sequence:
            if protocol_structured_messages.get(type) == None:
                break
            byte_sequence += utility.concatenate_values(protocol_structured_messages.get(type))
            byte_sequence += '\n'
        try:
            utility.save_byte_sequence_to_file(byte_sequence=byte_sequence, file_path=utility.get_byte_sequence_output_path(PROTOCOL))
        except Exception as e:
            print(f"Error in save_byte_sequence_to_file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=False, help='Input file')
    parser.add_argument('-p', '--protocol', required=True, help='Target Protocol')
    parser.add_argument('-o', '--output', required=False, help='Output Directory')
    parser.add_argument('-v', '--verbose', required=False, default=True, help='Verbose')
    ARGS = parser.parse_args()
    main()
