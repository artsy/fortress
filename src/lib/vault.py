import boto3
import hvac
import logging

from hvac.api.auth_methods import Kubernetes

from lib.export_backup import write_file


class Vault:
  ''' Interface with Hashicorp Vault '''
  def __init__(
    self,
    addr,
    auth_method,
    token=None,
    role=None,
    kvv2_mount_point=None,
    path=None,
    sanitizer=None
  ):
    self._client = hvac.Client(url=addr)
    self._mount_point = kvv2_mount_point
    self._path = path
    # a function for sanitizing a value before setting it in Vault
    # this is org-specific
    self._sanitizer = sanitizer
    self._login(auth_method, token, role)

  def _login(self, auth_method, token=None, role=None):
    ''' log into Vault using the specified method '''
    if auth_method == 'iam':
      self._iam_login(role)
    elif auth_method == 'token':
      self._client.token = token
    elif auth_method == 'kubernetes':
      self._kubernetes_login(role)
    else:
      raise Exception(f'Un-supported auth method: {auth_method}')

  def _kubernetes_login(self, role=None):
    ''' authenticate using k8s pod service account token '''
    with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as token_file:
      jwt = token_file.read()
    Kubernetes(self._client.adapter).login(role=role, jwt=jwt)

  def _iam_login(self, role=None):
    ''' log into Vault using AWS IAM keys '''
    session = boto3.Session()
    credentials = session.get_credentials()
    if role == None:
      # role not specified, let hvac default role to same as iam username
      self._client.auth.aws.iam_login(
        credentials.access_key,
        credentials.secret_key,
        credentials.token,
      )
    else:
      self._client.auth.aws.iam_login(
        credentials.access_key,
        credentials.secret_key,
        credentials.token,
        role=role
      )

  def get(self, key):
    ''' get an entry '''
    full_path = f'{self._path}{key}'
    logging.debug(f'Vault: getting {full_path}')
    # if key does not exist or if data is soft-deleted, it raises:
    # hvac.exceptions.InvalidPath
    response = self._client.secrets.kv.read_secret_version(
      path=full_path,
      mount_point=self._mount_point
    )
    # return value of key
    value = response['data']['data'][key]
    return value

  def list(self):
    ''' list keys under a path '''
    logging.debug(f'Vault: listing {self._path}')
    # list includes soft-deleted keys
    response = self._client.secrets.kv.v2.list_secrets(
      path=self._path,
      mount_point=self._mount_point
    )
    return response
