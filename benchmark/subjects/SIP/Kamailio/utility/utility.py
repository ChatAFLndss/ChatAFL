import os
import json
import random

from pprint import pprint

MODEL = "gpt-4o-mini"
SEQUENCE_REPEAT = 10
LLM_RETRY = 3

def hex_to_bytearray(hex_string: str) -> str:
    """Convert hex string to binary string.
    
    Args:
        hex_string (str): Hex string in format like "0x12 0x34" or "12 34"
        
    Returns:
        str: bytearray (e.g. "0x12 0x34" -> bytearray([0x12, 0x34]))
    """
    # Remove "0x" prefix and spaces
    hex_string = hex_string.replace("0x", "").replace(" ", "")
    if len(hex_string) % 2 == 1:
        hex_string = "0" + hex_string

    # Add spaces between each two characters
    hex_string = ' '.join(hex_string[i:i+2] for i in range(0, len(hex_string), 2))
    
    return bytearray.fromhex(hex_string)

def check_all_fields_non_binary(message_payload: dict) -> bool:
    """Check if all fields in the message payload are non-binary.
    
    Args:
        message (dict): Message dictionary containing payload fields
        
    Returns:
        bool: True if all fields are non-binary (is_binary=False), False otherwise
    """
    
    for field in message_payload:
        if field.get("is_binary", True):
            return False
            
    return True

def get_message_random(message: dict) -> bytearray:
    # Randomly select a message from the list of generated messages
    selected_message = random.choice(message["generated_message"])
    message = bytearray()

    is_text_based = check_all_fields_non_binary(selected_message["payload"])
    for field in selected_message["payload"]:
        if field["value"] is None:
            continue
        
        # All fields are non-binary (Text-based)
        if is_text_based:
            message.extend(field["value"].encode())
            message.extend(b'\r\n')
        else:
            # All fields are binary (Binary-based)            
            if field["is_binary"]:
                binary_string = hex_to_bytearray(field["value"])
                message.extend(binary_string)
            else:
                message.extend(field["value"].encode())
                message.extend(b' ')
    
    message.extend(b'\r\n')
    return message

def generate_test_cases(protocol: str, message_types: dict, _message_sequences: dict) -> None:
    message_sequences = {}
    idx = 1
    
    # 메시지 시퀀스 하나당 SEQUENCE_REPEAT 수만큼 메시지 생성
    for _ in range(SEQUENCE_REPEAT):
        for type_sequence in _message_sequences["message_sequences"]:
            message_sequence = bytearray()

            for message_type in type_sequence["message_type"]:
                message = get_message_random(message_types[message_type])
                message_sequence.extend(message)

            message_sequences[idx] = message_sequence
            idx += 1

    return message_sequences

def save_test_cases(test_cases: dict, output_dir: str) -> None:
    """Save test cases to files.
    
    Args:
        test_cases (dict): Dictionary containing test messages (bytearray)
        output_dir (str): Directory to save the files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, message in test_cases.items():
        file_path = os.path.join(output_dir, f"new_{idx}.raw")
        
        # Write binary data
        with open(file_path, 'wb') as f:
            f.write(message)
