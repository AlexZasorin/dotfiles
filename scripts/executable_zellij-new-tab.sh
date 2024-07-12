#!/usr/bin/env zsh

# set pane name
zellij action rename-pane "New Tab"

# prompt for a tab/dir name
print -nP "%B%F{blue}Name%f%b: %F{yellow}"
read "tab_name"
print -n "%f"

zoxide_result=$(zoxide query "$tab_name")

if [ $? -eq 0 ] && [ -n "$zoxide_result" ]; then
    zellij action new-tab --layout default --name "$tab_name" --cwd "$zoxide_result"
else
    zellij action new-tab --layout default --name "$tab_name"
fi
