// ignore_for_file: deprecated_member_use, use_build_context_synchronously
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vegaslides/provider/theme_provider.dart';
import 'package:vegaslides/utils/idiomas.dart';
import 'package:vegaslides/provider/auth_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vegaslides/screens/loja_screen.dart';
import 'package:vegaslides/services/api_service.dart';

class ConfigScreen extends StatefulWidget {
  const ConfigScreen({super.key});

  @override
  State<ConfigScreen> createState() => _ConfigScreenState();
}

class _ConfigScreenState extends State<ConfigScreen> {
  String _licencaAtual = 'FREE';
  String _iaProvider = 'gemini';
  String _posGeracaoAcao = 'sistema'; // 'pasta' ou 'sistema'

  // Controladores de Conta
  final _emailController = TextEditingController();
  final _senhaController = TextEditingController();
  bool _senhaOculta = true;
  bool _carregandoLogin = false;

  // Estado do Perfil na Nuvem
  Map<String, dynamic>? _dadosPerfil;
  bool _carregandoPerfil = false;

  // Controladores das Chaves de IA
  final _geminiKeyController = TextEditingController();
  final _cfAccountController = TextEditingController();
  final _cfTokenController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _carregarMemoria();
    _carregarPerfilServidor();
  }

  Future<void> _carregarMemoria() async {
    final prefs = await SharedPreferences.getInstance();
    if (!mounted) return;
    setState(() {
      String licencaSalva = prefs.getString('vega_license') ?? 'FREE';
      if (licencaSalva.contains('SAAS')) {
        _licencaAtual = 'SAAS';
      } else if (licencaSalva.contains('BYOK')) {
        _licencaAtual = 'BYOK';
      } else {
        _licencaAtual = 'FREE';
      }

      _iaProvider = prefs.getString('vega_provider') ?? 'gemini';
      _posGeracaoAcao = prefs.getString('vega_pos_geracao') ?? 'sistema';
      _geminiKeyController.text = prefs.getString('vega_api_key') ?? '';
      _cfAccountController.text = prefs.getString('vega_cf_account') ?? '';
      _cfTokenController.text = prefs.getString('vega_cf_token') ?? '';
    });
  }

  Future<void> _carregarPerfilServidor() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    if (!auth.isAuth || auth.token == null) return;

    setState(() => _carregandoPerfil = true);
    final dados = await ApiService.obterPerfil(auth.token!);
    if (!mounted) return;

    setState(() {
      _dadosPerfil = dados;
      _carregandoPerfil = false;
      if (dados.containsKey('plano')) {
        final plano = dados['plano'].toString().toUpperCase();
        if (plano != 'FREE' && plano.isNotEmpty) {
          _licencaAtual = plano.contains('BYOK') ? 'BYOK' : 'SAAS';
          auth.atualizarLicenca(_licencaAtual);
        }
      }
    });
  }

  @override
  void dispose() {
    _emailController.dispose();
    _senhaController.dispose();
    _geminiKeyController.dispose();
    _cfAccountController.dispose();
    _cfTokenController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          title: Text(Idiomas.tr('cfg_title'), style: const TextStyle(fontWeight: FontWeight.bold)),
          elevation: 0,
          bottom: TabBar(
            isScrollable: true,
            indicatorColor: const Color(0xFF0078D7), 
            labelColor: const Color(0xFF0078D7),
            unselectedLabelColor: Theme.of(context).brightness == Brightness.dark ? Colors.white54 : Colors.black54,
            tabs: [
              Tab(icon: const Icon(Icons.person), text: Idiomas.tr('btn_conta')),
              Tab(icon: const Icon(Icons.credit_card), text: Idiomas.tr('cfg_tab_lic')),
              Tab(icon: const Icon(Icons.psychology), text: Idiomas.tr('cfg_tab_ia')),
              Tab(icon: const Icon(Icons.palette), text: Idiomas.tr('cfg_tab_vis')),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildAbaConta(),
            _buildAbaLicenca(),
            _buildAbaIA(),
            _buildAbaAparencia(themeProvider),
          ],
        ),
        bottomNavigationBar: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: () {
                final apiKey = _geminiKeyController.text.trim();
                final cfAcc = _cfAccountController.text.trim();
                final cfTok = _cfTokenController.text.trim();
                _salvarConfiguracoes(apiKey, cfAcc, cfTok);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0078d7),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: Text(Idiomas.tr('cfg_btn_salvar'), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 16)),
            ),
          ),
        ),
      ),
    );
  }

  // ==========================================
  // ABA 1: CONTA (MINHA CONTA / LOGIN)
  // ==========================================
  Widget _buildAbaConta() {
    final authProvider = Provider.of<AuthProvider>(context);

    if (authProvider.isAuth) {
      if (_carregandoPerfil && _dadosPerfil == null) {
        return const Center(child: CircularProgressIndicator(color: Color(0xFF0078D7)));
      }

      final nome = _dadosPerfil?['nome'] ?? 'Usuário VegaTech';
      final email = _dadosPerfil?['email'] ?? 'Conectado';
      final cpf = _dadosPerfil?['documento'] ?? '-';
      final criadoEm = _dadosPerfil?['criado_em'] ?? '-';
      final plano = _dadosPerfil?['plano'] ?? _licencaAtual;
      final fotoB64 = _dadosPerfil?['foto'];

      return SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const SizedBox(height: 10),
            // Avatar Circular com Borda Neon Azul (#0078D7)
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFF0078D7), width: 3),
              ),
              child: ClipOval(
                child: Builder(
                  builder: (context) {
                    if (fotoB64 != null && fotoB64.toString().isNotEmpty) {
                      try {
                        String cleanB64 = fotoB64.toString().trim();
                        if (cleanB64.contains(',')) {
                          cleanB64 = cleanB64.split(',').last;
                        }
                        cleanB64 = cleanB64.replaceAll('\n', '').replaceAll('\r', '');
                        return Image.memory(
                          base64Decode(cleanB64),
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) => const Icon(Icons.person, size: 60, color: Colors.grey),
                        );
                      } catch (e) {
                        return const Icon(Icons.person, size: 60, color: Colors.grey);
                      }
                    }
                    return const Icon(Icons.person, size: 60, color: Colors.grey);
                  },
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Card de Dados da Conta
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF222222),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF444444)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'DADOS DA CONTA',
                    style: TextStyle(color: Color(0xFF0078D7), fontWeight: FontWeight.bold, fontSize: 13, letterSpacing: 1),
                  ),
                  const SizedBox(height: 12),
                  Text('Nome: $nome', style: const TextStyle(color: Colors.white, fontSize: 14)),
                  const SizedBox(height: 6),
                  Text('E-mail: $email', style: const TextStyle(color: Color(0xFFCCCCCC), fontSize: 14)),
                  const SizedBox(height: 6),
                  Text('CPF/CNPJ: $cpf', style: const TextStyle(color: Color(0xFFAAAAAA), fontSize: 14)),
                  const SizedBox(height: 6),
                  Text('Membro desde: $criadoEm', style: const TextStyle(color: Color(0xFF888888), fontSize: 13)),
                  const SizedBox(height: 10),
                  Text(
                    'Plano: $plano',
                    style: const TextStyle(color: Color(0xFF28A745), fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Card de Segurança
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF222222),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF444444)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'SEGURANÇA',
                    style: TextStyle(color: Color(0xFFAAAAAA), fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 1),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => _recuperarSenhaModal(context, email),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF333333),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                          side: const BorderSide(color: Color(0xFF555555)),
                        ),
                      ),
                      child: const Text('Trocar Minha Senha', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Botão de Logout
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () async {
                  await authProvider.fazerLogout();
                  if (!mounted) return;
                  setState(() {
                    _dadosPerfil = null;
                    _licencaAtual = 'FREE';
                  });
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Você saiu da sua conta.')),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFA8201A),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: const Text('Sair da Conta', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 15)),
              ),
            ),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(Idiomas.tr('auth_log_title'), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: _inputDecoration(Idiomas.tr('auth_email'), Icons.email),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _senhaController,
            obscureText: _senhaOculta,
            decoration: _inputDecoration(
              Idiomas.tr('auth_senha'),
              Icons.lock,
              suffix: IconButton(
                icon: Icon(_senhaOculta ? Icons.visibility : Icons.visibility_off, color: Colors.grey),
                onPressed: () => setState(() => _senhaOculta = !_senhaOculta),
              ),
            ),
          ),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton(
              onPressed: () => _recuperarSenhaModal(context, _emailController.text),
              child: const Text('Esqueceu a senha?', style: TextStyle(color: Color(0xFF0078D7))),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _carregandoLogin ? null : () async {
              setState(() => _carregandoLogin = true);
              try {
                await authProvider.fazerLogin(
                  _emailController.text.trim(),
                  _senhaController.text,
                );
                
                if (!mounted) return;
                await _carregarPerfilServidor();

                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Login efetuado com sucesso!'), backgroundColor: Colors.green),
                );
              } catch (e) {
                if (!mounted) return;
                showDialog(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Erro de Autenticação'),
                    content: Text(e.toString().replaceAll('Exception: ', '')),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(ctx),
                        child: const Text('OK'),
                      ),
                    ],
                  ),
                );
              } finally {
                if (mounted) setState(() => _carregandoLogin = false);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0078d7),
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: _carregandoLogin
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                  )
                : Text(Idiomas.tr('auth_btn_entrar'), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
          ),
        ],
      ),
    );
  }

  // ==========================================
  // ABA 2: LICENÇA
  // ==========================================
  Widget _buildAbaLicenca() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('💳 GESTÃO DE PLANOS E ASSINATURAS', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          Text(
            'Selecione a licença desejada abaixo para liberar a geração de apresentações. O plano SAAS ELITE desbloqueia a Inteligência Artificial da Cloudflare, enquanto o SAAS Padrão usa o Google Gemini.\n\n(Escolha o plano e clique em Salvar para abrir a loja)',
            style: TextStyle(color: Theme.of(context).brightness == Brightness.dark ? Colors.white70 : Colors.black87),
          ),
          const SizedBox(height: 24),
          DropdownButtonFormField<String>(
            value: _licencaAtual,
            decoration: _inputDecoration(Idiomas.tr('cfg_status_lic'), null),
            items: [
              DropdownMenuItem(value: 'FREE', child: Text(Idiomas.tr('lic_free'))),
              DropdownMenuItem(value: 'BYOK', child: Text(Idiomas.tr('lic_byok'))),
              DropdownMenuItem(value: 'SAAS', child: Text(Idiomas.tr('lic_saas'))),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _licencaAtual = val);
            },
          ),
        ],
      ),
    );
  }

  // ==========================================
  // ABA 3: INTELIGÊNCIA ARTIFICIAL
  // ==========================================
  Widget _buildAbaIA() {
    if (_licencaAtual == 'FREE') {
      final isDark = Theme.of(context).brightness == Brightness.dark;
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Text(
            Idiomas.tr('txt_tema_lock'),
            textAlign: TextAlign.center,
            style: TextStyle(color: isDark ? Colors.white54 : Colors.black54, fontSize: 16),
          ),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (_licencaAtual == 'SAAS') ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1), 
                borderRadius: BorderRadius.circular(8), 
                border: Border.all(color: Colors.green)
              ),
              child: Text(Idiomas.tr('cfg_aviso_saas'), style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 24),
          ],
          
          RadioListTile(
            title: Text(Idiomas.tr('cfg_chk_gemini')),
            value: 'gemini',
            groupValue: _iaProvider,
            activeColor: const Color(0xFF0078D7),
            onChanged: (val) => setState(() => _iaProvider = val.toString()),
          ),
          
          if (_iaProvider == 'gemini' && _licencaAtual == 'BYOK')
            Padding(
              padding: const EdgeInsets.only(left: 16, right: 16, bottom: 16),
              child: TextFormField(
                controller: _geminiKeyController,
                decoration: _inputDecoration(Idiomas.tr('cfg_lbl_key_gemini'), Icons.key)
              ),
            ),

          RadioListTile(
            title: Text(Idiomas.tr('cfg_chk_cf')),
            value: 'cloudflare',
            groupValue: _iaProvider,
            activeColor: const Color(0xFF0078D7),
            onChanged: (val) => setState(() => _iaProvider = val.toString()),
          ),
          
          if (_iaProvider == 'cloudflare' && _licencaAtual == 'BYOK') ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: TextFormField(
                controller: _cfAccountController,
                decoration: _inputDecoration(Idiomas.tr('cfg_lbl_acc_cf'), Icons.badge)
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: TextFormField(
                controller: _cfTokenController,
                obscureText: true,
                decoration: _inputDecoration(Idiomas.tr('cfg_lbl_tok_cf'), Icons.key)
              ),
            ),
          ],
        ],
      ),
    );
  }

  // ==========================================
  // ABA 4: APARÊNCIA
  // ==========================================
  Widget _buildAbaAparencia(ThemeProvider themeProvider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            value: themeProvider.isDarkMode ? 'Escuro' : 'Claro',
            decoration: _inputDecoration(Idiomas.tr('cfg_lbl_tema'), Icons.brightness_6),
            items: [
              DropdownMenuItem(value: 'Escuro', child: Text(Idiomas.tr('tema_escuro'))),
              DropdownMenuItem(value: 'Claro', child: Text(Idiomas.tr('tema_claro'))),
            ],
            onChanged: (val) {
              if (val != null) themeProvider.toggleTheme(val == 'Escuro');
            },
          ),
          const SizedBox(height: 24),
          DropdownButtonFormField<String>(
            value: Idiomas.idiomaAtual,
            decoration: _inputDecoration(Idiomas.tr('cfg_lbl_idioma'), Icons.language),
            items: const [
              DropdownMenuItem(value: 'pt', child: Text('Português')),
              DropdownMenuItem(value: 'en', child: Text('English')),
            ],
            onChanged: (val) {
              if (val != null) {
                setState(() {
                  Idiomas.setIdioma(val);
                });
              }
            },
          ),
          const SizedBox(height: 24),
          DropdownButtonFormField<String>(
            value: _posGeracaoAcao,
            isExpanded: true,
            decoration: _inputDecoration('Ação ao Concluir Geração:', Icons.file_present),
            items: const [
              DropdownMenuItem(
                value: 'sistema',
                child: Text(
                  '⚡ Abrir com Visualizador (PowerPoint / Office)',
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              DropdownMenuItem(
                value: 'pasta',
                child: Text(
                  '📁 Abrir a Pasta Downloads',
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _posGeracaoAcao = val);
            },
          ),
        ],
      ),
    );
  }

  // ==========================================
  // O MAESTRO DO FLUXO (LOGIN -> CHECAGEM -> LOJA)
  // ==========================================
  Future<void> _salvarConfiguracoes(String apiKey, String cfAcc, String cfTok) async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final prefs = await SharedPreferences.getInstance();
    String licencaSalva = prefs.getString('vega_license') ?? 'FREE';

    if (_licencaAtual == 'BYOK' || _licencaAtual == 'SAAS') {
      if (!auth.isAuth) {
        final logou = await _mostrarModalAuth(auth);
        if (!mounted) return;
        
        if (logou != true) {
          setState(() => _licencaAtual = licencaSalva);
          return;
        }
      }

      bool byokAtivo = prefs.getBool('vega_byok_ativo') ?? false;
      bool saasPadraoAtivo = prefs.getBool('vega_saas_padrao') ?? false;
      bool saasEliteAtivo = prefs.getBool('vega_saas_elite') ?? false;

      bool temAcesso = false;
      if (_licencaAtual == 'BYOK' && byokAtivo) temAcesso = true;
      if (_licencaAtual == 'SAAS' && (saasPadraoAtivo || saasEliteAtivo)) temAcesso = true;

      if (!temAcesso) {
        final resultado = await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => LojaScreen(tokenCliente: auth.token!, filtroLoja: _licencaAtual),
          ),
        );

        if (!mounted) return;

        if (resultado != null && resultado is String) {
          final nomePlanoAlto = resultado.toUpperCase();
          if (nomePlanoAlto.contains('ELITE')) {
            await prefs.setBool('vega_saas_elite', true);
          } else if (nomePlanoAlto.contains('SAAS')) {
            await prefs.setBool('vega_saas_padrao', true);
          } else if (nomePlanoAlto.contains('BYOK')) {
            await prefs.setBool('vega_byok_ativo', true);
          }
          await _carregarPerfilServidor();
        } else {
          setState(() => _licencaAtual = licencaSalva);
          return;
        }
      }
    }

    await _gravarTudoEFechar(prefs, _licencaAtual, apiKey, cfAcc, cfTok);
  }

  // ==========================================
  // MODAL DE LOGIN/CADASTRO INTELIGENTE COM OLHINHO
  // ==========================================
  Future<bool?> _mostrarModalAuth(AuthProvider auth) {
    final nomeCtrl = TextEditingController();
    final emailCtrl = TextEditingController();
    final senhaCtrl = TextEditingController();
    bool senhaOcultaLogin = true;
    bool senhaOcultaCad = true;
    bool carregando = false;

    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) {
          return Dialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: DefaultTabController(
              length: 2,
              child: Container(
                constraints: const BoxConstraints(maxHeight: 480),
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    const Text('Acesso Premium', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    const Text('Você precisa de uma conta para habilitar este plano.', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
                    const TabBar(
                      tabs: [Tab(text: "Login"), Tab(text: "Cadastrar")],
                      indicatorColor: Color(0xFF0078D7),
                      labelColor: Color(0xFF0078D7),
                    ),
                    Expanded(
                      child: TabBarView(
                        children: [
                          ListView(
                            padding: const EdgeInsets.only(top: 16),
                            children: [
                              TextField(controller: emailCtrl, decoration: const InputDecoration(labelText: 'E-mail', border: OutlineInputBorder())),
                              const SizedBox(height: 12),
                              TextField(
                                controller: senhaCtrl,
                                obscureText: senhaOcultaLogin,
                                decoration: InputDecoration(
                                  labelText: 'Senha',
                                  border: const OutlineInputBorder(),
                                  suffixIcon: IconButton(
                                    icon: Icon(senhaOcultaLogin ? Icons.visibility : Icons.visibility_off, color: Colors.grey),
                                    onPressed: () => setModalState(() => senhaOcultaLogin = !senhaOcultaLogin),
                                  ),
                                ),
                              ),
                              Align(
                                alignment: Alignment.centerRight,
                                child: TextButton(
                                  onPressed: () => _recuperarSenhaModal(ctx, emailCtrl.text),
                                  child: const Text('Esqueceu a senha?', style: TextStyle(color: Color(0xFF0078D7))),
                                ),
                              ),
                              const SizedBox(height: 8),
                              ElevatedButton(
                                onPressed: carregando ? null : () async {
                                  setModalState(() => carregando = true);
                                  try {
                                    await auth.fazerLogin(emailCtrl.text.trim(), senhaCtrl.text);
                                    if (ctx.mounted) {
                                      await _carregarPerfilServidor();
                                      Navigator.pop(ctx, true);
                                    }
                                  } catch (e) {
                                    if (ctx.mounted) {
                                      ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: Colors.red));
                                    }
                                  } finally {
                                    setModalState(() => carregando = false);
                                  }
                                },
                                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0078D7)),
                                child: carregando ? const CircularProgressIndicator(color: Colors.white) : const Text('Entrar', style: TextStyle(color: Colors.white)),
                              )
                            ],
                          ),
                          ListView(
                            padding: const EdgeInsets.only(top: 16),
                            children: [
                              TextField(controller: nomeCtrl, decoration: const InputDecoration(labelText: 'Nome', border: OutlineInputBorder())),
                              const SizedBox(height: 12),
                              TextField(controller: emailCtrl, decoration: const InputDecoration(labelText: 'E-mail', border: OutlineInputBorder())),
                              const SizedBox(height: 12),
                              TextField(
                                controller: senhaCtrl,
                                obscureText: senhaOcultaCad,
                                decoration: InputDecoration(
                                  labelText: 'Senha',
                                  border: const OutlineInputBorder(),
                                  suffixIcon: IconButton(
                                    icon: Icon(senhaOcultaCad ? Icons.visibility : Icons.visibility_off, color: Colors.grey),
                                    onPressed: () => setModalState(() => senhaOcultaCad = !senhaOcultaCad),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton(
                                onPressed: carregando ? null : () async {
                                  setModalState(() => carregando = true);
                                  try {
                                    await auth.fazerCadastro(nomeCtrl.text.trim(), emailCtrl.text.trim(), senhaCtrl.text);
                                    if (ctx.mounted) {
                                      await _carregarPerfilServidor();
                                      Navigator.pop(ctx, true);
                                    }
                                  } catch (e) {
                                    if (ctx.mounted) {
                                      ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: Colors.red));
                                    }
                                  } finally {
                                    setModalState(() => carregando = false);
                                  }
                                },
                                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF28A745)),
                                child: carregando ? const CircularProgressIndicator(color: Colors.white) : const Text('Criar Conta', style: TextStyle(color: Colors.white)),
                              )
                            ],
                          ),
                        ],
                      ),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, false),
                      child: const Text('Cancelar', style: TextStyle(color: Colors.red)),
                    )
                  ],
                ),
              ),
            ),
          );
        }
      ),
    );
  }

  Future<void> _gravarTudoEFechar(SharedPreferences prefs, String licencaDefinitiva, String apiKey, String cfAcc, String cfTok) async {
    await prefs.setString('vega_license', licencaDefinitiva);
    await prefs.setString('vega_pos_geracao', _posGeracaoAcao);
    
    final auth = Provider.of<AuthProvider>(context, listen: false);
    auth.atualizarLicenca(licencaDefinitiva);
    
    await prefs.setString('vega_provider', _iaProvider);
    await prefs.setString('vega_api_key', apiKey);
    await prefs.setString('vega_cf_account', cfAcc);
    await prefs.setString('vega_cf_token', cfTok);
    
    if (!mounted) return;
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('${Idiomas.tr('cfg_btn_salvar')} OK!'), backgroundColor: Colors.green),
    );
    Navigator.pop(context);
  }

  // ==========================================
  // MODAL DE RECUPERAÇÃO EM 2 ETAPAS (CÓDIGO DE 6 DÍGITOS)
  // ==========================================
  Future<void> _recuperarSenhaModal(BuildContext context, String emailAtual) async {
    final emailRecCtrl = TextEditingController(text: emailAtual);
    final codigoCtrl = TextEditingController();
    final novaSenhaCtrl = TextEditingController();
    bool etapaCodigo = false;
    bool enviando = false;
    bool novaSenhaOculta = true;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          title: Text(etapaCodigo ? 'Redefinir Senha' : 'Recuperar Senha', style: const TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (!etapaCodigo) ...[
                  const Text('Digite seu e-mail cadastrado para receber o código de verificação:'),
                  const SizedBox(height: 12),
                  TextField(controller: emailRecCtrl, decoration: const InputDecoration(labelText: 'E-mail', border: OutlineInputBorder())),
                ] else ...[
                  const Text('Digite o código de 6 dígitos enviado para seu e-mail e sua nova senha:'),
                  const SizedBox(height: 12),
                  TextField(
                    controller: codigoCtrl,
                    maxLength: 6,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Código de 6 Dígitos', border: OutlineInputBorder(), counterText: ""),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: novaSenhaCtrl,
                    obscureText: novaSenhaOculta,
                    decoration: InputDecoration(
                      labelText: 'Nova Senha',
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        icon: Icon(novaSenhaOculta ? Icons.visibility : Icons.visibility_off, color: Colors.grey),
                        onPressed: () => setModalState(() => novaSenhaOculta = !novaSenhaOculta),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar', style: TextStyle(color: Colors.red))),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: etapaCodigo ? const Color(0xFF28A745) : const Color(0xFF0078D7),
              ),
              onPressed: enviando
                  ? null
                  : () async {
                      if (!etapaCodigo) {
                        final email = emailRecCtrl.text.trim();
                        if (email.isEmpty) return;
                        setModalState(() => enviando = true);
                        try {
                          await ApiService.recuperarSenha(email);
                          setModalState(() {
                            etapaCodigo = true;
                            enviando = false;
                          });
                          if (ctx.mounted) {
                            ScaffoldMessenger.of(ctx).showSnackBar(
                              const SnackBar(content: Text('Código de 6 dígitos enviado! Verifique seu e-mail.'), backgroundColor: Colors.green),
                            );
                          }
                        } catch (e) {
                          setModalState(() => enviando = false);
                          if (ctx.mounted) {
                            ScaffoldMessenger.of(ctx).showSnackBar(
                              SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: Colors.red),
                            );
                          }
                        }
                      } else {
                        final cod = codigoCtrl.text.trim();
                        final nova = novaSenhaCtrl.text;
                        if (cod.isEmpty || nova.isEmpty) return;
                        setModalState(() => enviando = true);
                        try {
                          await ApiService.confirmarRecuperacaoSenha(emailRecCtrl.text.trim(), cod, nova);
                          if (ctx.mounted) {
                            Navigator.pop(ctx);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Senha alterada com sucesso! Você já pode entrar.'), backgroundColor: Colors.green),
                            );
                          }
                        } catch (e) {
                          setModalState(() => enviando = false);
                          if (ctx.mounted) {
                            ScaffoldMessenger.of(ctx).showSnackBar(
                              SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: Colors.red),
                            );
                          }
                        }
                      }
                    },
              child: enviando
                  ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : Text(etapaCodigo ? 'Confirmar Senha' : 'Enviar Código', style: const TextStyle(color: Colors.white)),
            )
          ],
        ),
      ),
    );
  }

  // ==========================================
  // WIDGET PADRÃO VEGATECH COM SUFFIX
  // ==========================================
  InputDecoration _inputDecoration(String label, IconData? icon, {Widget? suffix}) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return InputDecoration(
      labelText: label,
      prefixIcon: icon != null ? Icon(icon) : null,
      suffixIcon: suffix,
      filled: true,
      fillColor: isDark ? const Color(0xFF1A1A1A) : Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF0078D7), width: 2)),
    );
  }
}