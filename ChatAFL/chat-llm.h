#ifndef __CHAT_LLM_H
#define __CHAT_LLM_H

#include "klist.h"
#include "kvec.h"
#include "khash.h"
#include <json-c/json.h>

/*
There are 2048 tokens available, around 270 are used for the initial data for the stall prompt
We give at most 400 for the examples and 1300 for the stall prompt
Similarly 1700 is for the example request in the seed enrichment
*/

#define OPENAI_TOKEN "1"

#define MAX_PROMPT_LENGTH 2048
#define EXAMPLES_PROMPT_LENGTH 400
#define HISTORY_PROMPT_LENGTH 1300
#define EXAMPLE_SEQUENCE_PROMPT_LENGTH 1700

#define TEMPLATE_CONSISTENCY_COUNT 5

// Maximum amount of retries for the state stall
#define STALL_RETRIES 2

// Maximum amount of tries to get the grammars
#define GRAMMAR_RETRIES 5

// Maximum amount
#define MESSAGE_TYPE_RETRIES 5

//Maximum amount of tries for an enrichment
#define ENRICHMENT_RETRIES 5

// Maximum number of messages to be added
#define MAX_ENRICHMENT_MESSAGE_TYPES 2

// Maximum number of messages to examine for addition
#define MAX_ENRICHMENT_CORPUS_SIZE 10

#define PCRE2_CODE_UNIT_WIDTH 8 // Characters are 8 bits
#include <pcre2.h>

// Init KLIST with JSON object
#define __grammar_t_free(x)
#define __rang_t_free(x)
#define __khash_t_free(x) 
KHASH_SET_INIT_STR(strSet);
KLIST_INIT(gram, json_object *, __grammar_t_free)
KLIST_INIT(rang, pcre2_code **, __rang_t_free)
typedef struct
{
    int start;
    int len;
    int mutable;
} range;

typedef kvec_t(range) range_list;
typedef kvec_t(khash_t(strSet)*) message_set_list;

// define one map to save pairs: {key: string, value: int}
KHASH_MAP_INIT_STR(strMap, int)
KHASH_MAP_INIT_STR(field_table, int);
KHASH_INIT(consistency_table, const char *, khash_t(field_table) *, 1, kh_str_hash_func, kh_str_hash_equal);

char *chat_with_llm(char *prompt, char *model, int tries, float temperature);
char *construct_prompt_for_templates(char *protocol_name, char **final_msg);
char *construct_prompt_for_remaining_templates(char *protocol_name, char *templates_prompt, char *templates_answer);
char *construct_prompt_for_protocol_message_types(char *protocol_name);
char *construct_prompt_for_requests_to_states(const char *protocol_name, const char *protocol_state, const char *example_requests);
char *construct_prompt_stall(char *protocol_name, char *examples, char *history);

void extract_message_grammars(char *answers, klist_t(gram) * grammar_set);
char *extract_message_pattern(const char *header_str,
                               khash_t(field_table) * field_table,
                               pcre2_code **patterns,
                               int debug_file,
                               const char *debug_file_name);
char *extract_stalled_message(char *message, size_t message_len);
char *format_request_message(char *message);


range_list starts_with(char *line, int length, pcre2_code *pattern);
range_list get_mutable_ranges(char *line, int length, int offset, pcre2_code *pattern);
void get_protocol_message_types(char *state_prompt, khash_t(strSet) * message_types);

char *enrich_sequence(char* sequence, khash_t(strSet) *missing_message_types);
khash_t(strSet)* duplicate_hash(khash_t(strSet)* set);
void write_new_seeds(char *enriched_file, char *contents);
char *unescape_string(const char *input);
char *format_string(char *state_string);
message_set_list message_combinations(khash_t(strSet)* sequence, int size);
#endif // __CHAT_LLM_H
