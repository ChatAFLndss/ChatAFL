import os
import json
import random

from pprint import pprint

MODEL = "gpt-4o-mini"
SEQUENCE_REPEAT = 10
LLM_RETRY = 3

def hex_to_binary(hex_string: str) -> str:
    """Convert hex string to binary string.
    
    Args:
        hex_string (str): Hex string in format like "0x12 0x34" or "12 34"
        
    Returns:
        str: Binary string (e.g. "00010010 00110100")
    """
    # Remove "0x" prefix and spaces
    hex_string = hex_string.replace("0x", "").replace(" ", "")
    
    # Convert each hex character to 4-bit binary string
    binary_string = ""
    for hex_char in hex_string:
        # Convert hex to int then to binary, remove "0b" prefix and pad to 4 bits
        binary = bin(int(hex_char, 16))[2:].zfill(4)
        binary_string += binary
        
    return binary_string

def get_message_random(message: dict) -> str:
    # Randomly select a message from the list of generated messages
    selected_message = random.choice(message["generated_message"])
    message = ""

    for field in selected_message["payload"]:
        if field["value"] is None:
            continue

        if field["is_binary"]:
            binary_string = hex_to_binary(field["value"])
            message += binary_string
        else:
            message += field["value"] + '\r\n'
    
    message += '\r\n'
    return message


def generate_test_cases(protocol: str, message_types: dict, _message_sequences: dict) -> None:
    message_sequences = {}
    idx = 1
    
    # 메시지 시퀀스 하나당 SEQUENCE_REPEAT 수만큼 메시지 생성
    for _ in range(SEQUENCE_REPEAT):
        for type_sequence in _message_sequences["message_sequences"]:
            message_sequence = ""

            for message_type in type_sequence["message_type"]:
                message = get_message_random(message_types[message_type])
                message_sequence += message

            message_sequences[idx] = message_sequence
            idx += 1

    pprint(message_sequences)
    return message_sequences
    

def save_test_cases(test_cases: dict, output_dir: str) -> None:
    """Save test cases to files.
    
    Args:
        test_cases (dict): Dictionary containing test messages
        output_dir (str): Directory to save the files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, message in test_cases.items():
        # Check if message contains only binary characters and \r\n
        is_binary = all(c in '01\r\n' for c in message)
        
        file_path = os.path.join(output_dir, f"new_{idx}.raw")
        
        if is_binary:
            # Convert binary string to bytes while preserving line breaks
            bytes_data = bytearray()
            current_byte = ""
            
            i = 0
            while i < len(message):
                if message[i:i+2] == '\r\n':
                    # If we have collected bits, convert them to a byte first
                    if current_byte:
                        bytes_data.append(int(current_byte.ljust(8, '0'), 2))
                        current_byte = ""
                    # Add \r\n as actual bytes
                    bytes_data.extend(b'\r\n')
                    i += 2
                else:
                    current_byte += message[i]
                    if len(current_byte) == 8:
                        bytes_data.append(int(current_byte, 2))
                        current_byte = ""
                    i += 1
            
            # Handle any remaining bits
            if current_byte:
                bytes_data.append(int(current_byte.ljust(8, '0'), 2))
            
            # Write binary data
            with open(file_path, 'wb') as f:
                f.write(bytes_data)
        else:
            # Write text data
            with open(file_path, 'w') as f:
                f.write(message)



