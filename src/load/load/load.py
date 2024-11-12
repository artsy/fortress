import logging

import hvac

import load.context

from lib.vault import Vault


def load_secrets(vault_args, project, sa_token_path, secrets_file):
  ''' load secrets from  Vault and write them to a file '''
  logging.debug(
    f'Loading secrets from {vault_args.host}:{vault_args.port} under {vault_args.kvv2_mount_point}'
  )

  path = f'kubernetes/apps/{project}/'
  vault_url = f'https://{vault_args.host}:{vault_args.port}'

  vault_client = Vault(
    vault_url,
    kvv2_mount_point=vault_args.kvv2_mount_point,
    path=path,
  )

  if vault_args.auth == 'iam':
    vault_client.iam_login(vault_args.role)
  elif vault_args.auth == 'kubernetes':
    role = project
    vault_client.kubernetes_login(role, sa_token_path)

  keys = vault_client.list()['data']['keys']

  logging.debug(f'fetched keys from Vault: {keys}')

  with open(secrets_file, 'w') as f:
    for key in keys:
      try:
        value = vault_client.get(key)
        f.write(f"export {key}='{value}'\n")
      except hvac.exceptions.InvalidPath:
        logging.debug(
          f'{key} either does not exist or is soft deleted.'
        )
