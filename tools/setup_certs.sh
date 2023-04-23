#!/bin/bash

cd certs || exit 1

rm *

# Generate CA cert and private key
openssl ecparam -name prime256v1 -genkey -noout -out ca.key
openssl req -new -x509 -days 365 \
    -subj "/C=XX/ST=XX/L=XX/O=XX/OU=CA" \
    -key ca.key -out ca.crt

# Generate server private key
openssl genrsa -out server.key 2048

# Generate server CSR
openssl req \
    -subj "/C=XX/ST=XX/L=XX/O=XX/OU=Server/CN=localhost" \
    -out server.csr -key server.key -new

# Sign server CSR and generate server cert
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
           -CAcreateserial -out server.crt -days 365


for client in test_client deye client; do

    # Generate client private key
    openssl genrsa -out $client.key 2048

    # Generate client CSR
    openssl req \
        -subj "/C=XX/ST=XX/L=XX/O=XX/OU=Client/CN=$client" \
        -out $client.csr -key $client.key -new

    # Sign client CSR and generate server cert
    openssl x509 -req -in $client.csr -CA ca.crt -CAkey ca.key \
            -CAcreateserial -out $client.crt -days 365

done