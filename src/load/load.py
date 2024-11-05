import argparse
import logging
import os

import load.context

from load.load import load_secrets
from lib.logging import setup_logging
from lib.validations import (
  hostname_agrees_with_environment
)


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    'auth',
    choices=['iam', 'kubernetes', 'token'],
    default='kubernetes',
    help='the method to use for authenticating with Vault (default: kubernetes)'
  )
  parser.add_argument(
    '--role',
    default=None,
    help='the Vault role to authenticate as (default: None)'
  )
  parser.add_argument(
    'env',
    choices=['staging', 'production'],
    help='the artsy environment of the Kubernetes cluster'
  )
  parser.add_argument(
    'project',
    help='artsy project name'
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='log level'
  )
  return parser.parse_args()

def parse_env():
  ''' parse env vars '''
  vault_host = os.environ.get('VAULT_HOST')
  vault_port = os.environ.get('VAULT_PORT')
  kvv2_mount_point = os.environ.get('VAULT_KVV2_MOUNT_POINT')
  secrets_file = os.environ.get('SECRETS_FILE', '')

  return vault_host, vault_port, kvv2_mount_point, secrets_file

def validate(env, vault_host, vault_port, secrets_file):
  ''' validate config obtained from env and command line '''
  if not (vault_host and vault_port and secrets_file):
    raise Exception(
      "The following environment variables must be specified: " +
      "VAULT_HOST, " +
      "VAULT_PORT, " +
      "SECRETS_FILE"
    )
  if not hostname_agrees_with_environment(vault_host, env):
    raise Exception(
      f'Hostname {vault_host} does not agree with environment {env}'
    )


if __name__ == "__main__":

  args = parse_args()
  auth, role, env, project, loglevel = (
    args.auth,
    args.role,
    args.env,
    args.project,
    args.loglevel,
  )

  setup_logging(eval('logging.' + loglevel))

  vault_host, vault_port, kvv2_mount_point, secrets_file = parse_env()

  validate(env, vault_host, vault_port, secrets_file)

  load_secrets(project, vault_host, vault_port, auth, role, secrets_file, kvv2_mount_point)
