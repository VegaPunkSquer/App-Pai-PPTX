class Idiomas {
  static String idiomaAtual = "pt";

  static void setIdioma(String sigla) {
    idiomaAtual = sigla;
  }

  static String tr(String chave) {
    // Se não achar a chave, retorna a própria chave (mesma lógica do seu Python)
    return _dicionario[idiomaAtual]?[chave] ?? chave;
  }

  static const Map<String, Map<String, String>> _dicionario = {
    "pt": {
      "btn_conta": "Minha Conta",
      "cfg_title": "⚙️ Configurações do App",
      "cfg_tab_lic": "Licença",
      "cfg_tab_ia": "Inteligência Artificial",
      "cfg_tab_vis": "Aparência",
      "auth_log_title": "Já tem uma conta? Acesse:",
      "auth_email": "E-mail",
      "auth_senha": "Senha",
      "auth_btn_entrar": "Entrar",
      "cfg_btn_salvar": "Salvar Configurações",
      "cfg_status_lic": "Status da Licença atual:",
      "lic_free": "FREE (Edição Manual)",
      "lic_byok": "BYOK (Sua Chave)",
      "lic_saas": "SAAS (Chave Embutida)",
      "txt_tema_lock": "🔒 Inteligência Artificial bloqueada (Licença FREE).\n\nVá na aba Licença, escolha um plano e clique em Salvar.",
      "cfg_aviso_saas": "✅ Licença SaaS Ativa\nO motor principal está liberado.",
      "cfg_chk_gemini": "🔵 Usar Google Gemini (Padrão)",
      "cfg_lbl_key_gemini": "Chave de API Gemini (BYOK):",
      "cfg_chk_cf": "🟠 Usar Cloudflare Workers AI",
      "cfg_lbl_acc_cf": "Cloudflare Account ID (BYOK):",
      "cfg_lbl_tok_cf": "Cloudflare API Token (BYOK):",
      "cfg_lbl_tema": "Tema do Aplicativo:",
      "tema_escuro": "Escuro",
      "tema_claro": "Claro",
      "cfg_lbl_idioma": "Idioma / Language:"
    },
    "en": {
      "btn_conta": "My Account",
      "cfg_title": "⚙️ App Settings",
      "cfg_tab_lic": "License",
      "cfg_tab_ia": "Artificial Intelligence",
      "cfg_tab_vis": "Appearance",
      "auth_log_title": "Already have an account? Sign in:",
      "auth_email": "E-mail",
      "auth_senha": "Password",
      "auth_btn_entrar": "Sign In",
      "cfg_btn_salvar": "Save Settings",
      "cfg_status_lic": "Current License Status:",
      "lic_free": "FREE (Manual Edit)",
      "lic_byok": "BYOK (Your Key)",
      "lic_saas": "SAAS (Built-in Key)",
      "txt_tema_lock": "🔒 Smart Generation locked (FREE License).\n\nGo to the License tab, choose a plan and click Save.",
      "cfg_aviso_saas": "✅ SaaS License Active\nThe main engine is unlocked.",
      "cfg_chk_gemini": "🔵 Use Google Gemini (Default)",
      "cfg_lbl_key_gemini": "Gemini API Key (BYOK):",
      "cfg_chk_cf": "🟠 Use Cloudflare Workers AI",
      "cfg_lbl_acc_cf": "Cloudflare Account ID (BYOK):",
      "cfg_lbl_tok_cf": "Cloudflare API Token (BYOK):",
      "cfg_lbl_tema": "App Theme:",
      "tema_escuro": "Dark",
      "tema_claro": "Light",
      "cfg_lbl_idioma": "Language / Idioma:"
    }
  };
}