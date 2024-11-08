import os
import pytest

import lib.vault
from lib.vault import Vault


def describe_vault():
  def describe_init():
    def it_instantiates(mocker):
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault(
        addr='foourl',
        kvv2_mount_point='foomountpoint',
        path='foopath'
      )
      assert obj._client is lib.vault.hvac.Client()
      assert obj._mount_point == 'foomountpoint'
      assert obj._path == 'foopath'

  def describe_iam_login():
    def it_calls_iam_login(mocker):
      mocker.patch('lib.vault.hvac.Client')
      mocker.patch('lib.vault.boto3')
      obj = Vault(
        addr='foourl',
        kvv2_mount_point='foomountpoint',
        path='foopath'
      )
      spy = mocker.spy(obj._client.auth.aws, 'iam_login')
      obj.iam_login(role='foorole')
      spy.assert_called_once_with(
        lib.vault.boto3.Session().get_credentials().access_key,
        lib.vault.boto3.Session().get_credentials().secret_key,
        lib.vault.boto3.Session().get_credentials().token,
        role='foorole'
      )

  def describe_kubernetes_login():
    def it_raises_when_role_is_none(mocker):
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault(
        addr='foourl',
        kvv2_mount_point='foomountpoint',
        path='foopath'
      )
      with pytest.raises(Exception):
        obj.kubernetes_login()
    def it_calls_kubernetes_login_when_role_is_defined(mocker, tmp_path):
      mocker.patch('lib.vault.hvac.Client')
      kobj = mocker.patch('lib.vault.Kubernetes')
      obj = Vault(
        addr='foourl',
        kvv2_mount_point='foomountpoint',
        path='foopath'
      )
      sa_token_path = os.path.join(tmp_path, 'token.txt')
      with open(sa_token_path, 'w') as f:
        f.write('footoken')
      spy = mocker.spy(lib.vault.Kubernetes(), 'login')
      obj.kubernetes_login('foorole', sa_token_path)
      spy.assert_called_once_with(
        role='foorole',
        jwt='footoken'
      )

  def describe_get():
    def it_gets(mocker):
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault(
        addr='foourl',
        kvv2_mount_point='foomountpoint',
        path='foopath'
      )
      spy = mocker.spy(obj._client.secrets.kv, 'read_secret_version')
      assert obj.get('fookey') == lib.vault.hvac.Client().secrets.kv.read_secret_version()['data']['data']['key']
      spy.assert_has_calls([
        mocker.call(
          path='foopathfookey',
          mount_point='foomountpoint'
        )
      ])

  def describe_list():
    def it_lists(mocker):
      mocker.patch('lib.vault.hvac.Client')
      obj = Vault(
        addr='foourl',
        kvv2_mount_point='foomountpoint',
        path='foopath'
      )
      spy = mocker.spy(obj._client.secrets.kv.v2, 'list_secrets')
      assert obj.list() == lib.vault.hvac.Client().secrets.kv.v2.list_secrets()
      spy.assert_has_calls([
        mocker.call(
          path='foopath',
          mount_point='foomountpoint'
        )
      ])
