#!/bin/bash

# Update the openAI key
for x in ChatAFL-BIN;
do
  sed -i "s/#define OPENAI_TOKEN \".*\"/#define OPENAI_TOKEN \"$KEY\"/" $x/chat-llm.h
done

