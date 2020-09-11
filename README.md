# Helm chart for LND Lightning Node

This chart will install an [LND](https://dev.lightning.community/) server inside a kubernetes cluster. New certificates are generated on install, and a script is provided to auto-unlock the wallet if needed.

## Chart Details

This chart will do the following:

* Implemented a lnd node server using Kubernetes StatefulSets
* A way to auto-unlock the wallet
* Statefulset provides a way to persist your node data
* Run lndmon to gather monitoring metrics and provision grafana default dashboards
* Use prometheus operator servicemonitor CRD if enabled
* Default images are build using the Dockerfiles from the official repos. You can always build your own.
  * <https://github.com/lightningnetwork/lnd/blob/master/docker/lnd/Dockerfile>
  * <https://github.com/lightninglabs/lndmon/blob/master/Dockerfile>

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
git clone https://github.com/budacom/helm-lnd lnd
helm install --name my-release lnd
```

## Deleting the Charts

Delete the Helm deployment as normal

```bash
helm delete my-release
```

> Deletion of the StatefulSet doesn't cascade to deleting associated PVCs

## Configuration

The following table lists the configurable parameters of the `lnd` chart and their default values,
and can be overwritten via the helm `--set` flag.

Parameter | Description | Default
---                                           | ---                                                                   | ---
`replicaCount`                                | amount of parallel lnd replicas to be started                         | `1`
`updateStrategy`                              | update strategy for deployment                                        | `{type: rollingUpdate}`
`image.repository`                            | LND container image repository                                        | `budacom/lnd`
`image.tag`                                   | LND container image tag                                               | `v0.7.1-beta`
`image.pullPolicy`                            | Image pull policy                                                     | `IfNotPresent`
`lnd.debugLevel`                              | Debug logging level                                                   | `info`
`lnd.keystoreSecret`                          | Name of secret holding the TLS private key and certificate            | `nil`
`lnd.alias`                                   | Your node alias, e.g. `My Lightning Node`                             | `nil`
`lnd.color`                                   | The color of the node in hex format, e.g. `"#5293fc"`                 | `nil`
`lnd.externalip`                              | IP to advertise your node to the network with                         | `nil`
`lnd.tlsextradomains`                         | Adds an extra domain to the generate certificate                      | `nil`
`lnd.tlsextraips`                             | Adds an extra ip to the generated certificate                         | `nil`
`lnd.unlock.enabled`                          | Auto-unlock the wallet with the supplied password                     | `false`
`lnd.unlock.walletSecret`                     | Name of secret holding the wallet password, e.g. `wallet-secrets`     | `nil`
`lnd.autopilot.enabled`                       | Enable auto-pilot to open channels for you                            | `false`
`lnd.autopilot.maxchannles`                   | The maximum number of channels that should be created                 | `5`
`lnd.autopilot.allocation`                    | The fraction of total funds that should be used by auto pilot         | `0.6`
`lnd.prometheus.enabled`                      | Enable prometheus /metrics endpoint                                   | `false`
`lnd.prometheus.listen`                       | The host and por bind for the metrics endpoint                        | `0.0.0.0:9092`
`lnd.prometheus.serviceMonitor.enabled`       | Create serviceMonitor resource for the lnd service                    | `true`
`lnd.prometheus.serviceMonitor.interval`      | Define the scrape interval, e.g. `30s`                                | `nil`
`lnd.prometheus.serviceMonitor.scrapeTimeout` | Define the scrape timeout, e.g. `10s`                                 | `nil`
`lnd.persistence.enabled`                     | Use a PVC to persist configuration                                    | `true`
`lnd.persistence.accessMode`                  | Use volume as ReadOnly or ReadWrite                                   | `ReadWriteOnce`
`lnd.persistence.size`                        | Size of data volume                                                   | `"5Gi"`
`lnd.persistence.storageClass`                | Storage class of backing PVC, e.g. `"ssd"`                            | `nil`
`lnd.livenessProbe.enabled`                   | Enable/disable the readiness probe                                    | `false`
`lnd.readinessProbe.enabled`                  | Enable/disable the liveness probe                                     | `false`
`lnd.resources`                               | Node resources requests & limits                                      | `{}`
`bitcoin.enabled`                             | If the Bitcoin chain should be active                                 | `true`
`bitcoin.network`                             | Use Bitcoin's test network to use, `simnet`, `testnet`, `mainnet`     | `testnet`
`bitcoin.node`                                | Backend bitcoin node                                                  | `bitcoind`
`bitcoin.defaultchanconfs`                    | Number of confirmations for a channel to be open                      | `nil`
`bitcoin.bitcoind.rpchost`                    | The host that your local bitcoind daemon is listening on              | `nil`
`bitcoin.bitcoind.rpcuser`                    | Username for RPC connections to bitcoind`bitcoin`                     | `nil`
`bitcoin.bitcoind.rpcpass`                    | Password for RPC connections to bitcoind`password`                    | `nil`
`bitcoin.bitcoind.zmqpubrawblock`             | ZMQ socket for rawblock notifications, e.g. `tcp://127.0.0.1:28332`   | `nil`
`bitcoin.bitcoind.zmqpubrawtx`                | ZMQ socket for rawtx notifications, e.g. `tcp://127.0.0.1:28332`      | `nil`
`nodeSelector`                                | Node labels for data pod assignment                                   | `{}`
`tolerations`                                 | Node tolerations                                                      | `[]`
`affinity`                                    | Node affinity policy                                                  | `{}`

### Services

This charts expose the lnd node with two service.

* `api` service that expose the rest and rpc servers, by default use a `ClusterIP` service to expose within the cluster.
* `p2p` service that expose the p2p server, by default use a `LoadBalancer` service to expose to the world.

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

### Lndmon, monitoring with prometheus

lndmon is a drop-in monitoring solution for your lnd node using Prometheus and Grafana. [lightninglabs/lndmon](https://github.com/lightninglabs/lndmon)

Parameter | Description | Default
---                                              | ---                                                                   | ---
`lndmon.enabled`                                 | Enable lndmon prometheus /metrics endpoint                            | `false`
`lndmon.image.repository`                        | lndmon container image repository                                     | `budacom/lndmon`
`lndmon.image.tag`                               | lndmon container image tag                                            | `v0.1.0`
`lndmon.image.pullPolicy`                        | Image pull policy                                                     | `IfNotPresent`
`lndmon.prometheus.listen`                       | The host and por bind for the metrics endpoint                        | `0.0.0.0:9092`
`lndmon.prometheus.logdir`                       | Directory to log output                                               | `nil`
`lndmon.prometheus.maxlogfiles`                  | Maximum log files to keep (0 for no rotation)                         | `nil`
`lndmon.prometheus.maxlogfilesize`               | Maximum log file size in MB                                           | `nil`
`lndmon.prometheus.serviceMonitor.enabled`       | Create serviceMonitor resource for the lndmon service                 | `true`
`lndmon.prometheus.serviceMonitor.interval`      | Define the scrape interval, e.g. `30s`                                | `nil`
`lndmon.prometheus.serviceMonitor.scrapeTimeout` | Define the scrape timeout, e.g. `10s`                                 | `nil`
`lndmon.resources`                               | Lndmon resources requests & limits                                    | `{}`
`lndmon.livenessProbe.enabled`                   | Enable/disable the readiness probe                                    | `false`
`lndmon.readinessProbe.enabled`                  | Enable/disable the liveness probe                                     | `false`


### Lndbackup, static channel backups

lndbackup is a simple application that subscribe to the static channel backups from lnd and upload them to google cloud storage.

Parameter | Description | Default
---                                              | ---                                                                   | ---
`lndbackup.enabled`                              | Enable lndbackup prometheus /metrics endpoint                         | `false`
`lndbackup.image.repository`                     | lndbackup container image repository                                  | `budacom/lndbackup`
`lndbackup.image.tag`                            | lndbackup container image tag                                         | `v0.1.0`
`lndbackup.bucketUrl`                            | lndbackup target gsc bucket                                           | `gs://my_bucket/path`
`lndbackup.provider`                             | Object storage provider to backup to `gcs`                            | `gcs`
`lndbackup.gcs.secretName`                       | Secret that holds the service account key to write to the bucket      | `lnd-manager`
`lndbackup.gcs.keyFilename`                      | Key to the json file in the secret                                    | `service-account.json`


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

To regenerate the certificates you can run:

```bash
kubectl exec -ti ${RELEASE_NAME}-0 -- rm -R /root/.lnd/data/certs
kubectl delete pod ${RELEASE_NAME}-0
```

### Macaroons

New macaroons are generated with each deployment unless persistence is enabled. With persistence, maracoons data will be persisted across pod restarts.

Macaroons can be found in lnd pod in the following files:

 `/root/.lnd/data/chain/bitcoin/{network}/admin.macaroon`
 `/root/.lnd/data/chain/bitcoin/{network}/readonly.macaroon`
 `/root/.lnd/data/chain/bitcoin/{network}/invoice.macaroon`

You can download the generated macaroons to used them on other client applications.
They can be download using `kubetcl cp`

```bash
kubectl cp ${RELEASE_NAME}-0:/root/.lnd/data/chain/bitcoin/{network}/admin.macaroon .
```

## Create a wallet

When the node is firts started, it will not have a wallet. We recommend to disable `lnd.unlock` until a wallet is created or recovered.

To create a wallet, you can run the *lnd cli*:

```bash
kubectl exec -ti ${RELEASE_NAME}-0 -- lncli --tlscertpath /root/.lnd/data/certs/tls.cert create
```

The follow the instructions to create or to recover a wallet.

## Auto Unlock Wallet

To auto unlock the wallet on every restart just enable it with `lnd.unlock.enabled: true`
You can pass the wallet password in a secret with a key named `WALLET_PASSWORD`. You'll specify
the name of the secret holding the password in `lnd.unlock.walletSecret`

```bash
kubectl create secret generic wallet-secrets --from-literal=WALLET_PASSWORD="my_password"
```

## Prerequisites Details

* Kubernetes 1.6+
* PV dynamic provisioning support on the underlying infrastructure

### StatefulSets Details

* https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/

### StatefulSets Caveats

* https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/#limitations
