# Simulador de Cache Automatizado

Este projeto automatiza testes em um simulador de cache via Selenium, executando diferentes configurações de cache e gerando relatórios com os resultados de **Hit Rate (%)** e **AMAT (ns)**, além de gráficos comparativos salvos em imagens.

---

## Objetivo

Facilitar a execução de testes no simulador de cache de forma sistemática e automática, sem a necessidade de interação manual com a interface web, economizando tempo e padronizando resultados.

---

## Requisitos

- Python 3.10 ou superior
- Google Chrome instalado
- WebDriver correspondente à sua versão do Chrome (chromedriver)
- Instalar dependências com:

```bash
pip install -r requirements.txt
```

---

## Estrutura do Projeto

```
project/
├── cache_simulations.py       # Script principal
├── utils.py                   # Funções auxiliares separadas
├── config.json                # Configuração dos testes
├── results/                   # Resultados gerados automaticamente
│   ├── 5-random-string-chars/
│   │   ├── 5-random-string-chars.results.csv
│   │   └── chart.png
│   └── string-compare-forloop/
│       ├── string-compare-forloo.results.csv
│       └── chart.png
```

---

## Como configurar os testes (`config.json`)

O arquivo `config.json` é onde você define os projetos de cache que serão testados:

### Exemplo:
```json
{
  "repetitions": 3,
  "cache_projects": [
      {
      "cache_L1": [64, 4, 8, "LRU", [2, 12]],
      "cache_L2": [],
      "cache_L3": []
      },
      {
      "cache_L1": [128, 2, 4, "Random", []],
      "cache_L2": [],
      "cache_L3": []
      },
      ...
  ]
}
```

### Campos:
- `repetitions`: Quantas vezes repetir cada teste (a média é calculada).
- `cache_projects`: Lista de configurações para cada projeto de cache.
  - `cache_L1`, `cache_L2`, `cache_L3`: Cada um representa um nível de cache.

### Cada nível de cache recebe:
```json
[sets, blocks_por_conjunto, palavras_por_bloco, politica_substituicao, [hit_time, miss_penalty]]
```
- Se quiser usar o valor padrão do simulador para `hit_time` e `miss_penalty`, basta usar um array vazio: `[]`
- Se não quiser usar determinado nível (ex: L2, L3), deixe o campo como `[]`.

---

## Como executar

Com o `config.json` configurado, execute:

```bash
python cache_simulations.py
```

O script irá:
1. Abrir o simulador via navegador automaticamente.
2. Aplicar cada configuração de projeto definida.
3. Executar os testes e extrair os resultados.
4. Repetir os testes conforme configurado.
5. Salvar os resultados e gerar gráficos automaticamente.

---

## Saída dos Resultados

Os resultados de cada **algoritmo** (ex: `5-random-string-chars`, `string-compare-forloop`, etc) são armazenados em:

```
results/
└── Algoritmo/
    ├── algoritmo.results.csv    # Resultados tabulados
    └── chart.png      # Gráfico com comparação entre projetos
```

### Arquivo CSV
```csv
"Hit Rate (%)" "AMAT (ns)"
91.9 1.81
93.2 1.55
...
```
Cada linha representa os resultados de um projeto.

### Imagem PNG (chart.png)
- Contém **dois gráficos de barras horizontais**:
  1. Comparando o Hit Rate entre os projetos.
  2. Comparando o AMAT entre os projetos.

---

## Dicas e Observações

- Cada algoritmo é testado já com todos os projetos configurados.
- Cada projeto de cache roda todos os algoritmos.
- O script é modular: você pode modificar facilmente as funções em `utils.py` para adaptar comportamentos.
- Basta modificar o arquivo config.json com base nas suas necessidades e rodar o cache_simulatons.py no terminal.

---
