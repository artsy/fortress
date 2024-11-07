#!/bin/bash

# This assumes you have general prerequisites installed as by:
# https://github.com/artsy/potential/blob/main/scripts/setup

PROJECT="fortress"
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)
GREEN=$(tput setaf 2)
DEFAULT=$(tput sgr0)
PYTHON_VERSION="3.10.11"
set -e

if [[ "$SHELL" = *"bash"* ]]; then
  touch ~/.bashrc
  PROFILE="$HOME/.bashrc"
elif [[ "$SHELL" = *"zsh"* ]]; then
  PROFILE="$HOME/.zshrc"
fi

append_to_shell_profile() {
  local text="$1"
  echo "Adding line to profile ($PROFILE): $text"
  if ! grep -Fqs "$text" "$PROFILE"; then
    printf "\n%s\n" "$text" >> "$PROFILE"
  fi
}

if ! command -v jq >/dev/null; then
    brew install jq
fi

if ! command -v pyenv >/dev/null; then
  echo "Installing pyenv..."
  curl https://pyenv.run | bash
  append_to_shell_profile 'export PYENV_ROOT="$HOME/.pyenv"'
  append_to_shell_profile 'export PATH="$HOME/.pyenv/bin:$PATH"'
  append_to_shell_profile 'eval "$(pyenv init -)"'
  append_to_shell_profile 'eval "$(pyenv virtualenv-init -)"'
  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$HOME/.pyenv/bin:$PATH"
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"
fi

VERSIONS=$(pyenv versions)

if [[ ! $VERSIONS =~ "$PYTHON_VERSION" ]]; then
  echo "Installing python $PYTHON_VERSION..."
  eval "$(pyenv init -)"
  pyenv install -v $PYTHON_VERSION
fi

if [[ ! $VERSIONS =~ " $PROJECT" ]]; then
  echo "Initialising a $PROJECT virtualenv..."
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"
  pyenv virtualenv $PYTHON_VERSION "$PROJECT"
  pyenv local "$PROJECT"
fi

echo "Running $PROJECT virtualenv..."
pyenv local "$PROJECT"

eval "$(pyenv init -)"
echo "Installing Poetry..."
pip install poetry
echo "Running poetry install..."
poetry install
pyenv rehash

echo "Downloading .env.shared (project's local dev configuration common across developers)..."
aws s3 cp "s3://artsy-citadel/$PROJECT/.env.shared" ./

if [ ! -e ".env" ]; then
  echo "Initializing .env from .env.example (for any custom local dev configuration)..."
  cp .env.example .env
fi

echo "Configuring pre commit hook..."
pre-commit install

echo "Pyenv has been installed!"
echo "A pyenv virtualenv called '$PROJECT' has been created. It should run automatically when you are in the project directory."
echo "And we're all done!"
