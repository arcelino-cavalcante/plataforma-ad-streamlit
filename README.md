# Plataforma AD Streamlit

Este repositório contém um painel em [Streamlit](https://streamlit.io/) para gerenciamento de casos jurídicos.

## Executando

1. Instale as dependências necessárias:
   ```bash
   pip install streamlit streamlit-option-menu streamlit-calendar fpdf openpyxl
   ```
2. Execute a aplicação com:
   ```bash
   streamlit run app.py
   ```

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
