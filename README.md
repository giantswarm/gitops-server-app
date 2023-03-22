# GitOps Server Helm Chart

This Helm Chart provides a Weave GitOps Server setup based on the [upstream Helm Chart](https://github.com/weaveworks/weave-gitops/tree/main/charts/gitops-server). The server provides a graphical interface to the GitOps environments managed by Flux. Quoting the [official documentation](https://docs.gitops.weave.works/docs/0.18.0/intro/):

> The web UI surfaces key information to help application operators easily discover and resolve issues. The intuitive interface provides a guided experience to build understanding and simplify getting started for new users; they can easily discover the relationship between Flux objects and navigate to deeper levels of information as required.

## Installing

There are several ways to install this app onto a workload cluster.

- [Using GitOps to instantiate the App](https://docs.giantswarm.io/advanced/gitops/#installing-managed-apps)
- [Using our web interface](https://docs.giantswarm.io/ui-api/web/app-platform/#installing-an-app).
- By creating an [App resource](https://docs.giantswarm.io/ui-api/management-api/crd/apps.application.giantswarm.io/) in the management cluster as explained in [Getting started with App Platform](https://docs.giantswarm.io/app-platform/getting-started/).

## Configuring

This section gives various example of how to configure the `values.yaml`.

### Accessing the GitOps Server

Access from the outside world can be configured by the means of Ingress CR. The part of `values.yaml` responsible for handling its creation is presented below:

```yaml
ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts: []
  tls: []
```

A configuration could be something like this:

```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: gitops.fake.cluster.domain
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls:
    - hosts:
        - gitops.fake.cluster.domain
      secretName: gitops-tls
```

The server can also be access by the means of `kubectl port-forward` command, like for example:

```yaml
k port-forward svc/flux-system-gitops-server 9001:9001
Forwarding from 127.0.0.1:9001 -> 9001
Forwarding from [::1]:9001 -> 9001
```

In either case, authentication method could be either OIDC or cluster-local user account, see the next paragraph for details.

### Authentication to the GitOps Server

There are 2 supported methods for logging into the dashboard:

* via an OIDC provider
* via a cluster user account

Quoting the [official documentation](https://docs.gitops.weave.works/docs/0.18.0/configuration/securing-access-to-the-dashboard/), the latter one is not recommended:

> The recommended method is to integrate with an OIDC provider, as this will let you control permissions for existing users and groups that have already been configured to use OIDC. However, it is also possible to use the Emergency Cluster User Account to login, if an OIDC provider is not available to use. Both methods work with standard Kubernetes RBAC.

By default, both methods are enabled in the GitOps Server, even if only one is actually used. This can be controlled by the `--auth-methods` parameter passed to the GitOps Server. For example, in order to use only the OIDC provider method, configure the
`values.yaml` this way:

```yaml
additionalArgs:
  - "--auth-methods=oidc"
```

To use only the cluster user account, configure the `values.yaml` this way:

```yaml
additionalArgs:
  - "--auth-methods=user-account"
```

Next paragraphs shortly elaborate on configuration for each method.

#### Configuring Helm Chart for OIDC provider method

The part of `values.yaml` responsible for integrating the GitOps Server with the OIDC provider is presented below:

```yaml
oidcSecret:
  create: false
  # clientID:
  # clientSecret:
  # issuerURL:
  # redirectURL:
```

Meaning of the values can be found in the [official documentation](https://docs.gitops.weave.works/docs/0.18.0/configuration/oidc-access/#configuration). Setting on these values, and switching create flag, e.g. `oidcSecret.create`, from `false` to `true`, will instruct Helm Chart to create the necessary Kubernetes Secret with OIDC client configuration. See an example below.

```yaml
oidcSecret:
  create: true
  clientID: fakeclient          # configured with the provider
  clientSecret: fakesecret      # configured with the provider
  issuerURL: https://dex.fake.cluster.domain
  redirectURL: https://gitops.fake.cluster.domain/oauth2/callback
```

Bear in mind, as shown in the upstream documentation, the `oidc-auth` Kubernetes Secret may also be created by hand, or by some other means, in which case the create flag should remain set to `false`. No further configuration of the Helm Chart would be required in such case, the Secret should **get discovered by the GitOps Server automatically**.

#### Configuring Helm Chart for cluster user account method

The part of `values.yaml` responsible for creating a local cluster user for the GitOps Server is presented below:

```yaml
adminUser:
  create: false
  createClusterRole: true
  createSecret: true
  username: gitops-test-user
  passwordHash: ""
```

To create a local user the create flag, e.g. `adminUser.create`, must be switched to `true`. The `adminUser.username` and the `adminUser.passwordHash` fields configure the user name and password respectively. Password must be provided in a **form of the bcrypt hash**. One way to generate it from the plaintext password is to use the [Weaveworks GitOps CLI tool](https://docs.gitops.weave.works/docs/0.18.0/installation/weave-gitops/#install-the-gitops-cli), for example:

```shell
$ echo -n fakepassword | gitops get bcrypt-hash
$2a$10$sLpbh.W/hR77JvD40ScekOl50Dw97PaD.sRhOdu.SlNxPCAJHCCVK
```

**IMPORTANT**, as for the OIDC login, the `cluster-user-auth` Kubernetes Secret holding user credentials may get created outside this Helm Chart, in which case, the `adminUser.createSecret` flag should get switched to `false`. Note however, presence of the `cluster-user-auth` Secret is **absolutely necessary** by the GitOps Server to boot properly, when `user-account` login method has been choosen.

### Configuring RBAC permissions

No matter the authentication method, the GitOps Server impersonates the user that was logged in and uses his permissions for accessing the resources. When OIDC authentication is being used, the RBAC permissions of the IdP users are managed outside the application. The app however offers a way to limit the groups and users names that can be impersonated by the GitOps Server.

When a local cluster user account is being used instead, the app, on top of the [basic set of permissions for this user](https://docs.gitops.weave.works/docs/0.18.0/configuration/emergency-user/#user-permissions), offers a way to configure extra RBAC rules.

Next paragraphs shortly elaborate on configuration for each case.

#### Limit Impersonation

The part of `values.yaml` responsible for controlling impersonation permissions is presented below:

```yaml
giantswarm:
  rbac:
    impersonation:
      users:
        enabled: true
        resourceNames: []
      groups:
        enabled: true
        resourceNames: []
```

By default impersonation of all the users and groups is allowed. To limit this to only certain users or groups, the `giantswarm.rbac.impersonation.users.resourceNames` or the `giantswarm.rbac.impersonation.groups.resourceNames` arrays should get populated with the users' and groups' names respectively. Find an example below.

```yaml
giantswarm:
  rbac:
    impersonation:
      users:
        enabled: true
        resourceNames: ['user1@corporation.com', 'user2@corporation.com']
      groups:
        enabled: true
        resourceNames: ['admins', 'operations', 'devops']
```

#### Configuring extended RBAC permissions for the local cluster user account

The part of `values.yaml` responsible for extending the local user account permissions is presented below:

```yaml
giantswarm:
  rbac:
    additionalRules: []
```

The content of the `giantswarm.rbac.additionalRules` array must follow the [Kubernetes PolicyRule specification](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.26/#policyrule-v1-rbac-authorization-k8s-io), for example:

```yaml
giantswarm:
  rbac:
    additionalRules:
      - apiGroups: ["infra.contrib.fluxcd.io"]
        resources: ["terraforms"]
        verbs: [ "get", "list", "patch" ]
```

## Limitations

* Currently GitOps Server impersonates **all the groups** passed by in the ID token, what may cause troubles when the `giantswarm.rbac.impersonation.groups.resourceNames` array is not empty, for then if the ID token carries groups that are not listed in the aforemantioned array, user won't be granted access.

## Credit

- [Weaveworks GitOps](https://github.com/weaveworks/weave-gitops/tree/main/charts/gitops-server)
