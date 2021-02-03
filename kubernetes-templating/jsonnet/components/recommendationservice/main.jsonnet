local kap = import "lib/kapitan.libjsonnet";
local inv = kap.inventory();

local myContainers = [
  {
    name: "server",
    image: inv.parameters.server.image,
    ports: [{ containerPort: 8080 }],
    readinessProbe: {
      periodSeconds: 5,
      exec: {
        command: [
          "/bin/grpc_health_probe",
          "-addr=:8080"
        ],
      },
    },
    livenessProbe: {
      periodSeconds: 5,
      exec: {
        command: [
          "/bin/grpc_health_probe",
          "-addr=:8080",
        ],
      },
    },
    env: [
      {
        name: "PORT",
        value: "8080",
      },
      {
        name: "PRODUCT_CATALOG_SERVICE_ADDR",
        value: "productcatalogservice:3550",
      },
      {
        name: "ENABLE_PROFILER",
        value: "0",
      },
    ],
    resources: {
      requests: {
        cpu: "100m",
        memory: "220Mi",
      },
      limits: {
        cpu: "200m",
        memory: "450Mi",
      },
    },
  },
];

local deployment = {
    apiVersion: "apps/v1",
    kind: "Deployment",
    metadata: {
        name: "recommendationservice",
    },
    spec: {
        replicas: inv.parameters.server.replicas,
        selector: {
          matchLabels: { app: "recommendationservice" },
        },
        template: {
            metadata: {
                labels: { app: "recommendationservice" },
            },
            spec: {
                containers: myContainers,
                terminationGracePeriodSeconds: 5,
            },
        },
    },
};

local service = {
    apiVersion: "v1",
    kind: "Service",
    spec: {
        ports: [
            { name: "grpc", port: 8080, targetPort: 8080 },
        ],
        selector: { app: "recommendationservice" },
        type: "ClusterIP",
    },

    metadata: {
        name: "recommendationservice",
        labels: { name: "recommendationservice" },
    },
};


{
    "deployment": deployment,
    "service": service,
}
