#!/bin/bash

read -p "Enter a value: " input_value

zoxide_result=$(zoxide query "$input_value")

if [ $? -eq 0 ] && [ -n "$zoxide_result" ]; then
    zellij action new-tab --layout default --name "$input_value" --cwd "$zoxide_result"
else
    echo "Error: zoxide query failed or returned empty result."
    exit 1
fi
