# 5. Agente de Inteligência Artificial

## Objetivo

Esta etapa teve como objetivo integrar um modelo de linguagem à
aplicação para gerar um resumo executivo baseado nos indicadores de
vendas e nas métricas de qualidade dos dados.

O agente não realiza cálculos matemáticos diretamente.

Todos os valores utilizados no resumo são calculados previamente pelo
código Python e armazenados em arquivos JSON.

## Provedor utilizado

Foi utilizada a plataforma GroqCloud por disponibilizar acesso por API
com uma faixa gratuita adequada ao escopo educacional deste projeto.

O modelo configurado foi:

`llama-3.3-70b-versatile`

A Groq atua como plataforma de inferência para o modelo utilizado.

## Arquivo principal

A integração com a IA foi implementada em:

`src/agente_ia.py`

## Fontes de dados do agente

O agente recebe dois arquivos estruturados.

### Indicadores de vendas

`data/processed/resumo_indicadores.json`

Esse arquivo contém:

- indicadores gerais;
- modelos mais vendidos;
- modelo com maior faturamento;
- ranking de estados;
- formas de pagamento;
- destaques executivos.

### Qualidade dos dados

`data/processed/relatorio_qualidade.json`

Esse arquivo contém:

- total de registros;
- quantidade de validações;
- percentual geral de qualidade;
- campos válidos e inválidos;
- percentual de validade por campo.

## Fluxo do agente

O fluxo executado é:

1. carregar as instruções do prompt;
2. carregar os indicadores de vendas;
3. carregar o relatório de qualidade;
4. montar um contexto em formato JSON;
5. enviar o contexto para o modelo;
6. receber o resumo executivo;
7. validar se a resposta não está vazia;
8. exportar o resultado para um arquivo de texto;
9. disponibilizar o resumo no dashboard.

## Prompt do agente

As instruções utilizadas pelo agente estão em:

`prompts/resumo_executivo.md`

O prompt foi mantido em um arquivo separado para:

- facilitar ajustes;
- permitir versionamento;
- tornar as instruções visíveis ao avaliador;
- registrar a evolução do comportamento do agente.

## Primeira versão do prompt

A primeira versão produziu um resumo correto em grande parte, mas
incluiu interpretações não totalmente sustentadas pelos dados.

Exemplos observados:

- classificação do desempenho como razoável;
- sugestão de revisar processos;
- menção a perdas sem evidência suficiente;
- omissão de parte dos modelos empatados em uma das conclusões.

Esses resultados demonstraram que um modelo de linguagem pode produzir
inferências plausíveis, mas não necessariamente fundamentadas.

## Ajustes realizados no prompt

A segunda versão incluiu regras mais restritivas:

- não recalcular valores;
- não inventar informações;
- não atribuir causas;
- não fazer previsões;
- não classificar o desempenho subjetivamente;
- não recomendar mudanças sem evidência;
- informar todos os modelos empatados;
- diferenciar pedidos e vendas entregues;
- diferenciar faturamento bruto, realizado e cancelado;
- declarar limitações causadas por dados inválidos;
- informar quando os dados não permitem uma conclusão.

A temperatura do modelo também foi configurada como `0.0` para reduzir
variações e criatividade desnecessária.

## Resultado obtido

Após os ajustes, o agente produziu um resumo mais factual e aderente
aos dados.

O texto passou a:

- informar corretamente os seis modelos empatados;
- separar volume de pedidos e faturamento;
- reconhecer a diferença entre Texas e Califórnia;
- destacar as 24 datas inválidas;
- evitar atribuir causas aos resultados;
- declarar quando não existem dados suficientes para uma conclusão.

## Tratamento de erros

O módulo trata situações como:

- chave não configurada;
- chave inválida;
- indisponibilidade da API;
- limite gratuito atingido;
- arquivo ausente;
- resposta vazia;
- erros inesperados.

A aplicação apresenta mensagens controladas em vez de interromper sua
execução com um rastreamento técnico completo.

## Segurança da chave

A chave da API é armazenada no arquivo local:

`.env`

A variável utilizada é:

`GROQ_API_KEY`

O arquivo `.env` é ignorado pelo Git e não deve ser publicado.

O repositório contém apenas:

`.env.example`

Esse arquivo demonstra a configuração necessária sem revelar a chave
real.

## Integração com o dashboard

O dashboard apresenta:

- o último resumo executivo salvo;
- um botão para gerar um novo resumo;
- uma mensagem enquanto a chamada está sendo processada;
- tratamento visual de erros;
- continuidade dos gráficos mesmo quando a API não está disponível.

O resumo gerado é armazenado em:

`data/processed/resumo_executivo_ia.txt`

## Resiliência

A IA é uma camada de interpretação e não uma dependência dos cálculos.

Mesmo sem acesso à Groq, a aplicação continua exibindo:

- indicadores gerais;
- relatório de qualidade;
- gráficos;
- rankings;
- dados sanitizados.

Essa arquitetura reduz o acoplamento entre a análise determinística e o
modelo generativo.

## Limitações

- o resumo pode apresentar pequenas variações entre execuções;
- a faixa gratuita da API possui limites de uso;
- o agente depende da disponibilidade externa da Groq;
- o modelo interpreta apenas os indicadores fornecidos;
- a qualidade do texto depende das instruções do prompt;
- o resumo não substitui uma análise humana especializada.