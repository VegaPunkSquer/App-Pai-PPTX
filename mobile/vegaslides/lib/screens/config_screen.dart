// ignore_for_file: deprecated_member_use
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vegaslides/provider/theme_provider.dart';
import 'package:vegaslides/utils/idiomas.dart';
import 'package:vegaslides/provider/auth_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:vegaslides/screens/loja_screen.dart';

class ConfigScreen extends StatefulWidget {
  const ConfigScreen({super.key});

  @override
  State<ConfigScreen> createState() => _ConfigScreenState();
}

class _ConfigScreenState extends State<ConfigScreen> {
  String _licencaAtual = 'FREE';
  String _iaProvider = 'gemini';

  // Controladores de Conta
  final _emailController = TextEditingController();
  final _senhaController = TextEditingController();
  bool _carregandoLogin = false;

  // Controladores das Chaves de IA
  final _geminiKeyController = TextEditingController();
  final _cfAccountController = TextEditingController();
  final _cfTokenController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _carregarMemoria();
  }

  // CURA A AMNÉSIA: Filtra o lixo antigo e puxa o que tá salvo
  Future<void> _carregarMemoria() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      // O Filtro: Garante que o Flutter só leia a sigla exata que o Dropdown aceita
      String licencaSalva = prefs.getString('vega_license') ?? 'FREE';
      if (licencaSalva.contains('SAAS')) {
        _licencaAtual = 'SAAS';
      } else if (licencaSalva.contains('BYOK')) {
        _licencaAtual = 'BYOK';
      } else {
        _licencaAtual = 'FREE';
      }

      _iaProvider = prefs.getString('vega_provider') ?? 'gemini';
      _geminiKeyController.text = prefs.getString('vega_api_key') ?? '';
      _cfAccountController.text = prefs.getString('vega_cf_account') ?? '';
      _cfTokenController.text = prefs.getString('vega_cf_token') ?? '';
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
            indicatorColor: const Color(0xFF8B5CF6), 
            labelColor: const Color(0xFF8B5CF6),
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
  // ABA 1: CONTA (COM INTEGRAÇÃO API)
  // ==========================================
  Widget _buildAbaConta() {
    final authProvider = Provider.of<AuthProvider>(context);

    if (authProvider.isAuth) {
      return Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.check_circle, color: Colors.green, size: 64),
            const SizedBox(height: 16),
            const Text(
              'Conta Conectada com Sucesso!',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () async {
                await authProvider.fazerLogout();
                if (!mounted) return;
                setState(() {});
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Logout realizado com sucesso.')),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.redAccent,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text('Sair da Conta (Logout)', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
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
            obscureText: true,
            decoration: _inputDecoration(Idiomas.tr('auth_senha'), Icons.lock),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _carregandoLogin ? null : () async {
              setState(() => _carregandoLogin = true);
              try {
                await authProvider.fazerLogin(
                  _emailController.text.trim(),
                  _senhaController.text,
                );
                
                if (!mounted) return;

                final prefs = await SharedPreferences.getInstance();
                final saasPadrao = prefs.getBool('vega_saas_padrao') ?? false;
                final saasElite = prefs.getBool('vega_saas_elite') ?? false;
                final byok = prefs.getBool('vega_byok_ativo') ?? false;

                if (!mounted) return;

                setState(() {
                  if (saasElite || saasPadrao) {
                    _licencaAtual = 'SAAS';
                  } else if (byok) {
                    _licencaAtual = 'BYOK';
                  }
                });

                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Login efetuado! Licença carregada.'), backgroundColor: Colors.green),
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
          Text('💳 GESTÃO DE PLANOS E ASSINATURAS', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
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
              setState(() => _licencaAtual = val!);
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
            activeColor: const Color(0xFF8B5CF6),
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
            activeColor: const Color(0xFF8B5CF6),
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
              themeProvider.toggleTheme(val == 'Escuro');
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
              setState(() {
                Idiomas.setIdioma(val!);
              });
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
          if (nomePlanoAlto.contains('ELITE')) await prefs.setBool('vega_saas_elite', true);
          else if (nomePlanoAlto.contains('SAAS')) await prefs.setBool('vega_saas_padrao', true);
          else if (nomePlanoAlto.contains('BYOK')) await prefs.setBool('vega_byok_ativo', true);
        } else {
          setState(() => _licencaAtual = licencaSalva);
          return;
        }
      }
    }

    await _gravarTudoEFechar(prefs, _licencaAtual, apiKey, cfAcc, cfTok);
  }

  // ==========================================
  // O MODAL DE LOGIN/CADASTRO INTELIGENTE
  // ==========================================
  Future<bool?> _mostrarModalAuth(AuthProvider auth) {
    final nomeCtrl = TextEditingController();
    final emailCtrl = TextEditingController();
    final senhaCtrl = TextEditingController();
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
                constraints: const BoxConstraints(maxHeight: 450),
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    const Text('Acesso Premium', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    const Text('Você precisa de uma conta para habilitar este plano.', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
                    const TabBar(
                      tabs: [Tab(text: "Login"), Tab(text: "Cadastrar")],
                      indicatorColor: Colors.blue,
                      labelColor: Colors.blue,
                    ),
                    Expanded(
                      child: TabBarView(
                        children: [
                          ListView(
                            padding: const EdgeInsets.only(top: 16),
                            children: [
                              TextField(controller: emailCtrl, decoration: const InputDecoration(labelText: 'E-mail', border: OutlineInputBorder())),
                              const SizedBox(height: 12),
                              TextField(controller: senhaCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Senha', border: OutlineInputBorder())),
                              const SizedBox(height: 16),
                              ElevatedButton(
                                onPressed: carregando ? null : () async {
                                  setModalState(() => carregando = true);
                                  try {
                                    await auth.fazerLogin(emailCtrl.text.trim(), senhaCtrl.text);
                                    if (ctx.mounted) {
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
                                child: carregando ? const CircularProgressIndicator(color: Colors.white) : const Text('Entrar'),
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
                              TextField(controller: senhaCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Senha', border: OutlineInputBorder())),
                              const SizedBox(height: 16),
                              ElevatedButton(
                                onPressed: carregando ? null : () async {
                                  setModalState(() => carregando = true);
                                  try {
                                    await auth.fazerCadastro(nomeCtrl.text.trim(), emailCtrl.text.trim(), senhaCtrl.text);
                                    if (ctx.mounted) {
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
                                child: carregando ? const CircularProgressIndicator(color: Colors.white) : const Text('Criar Conta'),
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
  // WIDGET PADRÃO VEGATECH
  // ==========================================
  InputDecoration _inputDecoration(String label, IconData? icon) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return InputDecoration(
      labelText: label,
      prefixIcon: icon != null ? Icon(icon) : null,
      filled: true,
      fillColor: isDark ? const Color(0xFF1A1A1A) : Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF8B5CF6), width: 2)),
    );
  }
}