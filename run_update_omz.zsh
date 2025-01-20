#!/usr/bin/env zsh

if [ -d ~/.oh-my-zsh/ ]; then
  source ~/.oh-my-zsh/oh-my-zsh.sh
  omz update
else
  echo "Installing Oh My Zsh"
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi
