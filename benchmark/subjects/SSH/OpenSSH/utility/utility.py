import os

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
