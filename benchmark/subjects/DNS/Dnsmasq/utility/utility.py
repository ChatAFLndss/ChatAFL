import os
from typing import List, Dict
from pydantic import BaseModel

## UTILITY
# 파일을 바이트 시퀀스로 변환하여 반환하는 함수
def file_to_byte_sequence(file_path: str) -> str:
    '''
    :input: file path
    :output: byte sequence
    '''
    try:
        with open(file_path, 'rb') as file:
            byte_sequence = file.read()
            
            # 각 바이트를 16진수로 변환하여 바이트 시퀀스로 반환
            hex_output = " ".join(f"{byte:02x}" for byte in byte_sequence)
            return hex_output
    except Exception as e:
        print(f"An error occurred: {e}")

# 특정 파일에 바이트 시퀀스를 바이너리 데이터로 입력 후 줄바꿈을 하는 함수
def add_byte_sequence_to_file(byte_sequence: str, file_path: str) -> None:
    """
    :param byte_sequence: 공백으로 구분된 16진수 바이트 시퀀스 문자열
    :param file_name: 저장할 바이너리 파일의 이름
    """
    # 공백을 기준으로 바이트 시퀀스를 분리하여 각 바이트를 16진수로 변환
    byte_values = bytearray(int(b, 16) for b in byte_sequence.split())

    # 바이너리 파일로 저장
    with open(file_path, "ab") as binary_file:
        binary_file.write(byte_values)
        binary_file.write(b"\n")

# 바이트 시퀀스를 바이너리 파일로 변환하여 저장하는 함수
def save_total_byte_sequence_to_file(byte_sequence: str, file_path: str) -> None:
    """
    :param byte_sequence: 공백으로 구분된 16진수 바이트 시퀀스 문자열
    :param file_name: 저장할 바이너리 파일의 이름
    """
    # 공백을 기준으로 바이트 시퀀스를 분리하여 각 바이트를 16진수로 변환
    byte_values = bytearray(int(b, 16) for b in byte_sequence.split())

    # 바이너리 파일로 저장
    with open(file_path, "wb") as binary_file:
        binary_file.write(byte_values)

    print(f"{file_path} 파일로 저장되었습니다.")

# LLM 결과 저장 경로를 반환하는 함수
def get_output_path(protocol: str) -> str:
    number = 0
    if (not os.path.isdir('outputs')) or (not os.path.isdir(f'outputs/{protocol}')):
        os.makedirs(f'outputs/{protocol}')
    
    while True:
        output_dir = f"outputs/{protocol}/"
        file_name = f"{protocol}_output_{number}.txt"
        file_path = output_dir + file_name

        if os.path.exists(file_path):
            number += 1
        else:
            return file_path

# 새로 만든 시드 코퍼스 저장 경로를 반환하는 함수
def get_text_message_output_path(protocol: str, dir: str) -> str:
    number = 0
    if (not os.path.isdir(f'{dir}')):
        os.makedirs(f'{dir}/')

    while True:
        output_dir = f"{dir}/"
        file_name = f"new_{protocol}_message_sequence_{number}.raw"
        file_path = os.path.join(output_dir, file_name)

        if os.path.exists(file_path):
            number += 1
        else:
            return file_path

# 새로 만든 시드 코퍼스 저장 경로를 반환하는 함수
def get_byte_sequence_output_path(protocol: str, dir: str) -> str:
    number = 0
    if (not os.path.isdir(f'{dir}')):
        os.makedirs(f'{dir}/')

    while True:
        output_dir = f"{dir}/"
        file_name = f"new_{protocol}_input_{number}.raw"
        file_path = os.path.join(output_dir, file_name)

        if os.path.exists(file_path):
            number += 1
        else:
            return file_path

# 새로 만든 시드 코퍼스 저장 경로를 반환하는 함수
def get_byte_sequence_output_path_section(protocol: str, dir: str) -> str:
    number = 0
    if (not os.path.isdir(f'{dir}')):
        os.makedirs(f'{dir}/')

    while True:
        output_dir = f"{dir}/"
        file_name = f"new_{protocol}_input_section_{number}.raw"
        file_path = os.path.join(output_dir, file_name)

        if os.path.exists(file_path):
            number += 1
        else:
            return file_path

# 파일에 입력받은 문자열을 작성하는 함수
def write_to_file(file_path: str, string: str):
    with open(file_path, 'a') as file:
        file.write(string + "\n")

# 클래스의 바이트 시퀀스를 하나의 문자열로 만들어주는 함수
def concatenate_values(data):
    result = []
    
    def recurse(d):
        if 'subsection' in d and d['subsection']:
            for item in d['subsection']:
                recurse(item)
        elif 'subsection' in d and not d['subsection']:
            # Concatenate all other key values except 'subsection'
            for key, value in d.items():
                if key != 'subsection' and value:
                    # Split the value by spaces and extend the result list
                    result.extend(value.split())
    
    recurse(data)
    return ' '.join(result)

# Protocol structure에서 subsection 하위의 데이터를 tuple의 list로 만들어 반환하는 함수
def extract_subsection_pairs(data):
    result = []
    if isinstance(data, dict):
        if 'subsection' in data:
            # Ignore other keys at this level and process 'subsection'
            subsections = data['subsection']
            for subsection in subsections:
                result.extend(extract_subsection_pairs(subsection))
        else:
            # No 'subsection' at this level; collect key-value pairs
            for key, value in data.items():
                result.append((key, value))
    elif isinstance(data, list):
        # Process each item in the list
        for item in data:
            result.extend(extract_subsection_pairs(item))
    return result

# 특정 문자열이 byte sequence인지 확인하여 수정 및 그대로 반환하는 함수
def parse_to_byte_sequence(input_string: str) -> str:
    """
    :param input_string: 입력 문자열
    :return: 공백으로 구분된 바이트 시퀀스 문자열
    """
    try:
        # 공백으로 구분된 16진수 형태인지 확인 후 변환
        byte_values = [f"{int(b, 16):02x}" for b in input_string.split()]
    except ValueError:
        # 16진수 변환 실패 시 문자열을 UTF-8 바이트로 변환
        byte_values = [f"{ord(char):02x}" for char in input_string]

    # 공백으로 구분된 문자열로 반환
    return " ".join(byte_values)

# 중복되는 결과 저장 및 로깅을 처리하는 함수
def save_and_log_result(file_path: str, model: str, temperature: float, prompt: str, completion, response):
    """
    중복되는 결과 저장 및 로깅을 처리하는 함수

    :param file_path: 결과를 저장할 파일 경로
    :param model: 사용된 모델 이름
    :param temperature: 설정된 온도 값
    :param prompt: 사용된 프롬프트
    :param completion: API 응답 객체
    :param response: 파싱된 응답
    """
    result = ""
    result += "============ Setup ============\n"
    result += f"Model:          {model}\n"
    result += f"Temperature:    {temperature}\n"
    result += "============ Prompt ============\n"
    result += f"{prompt}\n"
    result += "============ Tokens ============\n"
    result += f"Total Tokens:       {completion.usage.total_tokens}\n"
    result += f"Prompt Tokens:      {completion.usage.prompt_tokens}\n"
    result += f"Completion Tokens:  {completion.usage.completion_tokens}\n"
    result += "============ Response ============\n"
    result += f"{response}\n"

    write_to_file(file_path=file_path, string=result)

    # DEBUG
    # print(result)

# LLM 테스트용 프롬프트
def test_llm(prompt, client):
    class Result(BaseModel):
        result: str
    temperature = 0.5
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=Result,
        timeout=15
    )
    response = completion.choices[0].message.parsed
    return response.result

def flatten_binary_sections(section: Dict) -> Dict[str, str]:
    """
    BinarySection 구조를 가진 dictionary를 입력으로 받아,
    subsection이 빈 리스트인 경우인 section_name을 key로,
    byte_sequence를 value로 하여 level이 없는 dictionary를 반환합니다.
    
    Args:
        section (Dict): BinarySection 구조를 가진 dictionary.
    
    Returns:
        Dict[str, str]: section_name을 key로, byte_sequence를 value로 하는 평탄화된 dictionary.
    """
    flat_dict = {}

    def recurse(current_section: Dict):
        # subsection이 비어있는 경우
        if not current_section.get('subsection'):
            section_name = current_section.get('section_name')
            byte_sequence = current_section.get('byte_sequence')
            if section_name and byte_sequence:
                flat_dict[section_name] = byte_sequence
        else:
            # 하위 섹션이 있는 경우 재귀적으로 탐색
            for sub in current_section.get('subsection', []):
                recurse(sub)
    
    recurse(section)
    return flat_dict

def concatenate_values_t2s(message_dict: Dict[str, str]) -> str:
    """
    딕셔너리를 입력받아 값들을 순차적으로 순회하며 각 값 사이에 공백을 추가하여 하나의 문자열로 연결합니다.

    Args:
        message_dict (Dict[str, str]): 섹션 이름을 키로 하고 바이트 시퀀스를 값으로 하는 딕셔너리.

    Returns:
        str: 모든 바이트 시퀀스가 공백으로 구분된 하나의 문자열.
    """
    return ' '.join(message_dict.values())

def save_text_message_sequence_to_file(message_sequence: List[str], file_path: str) -> None:
    with open(file_path, 'w') as file:
        for message in message_sequence:
            file.write(message + "\r\n")
