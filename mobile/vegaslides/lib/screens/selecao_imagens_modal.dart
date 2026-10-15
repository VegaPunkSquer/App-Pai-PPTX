// ignore_for_file: use_build_context_synchronously
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:open_filex/open_filex.dart';
import '../services/api_service.dart';
import '../utils/idiomas.dart';
import 'revisor_elementos_modal.dart';

class SelecaoImagensModal extends StatefulWidget {
  final String token;
  final List<dynamic> slides;

  const SelecaoImagensModal({
    super.key,
    required this.token,
    required this.slides,
  });

  @override
  State<SelecaoImagensModal> createState() => _SelecaoImagensModalState();
}

class _SelecaoImagensModalState extends State<SelecaoImagensModal> {
  late List<String?> _imagensEscolhidas;
  bool _compilando = false;

  @override
  void initState() {
    super.initState();
    // Inicia marcando a primeira foto como padrão para cada slide se houver opção
    _imagensEscolhidas = widget.slides.map<String?>((slide) {
      final opcoes = slide['opcoes_imagens'] as List<dynamic>?;
      if (opcoes != null && opcoes.isNotEmpty) {
        return opcoes[0]['full'] as String?;
      }
      return null;
    }).toList();
  }

  Future<String?> _perguntarNomeArquivo(String sugestao) async {
    final ctrl = TextEditingController(text: sugestao);
    return showDialog<String>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: const Text('Salvar Apresentação Como', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        content: TextField(
          controller: ctrl,
          decoration: const InputDecoration(
            labelText: 'Nome do arquivo (.pptx)',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, null),
            child: Text(Idiomas.tr('recup_btn_cancelar'), style: const TextStyle(color: Colors.red)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF28A745)),
            onPressed: () {
              String nome = ctrl.text.trim();
              if (nome.isEmpty) nome = sugestao;
              if (!nome.toLowerCase().endsWith('.pptx')) nome = '$nome.pptx';
              Navigator.pop(ctx, nome);
            },
            child: const Text('Salvar', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Future<void> _finalizarECompilar() async {
    // 1. Abre o Revisor Visual de Slides (Cards e SmartArt) exatamente como no Desktop
    final slidesRevisados = await Navigator.push<List<dynamic>>(
      context,
      MaterialPageRoute(
        builder: (ctx) => RevisorElementosModal(slides: widget.slides),
      ),
    );

    if (slidesRevisados == null || !mounted) return;

    // 2. Pergunta o nome que o usuário quer dar ao arquivo
    final primeiroTitulo = (slidesRevisados.isNotEmpty ? (slidesRevisados[0]['titulo'] ?? 'Apresentacao') : 'Apresentacao')
        .toString()
        .replaceAll(RegExp(r'[^\w\s-]'), '')
        .trim()
        .replaceAll(' ', '_');
    final nomeEscolhido = await _perguntarNomeArquivo(primeiroTitulo.isEmpty ? 'Apresentacao_VegaSlides' : primeiroTitulo);
    if (nomeEscolhido == null || !mounted) return;

    setState(() => _compilando = true);

    try {
      final List<Map<String, dynamic>> payloadSlides = [];

      for (int i = 0; i < slidesRevisados.length; i++) {
        final s = slidesRevisados[i];
        payloadSlides.add({
          "titulo": s['titulo'] ?? "Slide ${i + 1}",
          "texto": s['texto'] ?? "",
          "topicos": s['topicos'] ?? [],
          "imagem_url": _imagensEscolhidas[i],
        });
      }

      final bytes = await ApiService.compilarApresentacao(widget.token, payloadSlides);

      Directory? pastaDownload = Directory('/storage/emulated/0/Download');
      if (!pastaDownload.existsSync()) {
        pastaDownload = await getExternalStorageDirectory();
      }

      final caminhoFinal = "${pastaDownload?.path ?? ''}/$nomeEscolhido";
      final arquivo = File(caminhoFinal);
      await arquivo.writeAsBytes(bytes);

      final prefs = await SharedPreferences.getInstance();
      final acao = prefs.getString('vega_pos_geracao') ?? 'sistema';

      if (!mounted) return;
      Navigator.pop(context);

      if (acao == 'pasta') {
        await OpenFilex.open(pastaDownload!.path);
      } else {
        final res = await OpenFilex.open(
          caminhoFinal,
          type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        );

        if (res.type != ResultType.done && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Salvo em: $caminhoFinal'),
              backgroundColor: Colors.amber.shade800,
            ),
          );
        }
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _compilando = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceAll('Exception: ', '')),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(Idiomas.tr('img_sel_titulo'), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        elevation: 0,
      ),
      body: _compilando
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  CircularProgressIndicator(color: Color(0xFF8B5CF6)),
                  SizedBox(height: 16),
                  Text(
                    'Baixando fotos e compilando PowerPoint...',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: widget.slides.length,
              itemBuilder: (ctx, index) {
                final slide = widget.slides[index];
                final opcoes = (slide['opcoes_imagens'] as List<dynamic>?) ?? [];
                final fotoAtual = _imagensEscolhidas[index];

                return Card(
                  margin: const EdgeInsets.only(bottom: 20),
                  color: isDark ? const Color(0xFF1E1E1E) : Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Slide ${index + 1}: ${slide['titulo'] ?? ''}',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        if (slide['texto'] != null && slide['texto'].toString().isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Text(
                            Idiomas.tr('img_sel_contexto').replaceAll('{}', slide['texto'].toString()),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(color: isDark ? Colors.white60 : Colors.black54, fontSize: 13),
                          ),
                        ],
                        const SizedBox(height: 10),
                        // Checkbox explícito de NÃO USAR IMAGEM (igual ao Desktop)
                        InkWell(
                          onTap: () {
                            setState(() {
                              if (fotoAtual == null) {
                                if (opcoes.isNotEmpty) {
                                  _imagensEscolhidas[index] = opcoes[0]['full'] as String?;
                                }
                              } else {
                                _imagensEscolhidas[index] = null;
                              }
                            });
                          },
                          child: Row(
                            children: [
                              Checkbox(
                                value: fotoAtual == null,
                                activeColor: const Color(0xFFA8201A),
                                onChanged: (val) {
                                  setState(() {
                                    if (val == true) {
                                      _imagensEscolhidas[index] = null;
                                    } else if (opcoes.isNotEmpty) {
                                      _imagensEscolhidas[index] = opcoes[0]['full'] as String?;
                                    }
                                  });
                                },
                              ),
                              Expanded(
                                child: Text(
                                  Idiomas.tr('img_sel_sem_img'),
                                  style: const TextStyle(
                                    color: Color(0xFFA8201A),
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 8),
                        SizedBox(
                          height: 110,
                          child: ListView(
                            scrollDirection: Axis.horizontal,
                            children: opcoes.map((op) {
                              final thumb = op['thumb'] as String?;
                              final full = op['full'] as String?;
                              final isSelected = fotoAtual == full;

                              return GestureDetector(
                                onTap: () {
                                  setState(() => _imagensEscolhidas[index] = full);
                                },
                                child: Container(
                                  width: 120,
                                  margin: const EdgeInsets.only(right: 10),
                                  decoration: BoxDecoration(
                                    border: Border.all(
                                      color: isSelected ? const Color(0xFF28A745) : Colors.transparent,
                                      width: isSelected ? 3 : 1,
                                    ),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Stack(
                                    fit: StackFit.expand,
                                    children: [
                                      ClipRRect(
                                        borderRadius: BorderRadius.circular(6),
                                        child: thumb != null
                                            ? Image.network(
                                                thumb,
                                                fit: BoxFit.cover,
                                                errorBuilder: (_, __, ___) => const Icon(Icons.broken_image),
                                              )
                                            : const Icon(Icons.image),
                                      ),
                                      if (isSelected)
                                        Positioned(
                                          bottom: 4,
                                          right: 4,
                                          child: Container(
                                            padding: const EdgeInsets.all(2),
                                            decoration: const BoxDecoration(
                                              color: Color(0xFF28A745),
                                              shape: BoxShape.circle,
                                            ),
                                            child: const Icon(Icons.check, color: Colors.white, size: 16),
                                          ),
                                        ),
                                    ],
                                  ),
                                ),
                              );
                            }).toList(),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton(
            onPressed: _compilando ? null : _finalizarECompilar,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF28A745),
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: Text(
              Idiomas.tr('img_sel_btn_concluir'),
              style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 15),
            ),
          ),
        ),
      ),
    );
  }
}