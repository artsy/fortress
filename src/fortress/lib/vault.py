import logging

import boto3
import hvac
from hvac.api.auth_methods import Kubernetes


class Vault:
    """Interface with Hashicorp Vault"""

    def __init__(
        self,
        addr,
        kvv2_mount_point=None,
        path=None,
    ):
        self._client = hvac.Client(url=addr)
        self._mount_point = kvv2_mount_point
        self._path = path

    ## login methods

    def iam_login(self, role=None):
        """log into Vault using AWS IAM keys"""
        session = boto3.Session()
        credentials = session.get_credentials()
        # if role is None, hvac defaults it to iam username
        self._client.auth.aws.iam_login(
            credentials.access_key, credentials.secret_key, credentials.token, role=role
        )

    def kubernetes_login(self, role=None, sa_token_path=None):
        """authenticate using k8s pod service account token"""
        if role == None or sa_token_path == None:
            raise Exception(
                "Vault Kubernetes login requires a role and Kubernetes pod service account token path."
            )
        with open(sa_token_path) as token_file:
            jwt = token_file.read()
        Kubernetes(self._client.adapter).login(role=role, jwt=jwt)

    ##

    def get(self, key):
        """get an entry"""
        full_path = f"{self._path}{key}"
        logging.debug(f"Vault: getting {full_path}")
        # if key does not exist or if data is soft-deleted, it raises:
        # hvac.exceptions.InvalidPath
        response = self._client.secrets.kv.read_secret_version(
            path=full_path, mount_point=self._mount_point
        )
        # return value of key
        return response["data"]["data"][key]

    def list(self):
        """list keys under a path"""
        logging.debug(f"Vault: listing {self._path}")
        # list includes soft-deleted keys
        response = self._client.secrets.kv.v2.list_secrets(
            path=self._path, mount_point=self._mount_point
        )
        return response
