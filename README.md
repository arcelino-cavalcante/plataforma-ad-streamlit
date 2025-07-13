# Plataforma AD Streamlit

Este repositório contém um painel em [Streamlit](https://streamlit.io/) para gerenciamento de casos jurídicos.

## Executando

1. Instale as dependências necessárias:
   ```bash
   pip install streamlit streamlit-option-menu streamlit-calendar fpdf openpyxl \
       requests
   ```
2. Execute a aplicação com:
   ```bash
   streamlit run app.py
   ```

Este projeto utiliza um backend em **Google Apps Script** para manipular as
planilhas e os documentos. Crie um projeto no Apps Script, implemente as ações
necessárias (adicionar, editar, excluir e buscar dados) e publique-o como *Web
App*. Defina a variável de ambiente `APPS_SCRIPT_URL` com o endereço do script
implantado. Todas as operações de salvamento e upload feitas pelo painel serão
enviadas para essa URL utilizando requisições HTTP.

O painel possui as seguintes seções:
- Visão Geral
- Clientes
- Casos
- Documentos
- Agenda
- Tarefas
- Casos por Cliente
- Financeiro
- Relatórios

Cada seção permite cadastrar e visualizar informações relacionadas ao dia a dia do advogado.

O menu **Relatórios** permite exportar a listagem de casos, documentos ou movimentos financeiros para arquivos Excel ou PDF.

Os formulários agora utilizam `st.dialog` para exibir caixas de diálogo modais
ao adicionar novos registros. Os formulários de edição também usam `st.dialog`.
