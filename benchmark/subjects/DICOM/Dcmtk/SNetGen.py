import os
import json
import argparse

from LLM.basic_protocol_template import get_basic_protocol_template
from LLM.protocol_types import get_protocol_message_types
from LLM.specialized_structures import get_specialized_structures
from LLM.message import get_messages
from LLM.message_sequence import get_message_sequences
from utility.utility import save_test_cases, generate_test_cases

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", "-p", type=str, required=True)
    parser.add_argument("--output_dir", "-o", type=str, required=False, default="results")
    args = parser.parse_args()

    protocol = args.protocol
    output_dir = args.output_dir

    try:
        # 1. Extract base template
        template: dict = get_basic_protocol_template(protocol)

        # 2. Extract message types
        message_types: dict = get_protocol_message_types(protocol)

        # 3. Extract specialized structure
        # template = json.load(open(f"protocol_template_results/{protocol}_template.json"))
        # message_types = json.load(open(f"protocol_type_results/{protocol}_types.json"))
        specialized_structures: dict = get_specialized_structures(protocol, template, message_types)

        # 4. Generate messages
        # specialized_structures = json.load(open(f"protocol_specialized_structure_results/dns_specialized_structures.json"))
        messages: dict = get_messages(protocol, specialized_structures)
        
        # 5. Generate message sequences
        # message_types = json.load(open(f"protocol_type_results/{protocol}_types.json"))
        message_sequences: dict = get_message_sequences(protocol, message_types)

        # 6. Generate test cases
        # messages: dict = json.load(open(f"message_results/{protocol}_messages.json"))
        # message_sequences: dict = json.load(open(f"message_sequence_results/{protocol}_message_sequences.json"))
        test_cases = generate_test_cases(protocol, messages, message_sequences)

        # 7. Save results
        save_test_cases(test_cases, output_dir)

    except Exception as e:
        print(f"Error processing protocol {protocol}: {e}")

if __name__ == "__main__":
    main()
