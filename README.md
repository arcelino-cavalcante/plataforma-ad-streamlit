# Plataforma AD Streamlit

Este repositório contém um painel em [Streamlit](https://streamlit.io/) para gerenciamento de casos jurídicos.

## Executando

1. Instale as dependências necessárias:
   ```bash
   pip install streamlit streamlit-option-menu streamlit-calendar fpdf openpyxl \
       gspread google-api-python-client google-auth
   ```
2. Execute a aplicação com:
   ```bash
   streamlit run app.py
   ```

Para persistir os dados em planilhas do Google Sheets e armazenar documentos no
Google Drive, é necessário criar credenciais de uma **conta de serviço** no
[Google Cloud Console](https://console.cloud.google.com/). Habilite as APIs
**Google Sheets API** e **Google Drive API**, faça o download do arquivo JSON de
credenciais e defina a variável de ambiente `GOOGLE_CREDS` apontando para esse
arquivo. Opcionalmente, defina `GOOGLE_SHEETS_FILE` com o nome da planilha e
`GOOGLE_DRIVE_ROOT` com o nome da pasta raiz no Drive.

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
