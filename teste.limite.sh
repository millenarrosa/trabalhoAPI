#!/bin/bash
echo "Iniciando simulação (6 requisições seguidas)"

for i in {1..6}
do
   curl http://localhost:9000/api/health
   echo "" 
done