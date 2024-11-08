import logging

import hvac

import load.context

from lib.vault import Vault


def load_secrets(project, vault_host, vault_port, auth, role, secrets_file, kvv2_mount_point):
  ''' load secrets from  Vault and write them to a file '''
  logging.debug(f'Loading secrets from {vault_host}:{vault_port} under {kvv2_mount_point}')

  path = f'kubernetes/apps/{project}/'
  vault_url = f'https://{vault_host}:{vault_port}'

  vault_client = Vault(
    vault_url,
    kvv2_mount_point=kvv2_mount_point,
    path=path,
  )

  if auth == 'iam':
    vault_client.iam_login(role)
  elif auth == 'kubernetes':
    role = project
    vault_client.kubernetes_login(role)

  keys = vault_client.list()['data']['keys']

  logging.debug(f'fetched keys from Vault: {keys}')

  with open(secrets_file, 'w') as f:
    for key in keys:
      try:
        value = vault_client.get(key)
        f.write(f"export {key}='{value}'\n")
      except hvac.exceptions.InvalidPath:
        logging.debug(f'{key} either does not exist or is soft deleted.')
