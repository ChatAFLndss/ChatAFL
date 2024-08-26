from pydantic import BaseModel
from openai import OpenAI
import os
import argparse
import itertools

global ARGS

def check_for_other_file_path(target_file_path, other_file_path):
    target_directory = os.path.dirname(target_file_path)
    other_directory = os.path.dirname(other_file_path)
    
    if target_directory == other_directory:
        other_file_name = os.path.basename(other_file_path)
        
        files_in_directory = os.listdir(target_directory)
        
        if other_file_name in files_in_directory:
            return True
    
    return False

def read_file_as_hex_string(file_path):
    try:
        with open(file_path, 'rb') as file:
            byte_sequence = file.read()
            
            # 각 바이트를 16진수로 변환하여 C 스타일로 출력
            hex_output = " ".join(f"{byte:02x}" for byte in byte_sequence)
            
            # 출력
            return hex_output
    except Exception as e:
        print(f"An error occurred: {e}")

def save_byte_sequence_to_file(byte_sequence: str, file_path: str) -> None:
    """
    주어진 바이트 시퀀스 문자열을 바이너리 파일로 저장합니다.

    :param byte_sequence: 공백으로 구분된 16진수 바이트 시퀀스 문자열
    :param file_name: 저장할 바이너리 파일의 이름
    """
    # 공백을 기준으로 바이트 시퀀스를 분리하여 각 바이트를 16진수로 변환
    byte_values = bytearray(int(b, 16) for b in byte_sequence.split())

    # 바이너리 파일로 저장
    with open(file_path, "wb") as binary_file:
        binary_file.write(byte_values)

    print(f"{file_path} 파일로 저장되었습니다.")

def enrich_binary_sequence(file_path: str, protocol: str, model: str, temperature: float, type: tuple):
    client = OpenAI()
    class ByteSequenceString(BaseModel):
        client_request_byte_sequence_string: str
    
    hex_string = read_file_as_hex_string(file_path=file_path)
    
    prompt = "In the " + protocol + " protocol, following is one sequence of client requests:```" + hex_string + "```" +\
    "Please add the " + type[0] + ", " + type[1] + " client request in the proper locations, and the modified sequence of client requests is:"
    print("=============== prompt ================")
    print(prompt)

    completion = client.beta.chat.completions.parse(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=ByteSequenceString
    )
    print(completion)

    response = completion.choices[0].message.parsed
    print(response)
    
    idx = 0
    while (check_for_other_file_path(file_path, file_path.replace(".raw", "_enriched_"+str(idx)+".raw"))):
        idx += 1
    
    save_byte_sequence_to_file(byte_sequence=response.client_request_byte_sequence_string, file_path=file_path.replace(".raw", "_enriched_"+str(idx)+".raw"))
    # DEBUG
    # save_byte_sequence_to_file(byte_sequence="00 00 00 00 00", file_path=file_path.replace(".raw", "_enriched_"+str(idx)+".raw"))
    pass

def get_protocol_types(protocol: str, model: str, temperature: float):
    client = OpenAI()
    class ClientRequestMethod(BaseModel):
        client_request_method: str
    class ClientRequestMethods(BaseModel):
        client_request_methods: list[ClientRequestMethod]
    
    prompt = "\
            For the RTSP protocol, all of client request methods are DESCRIBE, OPTIONS, PAUSE, PLAY, SETUP, TEARDOWN, RECORD, SET_PARAMETER, ANNOUNCE, GET_PARAMETER.\\n\
            In the " + protocol + " protocol, get all of " + protocol +" client request method:"
    print(prompt)
    completion = client.beta.chat.completions.parse(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=ClientRequestMethods,
    )

    response = completion.choices[0].message.parsed
    types = []
    for method in response.client_request_methods:
        types.append(method.client_request_method)

    return types

def list_all_files(directory: str):
    all_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    
    return all_files

def main():
    global ARGS
    protocol = ARGS.protocol
    model = ARGS.model
    os.environ['OPENAI_API_KEY'] = ARGS.api_key
    inputs = ARGS.input_directory

    types:list = get_protocol_types(protocol=protocol, model=model, temperature=0.5)
    combination_length = int(ARGS.combination_length)
    combination = list(itertools.combinations(types, combination_length))
    print(combination)

    files = list_all_files(inputs)
    for file in files:
        if "enriched" not in file:
            for comb in combination:
                try:
                    enrich_binary_sequence(file_path=file, protocol=protocol, model=model, temperature=0.5, type=comb)
                except Exception as e:
                    print(f"ERRRROOORORRRORORRR...: {e}")

    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_directory', required=True, help='Input directory')
    parser.add_argument('-a', '--api_key', required=True, help='OpenAI API key')
    parser.add_argument('-m', '--model', required=True, help='Model')
    parser.add_argument('-p', '--protocol', required=True, help='Protocol Name')
    parser.add_argument('-c', '--combination_length', required=True, help='Combination length')
    ARGS = parser.parse_args()
    main()
