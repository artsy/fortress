import argparse
import logging
import os

from dotenv import load_dotenv

import load.context

from load.load import load_secrets


ENV = os.environ.get('ENV')


def parse_args():
  ''' parse command line args '''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    'auth',
    choices=['iam', 'kubernetes'],
    help='the method to use for authenticating with Vault'
  )
  parser.add_argument(
    'env',
    choices=['staging', 'production'],
    help='the environment of the Kubernetes cluster'
  )
  parser.add_argument(
    'project',
    help='the name of the project to fetch secrets from  Vault for'
  )
  parser.add_argument(
    '--role',
    default=None,
    help='the Vault role to authenticate as'
  )
  parser.add_argument(
    '--sa-token-path',
    default='/var/run/secrets/kubernetes.io/serviceaccount/token',
    help='for Kubernetes auth, the file path to Kubernetes service account token inside the pod'
  )
  parser.add_argument(
    '--loglevel',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='INFO',
    help='logging level'
  )
  return parser.parse_args()

def parse_env():
  ''' parse env vars '''
  # load env files for local dev
  if ENV == 'development':
    load_dotenv('.env.shared')
    load_dotenv('.env', override=True)

  vault_host = os.environ.get('VAULT_HOST')
  vault_port = os.environ.get('VAULT_PORT')
  kvv2_mount_point = os.environ.get('VAULT_KVV2_MOUNT_POINT')
  secrets_file = os.environ.get('SECRETS_FILE', '')

  return vault_host, vault_port, kvv2_mount_point, secrets_file

def validate(vault_host, vault_port, secrets_file):
  ''' validate config obtained from env and command line '''
  if not (vault_host and vault_port and secrets_file):
    raise Exception(
      "The following environment variables must be specified: " +
      "VAULT_HOST, " +
      "VAULT_PORT, " +
      "SECRETS_FILE"
    )


if __name__ == "__main__":

  args = parse_args()
  auth, env, project, role, sa_token_path, loglevel = (
    args.auth,
    args.env,
    args.project,
    args.role,
    args.sa_token_path,
    args.loglevel,
  )

  logging.basicConfig(
    level=eval(f'logging.{loglevel}')
  )

  vault_host, vault_port, kvv2_mount_point, secrets_file = parse_env()

  validate(vault_host, vault_port, secrets_file)

  load_secrets(project, vault_host, vault_port, auth, role, sa_token_path, secrets_file, kvv2_mount_point)
