// ignore_for_file: deprecated_member_use, avoid_print
import 'dart:convert';
import 'package:flutter/material.dart';
import 'config_screen.dart';
import 'selecao_imagens_modal.dart';
import 'estilizador_screen.dart';
import 'assistente_ia_dialog.dart';
import 'seletor_forma_modal.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../utils/idiomas.dart';
import 'package:provider/provider.dart';
import '../provider/auth_provider.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _promptController = TextEditingController();
  double _alturaCaixaPrompt = 130.0;
  bool _arrastandoGrip = false;

  @override
  void initState() {
    super.initState();
    _checarAvisosStartup();
    _promptController.addListener(_checarAtalhoForma);
  }

  @override
  void dispose() {
    _promptController.removeListener(_checarAtalhoForma);
    _promptController.dispose();
    super.dispose();
  }

  void _checarAtalhoForma() {
    final texto = _promptController.text;
    if (texto.contains('/forma')) {
      final limpo = texto.replaceAll('/forma', '').trim();
      _promptController.value = TextEditingValue(
        text: limpo,
        selection: TextSelection.collapsed(offset: limpo.length),
      );
      _abrirSeletorForma();
    }
  }

  Future<void> _abrirSeletorForma() async {
    final tag = await showDialog<String>(
      context: context,
      builder: (ctx) => const SeletorFormaModal(),
    );
    if (tag != null && tag.isNotEmpty) {
      final atual = _promptController.text.trim();
      final novo = atual.isEmpty ? tag : "$atual $tag";
      setState(() {
        _promptController.text = novo;
        _promptController.selection = TextSelection.collapsed(offset: novo.length);
      });
    }
  }

  Future<void> _abrirAssistenteGuiado(AuthProvider auth) async {
    if (auth.isFree) {
      _mostrarAlertaVip();
      return;
    }
    final promptGerado = await showDialog<String>(
      context: context,
      builder: (ctx) => const AssistenteIADialog(),
    );
    if (promptGerado != null && promptGerado.trim().isNotEmpty) {
      setState(() => _promptController.text = promptGerado);
      await _dispararGeracaoIA(auth);
    }
  }

  void _mostrarAlertaVip() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Recurso Premium Bloqueado'),
        content: Text(Idiomas.tr('txt_tema_lock')),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(Idiomas.tr('nov_btn_ok')),
          ),
        ],
      ),
    );
  }

  Future<void> _salvarRoteiroHistorico(String tema, List<dynamic> slides) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final List<String> histRaw = prefs.getStringList('vega_historico_roteiros') ?? [];
      final List<Map<String, dynamic>> historico =
          histRaw.map((e) => jsonDecode(e) as Map<String, dynamic>).toList();

      final agora = DateTime.now();
      final dataFmt =
          "${agora.day.toString().padLeft(2, '0')}/${agora.month.toString().padLeft(2, '0')}/${agora.year} ${agora.hour.toString().padLeft(2, '0')}:${agora.minute.toString().padLeft(2, '0')}";

      historico.add({
        "data": dataFmt,
        "tema": tema,
        "slides": slides,
      });

      while (historico.length > 5) {
        historico.removeAt(0);
      }

      await prefs.setStringList(
        'vega_historico_roteiros',
        historico.map((e) => jsonEncode(e)).toList(),
      );
    } catch (_) {}
  }

  Future<void> _abrirHistoricoSalvo(AuthProvider auth) async {
    final prefs = await SharedPreferences.getInstance();
    final List<String> histRaw = prefs.getStringList('vega_historico_roteiros') ?? [];

    if (histRaw.isEmpty) {
      if (!mounted) return;
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(Idiomas.tr('recup_vazio_titulo')),
          content: Text(Idiomas.tr('recup_vazio_msg')),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('OK')),
          ],
        ),
      );
      return;
    }

    final List<Map<String, dynamic>> itens =
        histRaw.map((e) => jsonDecode(e) as Map<String, dynamic>).toList().reversed.toList();

    if (!mounted) return;
    final escolhido = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF222222),
        title: Text(
          Idiomas.tr('recup_titulo'),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
        ),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: itens.length,
            itemBuilder: (c, i) {
              final item = itens[i];
              return Card(
                color: const Color(0xFF2C2C2C),
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  title: Text(
                    "📅 ${item['data'] ?? ''}",
                    style: const TextStyle(color: Color(0xFF0078D7), fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                  subtitle: Text(
                    "📝 ${item['tema'] ?? ''}",
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(color: Colors.white, fontSize: 13),
                  ),
                  onTap: () => Navigator.pop(ctx, item),
                ),
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(Idiomas.tr('recup_btn_cancelar'), style: const TextStyle(color: Colors.grey)),
          ),
        ],
      ),
    );

    if (escolhido != null && mounted) {
      final slidesRecup = escolhido['slides'] as List<dynamic>? ?? [];
      final temaRecup = (escolhido['tema'] ?? '').toString();
      setState(() => _promptController.text = temaRecup);

      if (slidesRecup.isNotEmpty) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (ctx) => SelecaoImagensModal(
              token: auth.token ?? '',
              slides: slidesRecup,
            ),
          ),
        );
      }
    }
  }

  Future<void> _dispararGeracaoIA(AuthProvider auth) async {
    if (auth.isFree) {
      _mostrarAlertaVip();
      return;
    }

    final tema = _promptController.text.trim();
    if (tema.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, digite o tema primeiro!'), backgroundColor: Colors.red),
      );
      return;
    }

    final nav = Navigator.of(context);
    final scaffold = ScaffoldMessenger.of(context);

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => const Center(child: CircularProgressIndicator(color: Color(0xFF8B5CF6))),
    );

    try {
      final temaParaIA =
          "$tema\n\n[CRITICAL RULE: You MUST generate the entire presentation, all text, and the speaker script strictly in the EXACT SAME LANGUAGE as the topic requested above.]";
      final slides = await ApiService.planejarApresentacao(auth.token!, temaParaIA);
      if (!mounted) return;
      nav.pop();

      if (slides.isEmpty) {
        scaffold.showSnackBar(
          const SnackBar(content: Text('A IA não retornou slides válidos.'), backgroundColor: Colors.red),
        );
        return;
      }

      await _salvarRoteiroHistorico(tema, slides);

      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (ctx) => SelecaoImagensModal(
            token: auth.token!,
            slides: slides,
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      nav.pop();
      scaffold.showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceAll('Exception: ', '')),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  // ==========================================
  // MOTOR DO MEGAFONE (AVISOS) E NOVIDADES
  // ==========================================
  Future<void> _checarAvisosStartup() async {
    final avisos = await ApiService.buscarAvisos();
    if (avisos.isEmpty) return;

    int maiorId = 0;
    for (var aviso in avisos) {
      int id = aviso['id'] ?? 0;
      if (id > maiorId) maiorId = id;
    }

    final prefs = await SharedPreferences.getInstance();
    int ultimoLido = prefs.getInt('ultimo_aviso_lido') ?? 0;

    if (maiorId > ultimoLido) {
      await prefs.setInt('ultimo_aviso_lido', maiorId);
      if (mounted) {
        _mostrarQuadroAvisos(avisos);
      }
    }
  }

  void _mostrarQuadroAvisos(List<dynamic> avisos) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF242424),
        title: Text(Idiomas.tr('avisos_titulo'), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: SizedBox(
          width: double.maxFinite,
          child: avisos.isEmpty
              ? Text(Idiomas.tr('avisos_vazio'), style: const TextStyle(color: Colors.white70))
              : ListView.builder(
                  shrinkWrap: true,
                  itemCount: avisos.length > 10 ? 10 : avisos.length,
                  itemBuilder: (c, i) {
                    final aviso = avisos[i];
                    final tipo = aviso['tipo'] ?? 'info';

                    Color corBorda = tipo == 'info'
                        ? Colors.blue
                        : tipo == 'warning'
                            ? Colors.amber
                            : tipo == 'erro'
                                ? Colors.red
                                : Colors.green;

                    return Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      decoration: BoxDecoration(
                        color: Colors.black12,
                        border: Border(left: BorderSide(color: corBorda, width: 4)),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: ListTile(
                        title: Text(aviso['titulo'] ?? 'Aviso',
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                        subtitle: Text(aviso['mensagem'] ?? '',
                            style: const TextStyle(color: Colors.white70, fontSize: 13)),
                      ),
                    );
                  },
                ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(Idiomas.tr('avisos_btn_fechar'), style: const TextStyle(color: Colors.grey)),
          )
        ],
      ),
    );
  }

  Future<void> _abrirNovidades() async {
    final dados = await ApiService.buscarNovidades();
    if (!mounted) return;

    final versao = (dados['versao_atual'] ?? 'v1.0.0').toString();
    final notasBrutas = Idiomas.idiomaAtual == 'en'
        ? (dados['notas_atualizacao_en'] ?? dados['notas_atualizacao'] ?? '')
        : (dados['notas_atualizacao'] ?? '');
    final textoFinal = notasBrutas.toString().trim().isEmpty
        ? 'Sem novidades registradas para esta versão no servidor.'
        : notasBrutas.toString();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF242424),
        title: Text(
          Idiomas.tr('nov_janela').replaceAll('{}', versao),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
        ),
        content: SingleChildScrollView(
          child: Text(
            textoFinal,
            style: const TextStyle(color: Colors.white70, fontSize: 13, height: 1.4),
          ),
        ),
        actions: [
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0078D7)),
            onPressed: () => Navigator.pop(ctx),
            child: Text(Idiomas.tr('nov_btn_ok'), style: const TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.asset('assets/splash.png', height: 28),
            const SizedBox(width: 8),
            const Text('VegaSlides', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            tooltip: Idiomas.tr('btn_novidades'),
            icon: Icon(Icons.assignment, color: isDark ? Colors.white70 : Colors.black87),
            onPressed: _abrirNovidades,
          ),
          IconButton(
            tooltip: Idiomas.tr('avisos_titulo'),
            icon: Icon(Icons.campaign, color: isDark ? Colors.amber : Colors.red),
            onPressed: () async {
              final avisos = await ApiService.buscarAvisos();
              if (mounted) _mostrarQuadroAvisos(avisos);
            },
          ),
          IconButton(
            tooltip: Idiomas.tr('cfg_title'),
            icon: Icon(Icons.settings, color: isDark ? Colors.white70 : Colors.black87),
            onPressed: () async {
              await Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ConfigScreen()),
              );
              if (mounted) setState(() {}); // Atualiza o idioma na hora ao voltar
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Botão 1: Estilizador Manual no topo (igual ao Desktop)
            ElevatedButton.icon(
              onPressed: () async {
                await Navigator.push(
                  context,
                  MaterialPageRoute(builder: (ctx) => const EstilizadorScreen()),
                );
                if (mounted) setState(() {});
              },
              icon: const Icon(Icons.folder_open, color: Colors.white),
              label: Text(
                Idiomas.tr('btn_load'),
                style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF333333),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            const SizedBox(height: 22),

            Text(
              '🧠 Motor de Criação por Inteligência Artificial:',
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.bold,
                color: Color(0xFF0078D7),
              ),
            ),
            const SizedBox(height: 10),

            // CAIXA DE PROMPT REDIMENSIONÁVEL COM PEGA VISUAL DE ESTRIAS NO CANTO INFERIOR DIREITO
            Stack(
              children: [
                Container(
                  height: _alturaCaixaPrompt,
                  decoration: BoxDecoration(
                    color: auth.isFree
                        ? (isDark ? Colors.grey.shade900 : Colors.grey.shade300)
                        : (isDark ? const Color(0xFF141414) : Colors.white),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: _arrastandoGrip
                          ? const Color(0xFF0078D7)
                          : (isDark ? const Color(0xFF333333) : Colors.grey.shade400),
                      width: _arrastandoGrip ? 2 : 1,
                    ),
                  ),
                  child: TextField(
                    controller: _promptController,
                    maxLines: null,
                    expands: true,
                    textAlignVertical: TextAlignVertical.top,
                    readOnly: auth.isFree,
                    onTap: auth.isFree ? _mostrarAlertaVip : null,
                    style: TextStyle(color: isDark ? Colors.white : Colors.black, fontSize: 15),
                    decoration: InputDecoration(
                      hintText: auth.isFree
                          ? Idiomas.tr('txt_tema_lock')
                          : 'Digite o tema para a IA criar a apresentação do zero...',
                      hintStyle: TextStyle(color: isDark ? Colors.white38 : Colors.black38),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.fromLTRB(16, 14, 24, 24),
                    ),
                  ),
                ),
                // Pega Visual no canto inferior direito (3 estrias diagonais)
                Positioned(
                  right: 2,
                  bottom: 2,
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onPanStart: (_) => setState(() => _arrastandoGrip = true),
                    onPanUpdate: (details) {
                      setState(() {
                        _alturaCaixaPrompt = (_alturaCaixaPrompt + details.delta.dy).clamp(90.0, 600.0);
                      });
                    },
                    onPanEnd: (_) => setState(() => _arrastandoGrip = false),
                    onPanCancel: () => setState(() => _arrastandoGrip = false),
                    child: Container(
                      width: 28,
                      height: 28,
                      alignment: Alignment.bottomRight,
                      padding: const EdgeInsets.all(4),
                      child: CustomPaint(
                        size: const Size(16, 16),
                        painter: _GripEstriasPainter(ativo: _arrastandoGrip),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // GRADE 2x2 DE BOTÕES DE AÇÃO DA IA (IGUAL AO DESKTOP)
            Row(
              children: [
                Expanded(
                  child: SizedBox(
                    height: 48,
                    child: ElevatedButton(
                      onPressed: () => _dispararGeracaoIA(auth),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: auth.isFree ? Colors.grey.shade700 : const Color(0xFF2B5C8F),
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      child: Text(
                        Idiomas.tr('btn_ia_completo'),
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: SizedBox(
                    height: 48,
                    child: ElevatedButton(
                      onPressed: () => _abrirAssistenteGuiado(auth),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: auth.isFree ? Colors.grey.shade700 : const Color(0xFF17A2B8),
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      child: Text(
                        Idiomas.tr('btn_guiado_completo'),
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: SizedBox(
                    height: 48,
                    child: ElevatedButton(
                      onPressed: _abrirSeletorForma,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF6F42C1),
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      child: Text(
                        Idiomas.tr('btn_smartart_completo'),
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: SizedBox(
                    height: 48,
                    child: ElevatedButton(
                      onPressed: () => _abrirHistoricoSalvo(auth),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF4A5568),
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      child: Text(
                        Idiomas.tr('btn_recuperar_completo'),
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _GripEstriasPainter extends CustomPainter {
  final bool ativo;
  _GripEstriasPainter({required this.ativo});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = ativo ? const Color(0xFF0078D7) : const Color(0xFF888888)
      ..strokeWidth = 1.8
      ..strokeCap = StrokeCap.round;

    final w = size.width;
    final h = size.height;

    canvas.drawLine(Offset(w - 2, h - 11), Offset(w - 11, h - 2), paint);
    canvas.drawLine(Offset(w - 2, h - 7), Offset(w - 7, h - 2), paint);
    canvas.drawLine(Offset(w - 2, h - 3), Offset(w - 3, h - 2), paint);
  }

  @override
  bool shouldRepaint(covariant _GripEstriasPainter oldDelegate) => oldDelegate.ativo != ativo;
}