# Fortress

This repo contains code for authenticating with [Hashicorp Vault](https://www.vaultproject.io/) and fetching secrets. The code can be run as a script at the command-line, and it can also be used by Python applications as a package.

The script is run in a Kubernetes Init Container for [Artsy apps](https://github.com/artsy/hokusai-sandbox/blob/e04dc52c7e5cd0144c34ba0541e7d32fc84bc15f/hokusai/staging.yml#L35).

* __Point People:__ [#product-sapphire][sapphire_channel]


## Setup

Read and run the setup script:
```
./bin/setup.sh
```

## Run Script

To run the script with environment files loaded (using [Foreman](https://github.com/ddollar/foreman)):

```
foreman run --env .env.shared,.env python src/load/load.py iam staging hokusai-sandbox
```

## Testing

### Unit tests

```
make test
```

or

```
pytest <dir>
ptw <dir>
```

[sapphire_channel]: https://artsy.slack.com/messages/product-sapphire "#product-sapphire Slack Channel"
