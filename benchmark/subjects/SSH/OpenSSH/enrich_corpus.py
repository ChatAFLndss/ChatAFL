from pydantic import BaseModel
from openai import OpenAI
from typing import List
from utility import utility
from enum import Enum
from typing import Dict

import os
import argparse
import json

from pprint import pprint

global ARGS, PROTOCOL, INPUT, OUTPUT, FILE_PATH, VERBOSE

MODEL = "gpt-4o-mini"

client = OpenAI()

## Class
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

## CLASS
class BinarySection(BaseModel):
    section_name: str
    byte_sequence: str
    subsection: List["BinarySection"]

    def display_tree(self, indent: int = 0) -> str:
        # 기본 정보 출력
        tree_str = " " * indent + f"|-- {self.section_name} (Byte sequence: {self.byte_sequence})\n"
        # 하위 섹션이 있는 경우 재귀적으로 탐색
        for sub in self.subsection:
            tree_str += sub.display_tree(indent + 4)  # 들여쓰기 레벨 추가
        return tree_str
BinarySection.model_rebuild() # This is required to enable recursive types

class Message(BaseModel):
    protocol_structure: BinarySection
    def display_tree(self) -> str:
        return self.protocol_structure.display_tree()

## Helper Function
def structure_to_json(structure: ProtocolStructure) -> Dict:
    ## Helper Function
    def section_to_dict(section: Section) -> Dict:
        # 현재 섹션을 'section_name': 'byte_sequence' 형식으로 변환
        section_dict = {section.section_name: section.byte_length}
        # 하위 섹션이 있을 경우 재귀적으로 변환 후 추가
        if section.subsection:
            section_dict["subsection"] = [section_to_dict(sub) for sub in section.subsection]
        return section_dict

    # Message 객체의 protocol_structure를 JSON으로 변환
    return section_to_dict(structure.protocol_structure)

def message_to_json(message: Message) -> Dict:        
    ## Helper Function
    def section_to_dict(section: BinarySection) -> Dict:
        # 현재 섹션을 'section_name': 'byte_sequence' 형식으로 변환
        section_dict = {section.section_name: section.byte_sequence}
        # 하위 섹션이 있을 경우 재귀적으로 변환 후 추가
        if section.subsection:
            section_dict["subsection"] = [section_to_dict(sub) for sub in section.subsection]
        else:
            section_dict["subsection"] = []
        return section_dict
        
    # Message 객체의 protocol_structure를 JSON으로 변환
    return section_to_dict(message.protocol_structure)

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
    # Prompt
    """
    For {PROTOCOL} protocol, the message structure with the message type {type} is {structure}.
    Generate a {type} byte sequence message according to the structure.
    Format the byte sequence output as a string with hex bytes separated by spaces, in the format '00 01 ... fe fd'.
    Message's byte sequences are MUST reveal message type."
    """
    prompt = f"For the {PROTOCOL} protocol, the message structure with the message type {type} is as follows: {structure}. "\
            f"Generate a byte sequence message of type {type} according to this structure. "\
            "Format the byte sequence output as a string with hex bytes separated by spaces, in the format '00 01 ... fe fd'."
            # "Message's byte sequences are MUST reveal message type."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": f"You are an expert in communication protocols and data structures. "
                                            "Generate accurate and consistent byte sequence messages "
                                            "according to the given protocol and message structure. "
                                            "Base your answers solely on the provided information, "
                                            "and do not include additional assumptions or unnecessary details. "
                                            "Format the byte sequence output as per the instruction, "
                                            "displaying hex bytes separated by spaces, like '00 01 ... fe fd'."},
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
    # Prompt
    """
    If the message {message} in the {PROTOCOL} protocol does not match the {type} format,
    please modify it to conform to the {type} structure.
    """
    prompt = f"If the message {message} in the {PROTOCOL} protocol does not match the format for type '{type}', "\
            f"which is defined as {structure}, please modify or fix it to conform to the type {type} structure."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert in communication protocols and data formatting. "
                                            "When given a message and a protocol's message structure, "
                                            "accurately modify the message to conform to the specified format. "
                                            "Base your response solely on the provided information, "
                                            "without adding any assumptions or unnecessary details."},
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

def get_modified_structured_message_v2(message, structure, type):
    # Prompt
    """
    If the message {message} in the {PROTOCOL} protocol does not match the {type} format,
    please modify it to conform to the {type} structure.
    """
    prompt = f"```\n"\
            f"{message}"\
            f"```\n"\
            f"Given the structure of a specific protocol and byte sequences for each section, "\
            f"check if the message has any issues especially LENGTH SECTION with respect to the {type} with structure {structure}. "\
            f"If any issues are found, adjust the byte sequence to comply with the correct format and length for the {type} message."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": f"You are a protocol message validator and byte sequence modifier. "
                                        f"When given the structure of a specific protocol and byte sequences for each section, follow these guidelines: "
                                        f"1. Validation: Analyze the given byte sequences according to the expected structure and requirements of the specified {type} message, "
                                        f"with particular attention to length constraints and formatting rules. "
                                        f"2. Modification: If any issues are found—especially in length or format—modify the byte sequence to meet the protocol's requirements "
                                        f"for the {type} message. Ensure adjustments align with both the section's constraints and the overall protocol structure."
                                        f"3. Output: Return the adjusted byte sequence for each section, formatted to be compatible with the {type} message structure, "
                                        f"or indicate no changes were necessary if the initial byte sequence was already correct."},
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

def get_section_byte_sequence(section_name, bytes, type):
    class Section(BaseModel):
        byte_sequence: str

    # Prompt
    """
    특정 {PROTOCOL} 프로토콜의 {type} 메시지의 {section_name} section에 들어갈 수 있는 임의의 바이트 시퀀스를 생성하시오.
    만약 해당 섹션이 존재하지 않는다면 빈 문자열을 반환하시오.
    Generate a arbitrary/random {bytes} byte sequence for the {section_name} section of a {type} message in the {PROTOCOL} protocol.
    If the specified section does not exist, return an empty string.
    """
    prompt = f"Generate a proper {bytes} byte sequence for the '{section_name}' section of a {type} message in the {PROTOCOL} protocol. "\
            f"If the specified section does not exist, return an empty string. "\
            f"Format the byte sequence output as a string with hex bytes separated by spaces, in the format '00 01 ... fe fd'."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": f"You are a protocol message generator and validator for various binary-based protocols, including SSH and DTLS. "
                                            f"When generating byte sequences for a specified section of a message:\n"
                                            f"1. Identify the {section_name} section within the specified {type} message of the {PROTOCOL} protocol."
                                            f"2. If the section exists, produce a random byte sequence suitable for that section's expected data format."
                                            f"3. If the section does not exist, return an empty string."
                                            f"4. Ensure all generated byte sequences adhere to the protocol specifications for the given {type} message and {section_name} section."},
            {"role": "user", "content": prompt}
        ],
        response_format=Section,
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

    return response.byte_sequence

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
    # 프로토콜 타입 시퀀스 겟또다제
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
        # Case 1: 전체 메시지 한 번에 생성
        # try:
        #     protocol_structured_message = get_structured_message(specified_protocol_structure, type)
        #     protocol_structured_messages[type] = protocol_structured_message
        # except Exception as e:
        #     print(f"Error in get_structured_message(): {e}")
        # # 프로토콜 메시지 수정본 겟또다제
        # try:
        #     protocol_modified_structured_message = get_modified_structured_message(utility.concatenate_values(protocol_structured_message), specified_protocol_structure, type)
        #     protocol_structured_messages[type] = protocol_modified_structured_message
        # except Exception as e:
        #     print(f"Error in get_modified_structured_message(): {e}")
        ## Case 2: 섹션별 메시지 생성
        try:
            # 섹션별 메시지 생성 후 concatenate
            message = {}
            subsection = utility.extract_subsection_pairs(specified_protocol_structure)
            for data in subsection:
                byte_sequence = get_section_byte_sequence(section_name=data[0], bytes=data[1], type=type)
                message[data[0]] = utility.parse_to_byte_sequence(byte_sequence)
            json_message = json.dumps(message)
        except Exception as e:
            print(f"Error in get_section_byte_sequence: {e}")
        try:
            # 전체 메시지 시퀀스에 대해 길이 및 세부 사항에 대해서 수정
            protocol_structured_messages[type] = get_modified_structured_message_v2(message=json_message, structure=specified_protocol_structure, type=type)
        except Exception as e:
            print(f"Error in get_modified_structured_message_v2: {e}")
        idx += 1

    pprint(specified_protocol_structures)
    pprint(protocol_structured_messages)

    # 메시지 시퀀스에 따른 시드 입력 생성
    for type_sequence in protocol_type_sequences:
        output_path = utility.get_byte_sequence_output_path(PROTOCOL, OUTPUT)
        byte_sequence = ""
        for type in type_sequence:
            if protocol_structured_messages.get(type) == None:
                try:
                    print(f"Can't make new binary message sequences in {output_path}: No structured {type} type message.")
                    os.remove(output_path)
                except Exception as e:
                    print(f"{e}")
                break
            byte_sequence += utility.concatenate_values(protocol_structured_messages.get(type))
            ## Case 1. 각 메시지마다 줄바꿈을 하여 바이너리 파일로 저장
            try:
                utility.add_byte_sequence_to_file(byte_sequence=utility.concatenate_values(protocol_structured_messages.get(type)),
                                                  file_path=output_path)
            except Exception as e:
                print(f"Error in add_byte_sequence_to_file: {e}")

        ## Case 2. 각 메시지마다 줄바꿈 없이 그냥 일련의 바이너리 파일로 저장
        # try:
        #     utility.save_total_byte_sequence_to_file(byte_sequence=byte_sequence, file_path=output_path)
        # except Exception as e:
        #     print(f"Error in save_byte_sequence_to_file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=False, help='Input file')
    parser.add_argument('-p', '--protocol', required=True, help='Target Protocol')
    parser.add_argument('-o', '--output', required=False, default='results', help='Output Directory')
    parser.add_argument('-v', '--verbose', required=False, default=True, help='Verbose')
    ARGS = parser.parse_args()
    main()
