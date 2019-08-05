

# Helm chart for LND Lightning Node
This chart will install an [LND](https://dev.lightning.community/) server inside a kubernetes cluster. New certificates are generated on install, and a script is provided to auto-unlock the wallet if needed.

### Uses
The primary purpose of this chart was to make it easy to access kubernetes services during development.  It could also be used for any service that only needs to be accessed through a vpn or as a standard vpn.

### Prerequisites Details

* Kubernetes 1.6+
* PV dynamic provisioning support on the underlying infrastructure

#### StatefulSets Details
* https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/

#### StatefulSets Caveats
* https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/#limitations

## Chart Details
This chart will do the following:

* Implemented a lnd node server using Kubernetes StatefulSets/Deployments
* A way to auto-unlock the wallet
* Statefulset provides a way to persist your node data

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
$ helm install --name my-release incubator/lnd
```

## Deleting the Charts

Delete the Helm deployment as normal

```
$ helm delete my-release
```

> Deletion of the StatefulSet doesn't cascade to deleting associated PVCs

## Configuration
The following table lists the configurable parameters of the `lnd` chart and their default values,
and can be overwritten via the helm `--set` flag.

Parameter | Description | Default
---                                   | ---                                                                   | ---
`replicaCount`                        | amount of parallel lnd replicas to be started                         | `1`
`updateStrategy`                      | update strategy for deployment                                        | `{type: rollingUpdate}`
`image.repository`                    | LND container image repository                                        | `lightningnetwork/lnd-alpine`
`image.tag`                           | LND container image tag                                               | `latest`
`image.pullPolicy`                    | Image pull policy                                                     | `IfNotPresent`
`lnd.debugLevel`                      | Debug logging level                                                   | `info`
`lnd.keystoreSecret`                  | Name of secret holding the TLS private key and certificate            | `nil`
`lnd.alias`                           | Your node alias, e.g. `My Lightning Node`                             | `nil`
`lnd.color`                           | The color of the node in hex format, e.g. `"#5293fc"`                 | `nil`
`lnd.externalip`                      | IP to advertise your node to the network with                         | `nil`
`lnd.tlsextradomains`                 | Adds an extra domain to the generate certificate                      | `nil`
`lnd.tlsextraips`                     | Adds an extra ip to the generated certificate                         | `nil`
`lnd.unlock.enabled`                  | Auto-unlock the wallet with the supplied password                     | `false`
`lnd.unlock.walletSecret`             | Name of secret holding the wallet password, e.g. `wallet-secrets`     | `nil`
`lnd.autopilot.enabled`               | Enable auto-pilot to open channels for you                            | `false`
`lnd.autopilot.maxchannles`           | The maximum number of channels that should be created                 | `5`
`lnd.autopilot.allocation`            | The fraction of total funds that should be used by auto pilot         | `0.6`
`bitcoin.enabled`                     | If the Bitcoin chain should be active                                 | `true`
`bitcoin.network`                     | Use Bitcoin's test network to use, `simnet`, `testnet`, `mainnet`     | `testnet`
`bitcoin.node`                        | Backend bitcoin node                                                  | `bitcoind`
`bitcoin.defaultchanconfs`            | Number of confirmations for a channel to be open                      | `nil`
`bitcoin.bitcoind.rpchost`            | The host that your local bitcoind daemon is listening on              | `nil`
`bitcoin.bitcoind.rpcuser`            | Username for RPC connections to bitcoind`bitcoin`                     | `nil`
`bitcoin.bitcoind.rpcpass`            | Password for RPC connections to bitcoind`password`                    | `nil`
`bitcoin.bitcoind.zmqpubrawblock`     | ZMQ socket for rawblock notifications, e.g. `tcp://127.0.0.1:28332`   | `nil`
`bitcoin.bitcoind.zmqpubrawtx`        | ZMQ socket for rawtx notifications, e.g. `tcp://127.0.0.1:28332`      | `nil`
`persistence.enabled`                 | Use a PVC to persist configuration                                    | `true`
`persistence.accessMode`              | Use volume as ReadOnly or ReadWrite                                   | `ReadWriteOnce`
`persistence.size`                    | Size of data volume                                                   | `"5Gi"`
`persistence.storageClass`            | Storage class of backing PVC, e.g. `"ssd"`                            | `nil`
`resources`                           | Node resources requests & limits                                      | `{}`
`nodeSelector`                        | Node labels for data pod assignment                                   | `{}`
`tolerations`                         | Node tolerations                                                      | `[]`
`affinity`                            | Node affinity policy                                                  | `{}`

### Services

This charts expose the lnd node with two service.
- `api` service that expose the rest and rpc servers, by default use a `ClusterIP` service to expose within the cluster.
- `p2p` service that expose the p2p server, by default use a `LoadBalancer` service to expose to the world.

Parameter | Description | Default
---                                   | ---                                                          | ---
`services.api.type`                   | service type exposing ports, e.g. `NodePort`                 | `ClusterIP`
`services.api.restPort`               | port to listen on for rest connections                       | `8080`
`services.api.restListen`             | interfaces to listen on for rest connections                 | `["0.0.0.0"]`
`services.api.rpcPort`                | port to listen on for gRPC connections                       | `10009`
`services.api.rpcListen`              | interfaces to listen on for gRPC connections                 | `[]`
`services.p2p.type`                   | service type exposing ports, e.g. `NodePort`                 | `LoadBalancer`
`services.p2p.port`                   | port to listen on for p2p connections                        | `9735`
`services.p2p.listen`                 | interfaces to listen on for p2p connections                  | `[]`
`services.p2p.nolisten`               | Disable listening for incoming p2p connections               | `false`


Please refer to the `values.yaml` and the `templates/config-lnd.yml` files to find more thorough descriptions

### Certificates

New certificates are generated with each deployment unless persistence is enabled. With persistence, certificate data will be persisted across pod restarts.

Certificates can be passed in secret, which name is specified in *lnd.keystoreSecret* value.
Create secret as follows:

```bash
kubectl create secret generic lnd-keystore --from-file=./tls.key --from-file=./tls.cert
```

You can deploy temporary lnd chart, create secret from generated certificates, and then re-deploy lnd, providing the secret.
Certificates can be found in lnd pod in the following files:

 `/root/.lnd/data/certs/tls.key`
 `/root/.lnd/data/certs/tls.cert`

### Macaroons

New macaroons are generated with each deployment unless persistence is enabled. With persistence, maracoons data will be persisted across pod restarts.

Macaroons can be found in lnd pod in the following files:

 `/root/.lnd/data/chain/bitcoin/{network}/admin.macaroon`
 `/root/.lnd/data/chain/bitcoin/{network}/readonly.macaroon`
 `/root/.lnd/data/chain/bitcoin/{network}/invoice.macaroon`

You can download the generated macaroons to used them on other client applications.
They can be download using `kubetcl cp`

```
kubectl cp ${RELEASE_NAME}-0:/root/.lnd/data/chain/bitcoin/{network}/admin.macaroon .
```

## Create a wallet

When the node is firts started, it will not have a wallet. We recommend to disable `lnd.unlock` until a wallet is created or recovered.

To create a wallet, you can un the *lnd cli*:

```
kubectl exec -ti ${RELEASE_NAME}-0 -- lncli --tlscertpath /root/.lnd/data/tls.cert create
```

The follow the instructions to create or to recover a wallet.

## Auto Unlock Wallet

To auto unlock the wallet on every restart just enable it with `lnd.unlock.enabled: true`
You can pass the wallet password in a secret with a key named `WALLET_PASSWORD`. You'll specify
the name of the secret holding the password in `lnd.unlock.walletSecret`

```
kubectl create secret generic wallet-secrets --from-literal=WALLET_PASSWORD="my_password"
```