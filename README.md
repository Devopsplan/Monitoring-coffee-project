# CoffeeCraft Roastery

A small ecommerce demo built with Flask. The product catalog is a static
JSON file (`data/products.json`) — no database required — and the cart is
kept in the Flask session. It's meant as a clean, readable starting point
you can extend with a real database, payment provider, or user accounts.

## Features

- Product catalog rendered from `data/products.json`
- Product detail pages
- Session-based shopping cart (add / update quantity / remove)
- Free-shipping threshold logic
- Checkout form + order confirmation (no real payment processing)
- Custom dark "roastery" visual design, fully responsive

## Project structure

```
coffeecraft/
├── app.py                  # Flask app & routes
├── requirements.txt
├── data/
│   └── products.json       # static "database" of products
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── confirmation.html
│   └── 404.html
└── static/
    └── css/style.css
```

## Running it locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:4000 in your browser.

## Extending it

- **Swap in a real database**: replace `load_products()` / `get_product()`
  in `app.py` with SQLAlchemy models — the templates only expect each
  product to have the same fields as in `products.json`.
- **Add real payments**: the `checkout()` view is where you'd call out to
  Stripe/PayPal/etc. before creating the order.
- **Add accounts**: `flask-login` drops in cleanly next to the existing
  session-based cart.
- **Persist orders**: `session["last_order"]` is only good for one
  browser session — write it to a database or send it via email once you
  have persistence set up.

Set a real `SECRET_KEY` environment variable before deploying:

```bash
export SECRET_KEY="something-long-and-random"
```
-----------------------------

Phase 2nd 

>> Create a dockerfile  and docker image + check locally via container and docker compose .
 >> After the testing locally push that image to the dockerhub.

nano dockerfile

---

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 4000

CMD ["python", "app.py"]

---  --- --- --- --- --- --- 

docker build -t coffeecraft .
docker run -p 4000:4000 coffeecraft

or 

nano docker-compose.yaml

---

services:
  web:
    build: .
    ports:
      - "4000:4000"


------ --- --- --- --- --- 

docker compose up --build

docker tag coffeecraft:latest <dockerhub-username/coffeecraft:v1>

docker push <dockerhub-username/coffeecraft:v1>

-----------------

Phase 3 kubernetes 
--- --- --- --- --- --- --- --- 

Create deployment.yaml and service.yaml

nano deployment.yaml

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: coffeecraft
spec:
  replicas: 2
  selector:
    matchLabels:
      app: coffeecraft
  template:
    metadata:
      labels:
        app: coffeecraft
    spec:
      containers:
        - name: coffeecraft
          image: coffeecraft:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 4000

--- --- --- --- --- --- --- 

nano service.yaml

---

apiVersion: v1
kind: Service
metadata:
  name: coffeecraft
spec:
  type: NodePort
  selector:
    app: coffeecraft
  ports:
    - port: 4000
      targetPort: 4000
      nodePort: 30500


------
Run:

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

kubectl get pods
kubectl get svc coffeecraft


if firwall issue then:

gcloud compute firewall-rules update allow-nodeport --allow=tcp:<nodeport-port-number>

gcloud compute firewall-rules list --format="table(name,network,allowed[].map().firewall_rule().list())"

