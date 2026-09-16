# Desenvolvimento de API com Persistência e Arquitetura Distribuída

**Aluna:** Millena Rosa  
**Curso:** Análise e Desenvolvimento de Sistemas - Universidade de Passo Fundo (UPF)

Este repositório contém a entrega do trabalho da disciplina de Desenvolvimento de APIs e Micro Serviços. O projeto consiste em uma aplicação backend expondo uma API RESTful, integrada a conceitos de arquitetura distribuída e infraestrutura moderna utilizando containers.

---

## Decisões de Arquitetura:

Para o cumprimento dos requisitos, a arquitetura foi dividida nos seguintes componentes:

- **API e Persistência:** A API principal (Backend) foi desenvolvida em **Python (FastAPI)**. Ela implementa um CRUD para o recurso de _Produtos_. Os dados são persistidos de forma definitiva em um banco de dados relacional **PostgreSQL**.
- **API Gateway com Rate Limit e Load Balancer:**
  - Foi implementado um serviço dedicado de Gateway (também em FastAPI) que centraliza a entrada de requisições.
  - O **Load Balancer** interno distribui o tráfego recebido alternando entre as instâncias disponíveis da API (`backend-1` e `backend-2`) utilizando a estratégia _Round Robin_.
  - O **Rate Limiting** foi configurado utilizando **Redis** (algoritmo de janela fixa), bloqueando o IP do cliente com o erro `429 Too Many Requests` caso o limite configurado seja excedido, protegendo os backends de sobrecarga.
- **Telemetria e Monitoramento (Loki):**
  - A observabilidade do ecossistema foi garantida utilizando a stack da Grafana Labs.
  - O **Promtail** foi acoplado ao socket do Docker para capturar passivamente os logs de todos os containers (Gateway, Backends, Banco de Dados).
  - Os logs são enviados ao **Loki** e podem ser consultados visualmente e em tempo real através do dashboard do **Grafana**.

---

## Como Executar o Projeto:

A orquestração do ambiente é feita de forma automatizada pelo Docker. Não há necessidade de instalar bibliotecas locais ou configurar bancos de dados manualmente.

1. Certifique-se de ter o **Docker** e o **Docker Compose** instalados e em execução na sua máquina.
2. Clone este repositório ou extraia os arquivos na sua máquina.
3. Abra o terminal na raiz do projeto (onde está o arquivo `docker-compose.yml`).
4. Execute o comando abaixo para construir as imagens e subir os serviços em segundo plano:

   ```bash
   docker compose up --build -d
   ```

---

## Configurar o Grafana (Telemetria):

Como a interface visual do Grafana inicia sem conexões prévias, é necessário apontá-la para o nosso centralizador de logs (Loki) no primeiro acesso:

1. **Acesse o painel:** Abra `http://localhost:3000` no navegador (Credenciais: usuário **admin** / senha **admin**).
2. **Adicione a fonte de dados:** No menu lateral esquerdo, vá em **Connections** > **Data sources**.
3. **Selecione o Loki:** Clique no botão azul **Add data source** e pesquise por **Loki**.
4. **Configure a URL:** No campo de endereço (URL), insira a rota interna do container no Docker: `http://loki:3100`.
5. **Teste a conexão:** Role a página até o final e clique em **Save & test**. Uma notificação verde confirmará o sucesso.
6. **Monitore em tempo real:**
   - Acesse a aba **Explore** (ícone de bússola no menu lateral).
   - Em _Label filters_, selecione `container` e escolha a instância desejada (ex: `trabalhomillena-backend-1-1`).
   - Clique em **Run query** ou ative o modo **Live** (canto superior direito) para ver os logs de requisição da API aparecendo instantaneamente.

---

## Demonstração de Segurança (Rate Limiter):
Para fins de avaliação, o Rate Limiter no Gateway (apoiado pelo Redis) está configurado com um limite intencionalmente baixo (`RATE_LIMIT: 5` requisições por minuto). 

* **Comportamento esperado:** Ao testar o front-end intensamente (ex: clicando várias vezes para excluir produtos ou recarregando a página), o sistema bloqueará a sua conexão por segurança. Isso demonstrará a proteção contra ataques de sobrecarga atuando em tempo real.