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

# 바이트 시퀀스를 바이너리 파일로 변환하여 저장하는 함수
def save_byte_sequence_to_file(byte_sequence: str, file_path: str) -> None:
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
        os.makedirs(f'{dir}')

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
