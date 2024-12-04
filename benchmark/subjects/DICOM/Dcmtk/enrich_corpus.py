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
class Section(BaseModel):
    section_name: str
    byte_length: str
    description: str
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

class BinarySection(BaseModel):
    section_name: str
    byte_length: str
    byte_sequence: str
    # description: str
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
        section_dict = {section.section_name: (section.byte_length, section.description)}
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
## 1. 프로토콜의 구조를 가져오는 함수
def get_protocol_structure_recursive(protocol: str, type: str) -> List[str]:
    # Prompt
    """
    For DICOM protocol, protocol message's structure is
    [("PDU Header", length=6 bytes, 
        subsection=[("PDU Type", length=1 byte),
                    ("Reserved", length=1 byte),
                    ("Length", length=4 bytes)]),
    ("PDU Data", length=variable,
        subsection=[("Data Elements", length=variable)])]
    For the {PROTOCOL} protocol, {type} protocol message's structure is: 
    """
    ## ORIGINAL
    prompt = f"For DICOM protocol, protocol message's structure is "\
        "[(\"PDU Header\", length=6 bytes, subsection=[(\"PDU Type\", length=1 byte), (\"Reserved\", length=1 byte), (\"Length\", length=4 bytes)]), "\
        "(\"PDU Data\", length=variable, subsection=[(\"Data Elements\", length=variable)])]. "\
        f"For the {protocol} protocol, {type} protocol message's structure is: "
    # prompt = f"For DICOM protocol, protocol message's structure is "\
    #     "[(\"PDU Header\", length=6 bytes, dependency_section=\"\", subsection=[(\"PDU Type\", length=1 byte, dependency_section=\"\"), (\"Reserved\", length=1 byte, dependency_section=\"\"), (\"Length\", length=4 bytes, dependency_section=\"PDU Data\")]), "\
    #     "(\"PDU Data\", length=variable, dependency_section=\"\", subsection=[(\"Data Elements\", length=variable, dependency_section=\"\")])]. "\
    #     f"For the {protocol} protocol, {type} protocol message's structure is: "

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
    
    # Save result using utility function
    utility.save_and_log_result(
        file_path=FILE_PATH,
        model=MODEL,
        temperature=temperature,
        prompt=prompt,
        completion=completion,
        response=response
    )
    print(response.display_tree())

    return structure_to_json(response)


## 2. 프로토콜 메시지가 가질 수 있는 타입을 반환하는 함수
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

## 4. 메시지 타입 시퀀스를 반환하는 함수
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

## 5-b. 특정 섹션에 들어갈 수 있는 임의의 바이트 시퀀스를 생성하는 함수
def get_section_byte_sequence(message, section_name, bytes, description, type):
    class Section(BaseModel):
        byte_sequence: str
        # description: str
    class CorrectSection(BaseModel):
        correct_byte_sequence: str
        # description: str
    # Prompt
    """
    현재까지 만들어진 {PROTOCOL}의 {type} 메시지는 다음과 같다.
    ```
    {message}
    ```
    여기서 {section_name}의 의미는 \"{description}\"이다.
    {bytes} 길이의 {section_name}의 바이트 시퀀스 데이터는 무엇인가?
    바이트 시퀀스는 16진수로 표현되어야 하며 공백으로 구분되어야 한다.
    """
    prompt = f"The following {type} messages of the {PROTOCOL} protocol have been created so far:\n"\
            f"```\n"\
            f"{message}\n"\
            f"```\n"\
            f"Here, the meaning of '{section_name}' is \"{description}\". "\
            f"What is the byte sequence data of '{section_name}' with a length of {bytes} bytes? "\
            f"The byte sequence should be represented in hexadecimal format, separated by spaces."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": f"You are an expert in binary protocols and data serialization. "\
                                            "Your task is to interpret the provided protocol details and generate precise byte sequence messages for the given sections of the protocol. "\
                                            "Ensure that all byte sequences strictly adhere to the protocol's specifications and are represented in hexadecimal format. "\
                                            "Each byte should be separated by a single space. Respond concisely and only with the required byte sequence unless additional clarification is requested."},
            {"role": "user", "content": prompt}
        ],
        response_format=Section,
        timeout=15
    )
    response = completion.choices[0].message.parsed
    message[section_name] = response.byte_sequence
    # Save result using utility function
    utility.save_and_log_result(
        file_path=FILE_PATH,
        model=MODEL,
        temperature=temperature,
        prompt=prompt,
        completion=completion,
        response=response
    )
    initial_response = response.byte_sequence

    # Prompt
    """
    Please verify the correctness of the following data for the {type} messages of the {PROTOCOL}:
    ```
    {message}
    ```
    In this context, {section_name} represents {description}.
    Is the byte sequence of {section_name} with {bytes} correct?
    If the sequence is incorrect, please provide the corrected byte sequence in hexadecimal format, separated by spaces.
    """
    prompt = f"Please verify the correctness of the following data for the {type} messages of the {PROTOCOL}:\n"\
            f"```\n"\
            f"{message}\n"\
            f"```\n"\
            f"In this context, {section_name} represents \"{description}\". "\
            f"Is the byte sequence of '{section_name}' with {bytes} correct? "\
            f"If the sequence is incorrect, please provide the corrected byte sequence in hexadecimal format, separated by spaces."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": f"You are an expert in verifying binary protocol data and ensuring compliance with protocol specifications. "\
                                        "Your role is to analyze the provided byte sequences against the described protocol details and verify their correctness. "\
                                        "If any discrepancies are found, provide the corrected byte sequence in hexadecimal format, ensuring each byte is separated by a single space. "\
                                        "Your responses should be precise and directly address the correctness of the byte sequence, including only necessary explanations or corrections as required."},
            {"role": "user", "content": prompt}
        ],
        response_format=CorrectSection,
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
    print(f"Initial response: {initial_response}")
    print(f"Corrected response: {response.correct_byte_sequence}")
    return response.correct_byte_sequence

## 6-b. 프로토콜 메시지 수정 함수 (section)
def get_modified_structured_message_v2(message, structure, type):
    class MessageIssues(BaseModel):
        is_issue: bool
        message_issues: List[str]

    class BinaryMessage(BaseModel):
        section_name: str
        byte_sequence: str

    class BinaryMessages(BaseModel):
        binary_messages: List[BinaryMessage]
    
    def binary_messages_to_dict(messages: List[BinaryMessage]) -> Dict[str, str]:
        """
        BinaryMessage 객체들의 리스트를 받아 section_name을 키로, byte_sequence를 값으로 하는 딕셔너리를 반환합니다.
        
        Args:
            messages (List[BinaryMessage]): 변환할 BinaryMessage 객체들의 리스트.
        
        Returns:
            Dict[str, str]: section_name을 키로 하고 byte_sequence를 값으로 하는 딕셔너리.
        """
        return {message.section_name: message.byte_sequence for message in messages}


    # Prompt
    """
    The following {type} messages of the {PROTOCOL} have been created so far:
    ```
    {message}
    ```
    프로토콜의 구조 {structure}에 따라 위의 메시지에 대하여 문제가 있다면 True를 반환하며 해당 key 값을 반환하라.
    """
    prompt = f"The following {type} message byte sequences of the {PROTOCOL} protocol have been created so far:\n"\
            f"```\n"\
            f"{message}\n"\
            f"```\n"\
            f"According to the structure of the protocol, "\
            f"return True if there is an issue with the above message and return the corresponding key with explanation."

    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": f"You are an expert in analyzing and validating binary protocol messages. Your role is to examine the provided byte sequence messages as a whole and identify any issues or inconsistencies based on the protocol's structure and specifications. "\
                                        "If an issue exists, return `True` along with the corresponding key and a concise explanation of the problem. If no issues are found, return `False`. "\
                                        "Ensure your analysis is accurate and adheres strictly to the protocol's defined rules."},
            {"role": "user", "content": prompt}
        ],
        response_format=MessageIssues,
        timeout=15
    )
    response = completion.choices[0].message.parsed
    message_issues = response.message_issues
    # Save result using utility function
    utility.save_and_log_result(
        file_path=FILE_PATH,
        model=MODEL,
        temperature=temperature,
        prompt=prompt,
        completion=completion,
        response=response
    )

    # 문제가 있는 경우 수정
    if response.is_issue:
        # Prompt
        """
        The following {type} messages of the {PROTOCOL} have been created so far:
        ```
        {message}
        ```
        위 메시지의 {message_issues} 섹션에 대하여 알맞게 수정하시오. 수정한 메시지는 유효한 데이터를 가지고 있어야 한다.
        """
        prompt = f"The following {type} message byte sequences of the {PROTOCOL} protocol have been created so far:\n"\
                f"```\n"\
                f"{message}\n"\
                f"```\n"\
                f"Please appropriately modify the {message_issues} issues of the above message. "\
                f"The modified message should contain valid data. "\
                f"The byte sequence should be in hexadecimal format, separated by spaces."

        temperature = 0.5
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            temperature=temperature,
            messages=[
                {"role": "system", "content": f"You are an expert in binary protocol message construction and repair. Your task is to analyze the provided byte sequence messages, identify the specified issues, and modify the message appropriately to ensure it adheres to the protocol's specifications. "\
                                            "The corrected message must contain valid data and be represented in hexadecimal format, with each byte separated by a single space. "\
                                            "Provide a response that is accurate and strictly addresses the identified issues while maintaining the protocol's integrity."},
                {"role": "user", "content": prompt}
            ],
            response_format=BinaryMessages,
            timeout=15
        )
        response = completion.choices[0].message.parsed
    else:
        return False, message

    # Save result using utility function
    utility.save_and_log_result(
        file_path=FILE_PATH,
        model=MODEL,
        temperature=temperature,
        prompt=prompt,
        completion=completion,
        response=response
    )
    print(f"Message issues: {message_issues}")
    return True, binary_messages_to_dict(response.binary_messages)

def to_protocol_structure(structure: str, message: str) -> List[str]:
    # Prompt
    """
    """
    prompt = f"For {PROTOCOL} protocol, protocol message's structure is {structure}. "\
            f"Parse the following message into the protocol structure: {message}. "\
            f"The byte sequence should be in hexadecimal format, separated by spaces."
            
    temperature = 0.1
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=temperature, # 0.1~0.3 사이로 하는 게 좋아보임
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=Message,
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
    print(response.display_tree())

    return message_to_json(response)

def main():
    global ARGS, PROTOCOL, INPUT, OUTPUT, FILE_PATH
    PROTOCOL = ARGS.protocol
    INPUT = ARGS.input
    OUTPUT= ARGS.output
    FILE_PATH = utility.get_output_path(PROTOCOL)
    
    # 프로토콜 타입 겟또다제
    protocol_types = get_protocol_types(PROTOCOL)
    # 프로토콜 구조 겟또다제
    # protocol_structure = get_protocol_structure_recursive(PROTOCOL)
    
    specified_protocol_structures = {}
    protocol_structured_messages = {}
    idx = 0
    for protocol_type in protocol_types:
        ## DEBUG
        # if idx == 1:
        #     break
        # 구체화된 프로토콜 구조 겟또다제
        try:
            specified_protocol_structure = get_protocol_structure_recursive(protocol=PROTOCOL, type=protocol_type)
            specified_protocol_structures[protocol_type] = specified_protocol_structure
        except Exception as e:
            print(f"Error in get_specified_protocol_structure(): {e}")
    # pprint(specified_protocol_structures)
    # exit()
    # # debug 아래 for 지워야함.
    # for protocol_type in specified_protocol_structures:
        ## Case 2: 섹션별 메시지 생성
        try:
            # 섹션별 메시지 생성 후 concatenate
            message = {}
            subsection = utility.extract_subsection_pairs(specified_protocol_structure)
            print(subsection)
            for data in subsection:
                message[data[0]] = data[1][0]
            pprint(message)
            for data in reversed(subsection):
                byte_sequences = [
                    get_section_byte_sequence(
                        message=message,
                        section_name=data[0],
                        bytes=data[1][0],
                        description=data[1][1],
                        type=protocol_type
                    )
                    for _ in range(LLM_RETRY)
                ]
                
                # 유효한 바이트 시퀀스만 필터링
                byte_sequences = [bs for bs in byte_sequences if bs]
                
                if not byte_sequences:
                    selected_byte_sequence = ""
                else:
                    counter = collections.Counter(byte_sequences)
                    max_count = max(counter.values())
                    most_common = [seq for seq, count in counter.items() if count == max_count]
                    selected_byte_sequence = random.choice(most_common)
                
                message[data[0]] = utility.parse_to_byte_sequence(selected_byte_sequence)
            json_message = json.dumps(message)
            pprint(json_message)
        except Exception as e:
            print(f"Error in get_section_byte_sequence: {e}")
        try:
            # 전체 메시지 시퀀스에 대해 길이 및 세부 사항에 대해서 수정
            is_issue, protocol_structured_messages[protocol_type] = get_modified_structured_message_v2(
                                                                        message=json_message,
                                                                        structure=specified_protocol_structure,
                                                                        type=protocol_type
            )
            repeat = 1
            while is_issue and repeat < MODIFY_RETRY:
                is_issue, protocol_structured_messages[protocol_type] = get_modified_structured_message_v2(
                    message=protocol_structured_messages[protocol_type],
                    structure=specified_protocol_structure,
                    type=protocol_type
                )
                repeat += 1
        except Exception as e:
            print(f"Error in get_modified_structured_message_v2: {e}")
        idx += 1

    pprint(specified_protocol_structures)
    pprint(protocol_structured_messages)

    ## 프로토콜 구조 정상화
    for type in protocol_types:
        print(f"{type}: {protocol_structured_messages.get(type)}")
        if protocol_structured_messages.get(type) != None:
            protocol_structured_messages[type] = to_protocol_structure(specified_protocol_structures[type], protocol_structured_messages[type])
    pprint(protocol_structured_messages)

    # 프로토콜 타입 시퀀스 겟또다제
    protocol_type_sequences = get_message_type_sequence(protocol_types)
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
            try:
                utility.add_byte_sequence_to_file(byte_sequence=utility.concatenate_values(protocol_structured_messages.get(type)),
                                                  file_path=output_path)
            except Exception as e:
                print(f"Error in add_byte_sequence_to_file: {e}")
        print(f"Generated {output_path}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=False, help='Input file')
    parser.add_argument('-p', '--protocol', required=True, help='Target Protocol')
    parser.add_argument('-o', '--output', required=False, default='results', help='Output Directory')
    ARGS = parser.parse_args()
    main()
