from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Controller(BaseHTTPRequestHandler):
    def sync(self, parent, children):
        # Generate the desired child object(s).
        ingressVersion = parent.get("spec", {})["ingressVersion"]
        if ingressVersion == "extensions/v1beta1":
            desired_pods = [
                {
                    "apiVersion": ingressVersion,
                    "kind": "Ingress",
                    "metadata": {
                        "name": "ingress-0",
                        "annotations": {
                            "kubernetes.io/ingress.class": "nginx",
                            "nginx.ingress.kubernetes.io/proxy-body-size": "100m",
                            "nginx.ingress.kubernetes.io/proxy-read-timeout": "120",
                        },
                    },
                    "spec": {
                        "rules": [
                            {
                                "host": "weirdhost.dev",
                                "http": {
                                    "paths": [
                                        {
                                            "path": "/",
                                            "backend": {
                                                "serviceName": "kubernetes",
                                                "servicePort": 443,
                                            },
                                        }
                                    ]
                                },
                            }
                        ],
                    },
                },
            ]
        else:
            desired_pods = [
                {
                    "apiVersion": "networking.k8s.io/v1",
                    "kind": "Ingress",
                    "metadata": {
                        "name": "ingress-0",
                        "annotations": {
                            "kubernetes.io/ingress.class": "nginx",
                            "nginx.ingress.kubernetes.io/proxy-body-size": "100m",
                            "nginx.ingress.kubernetes.io/proxy-read-timeout": "120",
                        },
                    },
                    "spec": {
                        "rules": [
                            {
                                "host": "weirdhost.dev",
                                "http": {
                                    "paths": [
                                        {
                                            "path": "/",
                                            "pathType": "ImplementationSpecific",
                                            "backend": {
                                                "service": {
                                                    "name": "kubernetes",
                                                    "port": {"number": 443},
                                                }
                                            },
                                        }
                                    ],
                                },
                            },
                        ],
                    },
                },
            ]

        x = {"status": {}, "children": desired_pods}
        print(f"returning {x}")
        return x

    def do_POST(self):
        # Serve the sync() function as a JSON webhook.
        observed = json.loads(self.rfile.read(int(self.headers.get("content-length"))))
        print(f"============\nObserved: {observed}\n")
        desired = self.sync(observed["parent"], observed["children"])

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(desired).encode())


HTTPServer(("", 80), Controller).serve_forever()
