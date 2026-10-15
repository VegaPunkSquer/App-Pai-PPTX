// ignore_for_file: use_build_context_synchronously
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:open_filex/open_filex.dart';
import '../services/api_service.dart';
import '../utils/idiomas.dart';

class EstilizadorScreen extends StatefulWidget {
  final Uint8List? pptxBytesInicial;
  final String? nomeArquivoInicial;

  const EstilizadorScreen({
    super.key,
    this.pptxBytesInicial,
    this.nomeArquivoInicial,
  });

  @override
  State<EstilizadorScreen> createState() => _EstilizadorScreenState();
}

class _EstilizadorScreenState extends State<EstilizadorScreen> {
  Uint8List? _pptxBytes;
  String? _nomeArquivo;

  // Preset
  String _presetAtual = "Personalizado";

  // Cores
  Color _corTitulo = const Color(0xFF1E3C5A);
  Color _corCorpo = const Color(0xFF333333);
  Color _corFundoCard = const Color(0xFF2B5C8F);

  // Tipografia
  String _fonteTitulo = "Padrão do Tema";
  String _fonteCorpo = "Padrão do Tema";

  // Sliders e Toggles
  bool _habilitarEscalaImg = false;
  double _escalaImagem = 100;

  bool _habilitarEscalaTexto = false;
  double _escalaTexto = 20;

  bool _inserirNotasApresentador = true;
  bool _exibirBarraLateral = true;

  // Imagem de Fundo
  Uint8List? _fundoBytes;
  String? _nomeFundo;

  bool _processando = false;

  final List<String> _fontesDisponiveis = [
    "Padrão do Tema",
    "Arial",
    "Calibri",
    "Century Gothic",
    "Georgia",
    "Segoe UI",
    "Tahoma",
    "Times New Roman",
    "Trebuchet MS",
    "Verdana"
  ];

  @override
  void initState() {
    super.initState();
    if (widget.pptxBytesInicial != null) {
      _pptxBytes = widget.pptxBytesInicial;
      _nomeArquivo = widget.nomeArquivoInicial ?? "Apresentacao.pptx";
    }
  }

  Future<void> _selecionarPptx() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pptx'],
      withData: true,
    );

    if (result != null && result.files.single.bytes != null) {
      setState(() {
        _pptxBytes = result.files.single.bytes;
        _nomeArquivo = result.files.single.name;
      });
    }
  }

  Future<void> _selecionarImagemFundo() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.image,
      withData: true,
    );

    if (result != null && result.files.single.bytes != null) {
      setState(() {
        _fundoBytes = result.files.single.bytes;
        _nomeFundo = result.files.single.name;
      });
    }
  }

  void _aplicarPreset(String preset) {
    setState(() {
      _presetAtual = preset;
      if (preset == "Corporativo Azul") {
        _corTitulo = const Color(0xFF1E3C5A);
        _corCorpo = const Color(0xFF28323C);
        _corFundoCard = const Color(0xFFF0F8FF);
      } else if (preset == "Dark Mode Clássico") {
        _corTitulo = const Color(0xFFFFFFFF);
        _corCorpo = const Color(0xFFDCDCDC);
        _corFundoCard = const Color(0xFF2D2D2D);
      } else if (preset == "Minimalista Clean") {
        _corTitulo = const Color(0xFF000000);
        _corCorpo = const Color(0xFF323232);
        _corFundoCard = const Color(0xFFFFFFFF);
      }
    });
  }

  String _colorToHex(Color color) {
    return '#${color.value.toRadixString(16).substring(2).toUpperCase()}';
  }

  TextStyle _obterEstiloComFonte(String nomeFonte, double tamanho, Color cor, {bool bold = false}) {
    // No Android, fontes nativas do Windows usam mapeamento de famílias visuais equivalentes
    String? fontFamily;
    FontStyle fontStyle = FontStyle.normal;

    switch (nomeFonte) {
      case "Arial":
      case "Calibri":
      case "Segoe UI":
      case "Tahoma":
      case "Verdana":
        fontFamily = "sans-serif";
        break;
      case "Georgia":
      case "Times New Roman":
        fontFamily = "serif";
        break;
      case "Century Gothic":
      case "Trebuchet MS":
        fontFamily = "sans-serif-condensed";
        break;
      default:
        fontFamily = null;
    }

    return TextStyle(
      fontSize: tamanho,
      fontWeight: bold ? FontWeight.bold : FontWeight.normal,
      fontStyle: fontStyle,
      color: cor,
      fontFamily: fontFamily,
    );
  }

  void _abrirSeletorCor(String titulo, Color corAtual, Function(Color) onSelecionada) {
    final List<Color> paleta = [
      Colors.white, const Color(0xFFDCDCDC), const Color(0xFF888888), const Color(0xFF333333), Colors.black,
      const Color(0xFF1E3C5A), const Color(0xFF0078D7), const Color(0xFF2B5C8F), const Color(0xFF17A2B8),
      const Color(0xFF28A745), const Color(0xFFFFC107), const Color(0xFFDC3545), const Color(0xFF8B5CF6),
      const Color(0xFFF0F8FF), const Color(0xFF2D2D2D), const Color(0xFFE9ECEF),
    ];

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(titulo, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        content: Wrap(
          spacing: 10,
          runSpacing: 10,
          children: paleta.map((c) {
            final selecionada = c.value == corAtual.value;
            return GestureDetector(
              onTap: () {
                onSelecionada(c);
                Navigator.pop(ctx);
              },
              child: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: c,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: selecionada ? Colors.blueAccent : Colors.grey.shade600,
                    width: selecionada ? 3 : 1,
                  ),
                ),
                child: selecionada
                    ? Icon(Icons.check, size: 20, color: c.computeLuminance() > 0.5 ? Colors.black : Colors.white)
                    : null,
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Future<String?> _perguntarNomeArquivo(String sugestao, String extensao) async {
    final baseLimpa = sugestao.replaceAll(RegExp(r'\.(pptx|pdf)$', caseSensitive: false), '');
    final ctrl = TextEditingController(text: baseLimpa);
    return showDialog<String>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: Text('Salvar Arquivo ($extensao)', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        content: TextField(
          controller: ctrl,
          decoration: InputDecoration(
            labelText: 'Nome do arquivo ($extensao)',
            border: const OutlineInputBorder(),
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
              if (nome.isEmpty) nome = 'Apresentacao_Final';
              if (!nome.toLowerCase().endsWith(extensao)) nome = '$nome$extensao';
              Navigator.pop(ctx, nome);
            },
            child: const Text('Salvar', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Future<void> _processarESalvar({bool paraPdf = false}) async {
    if (_pptxBytes == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Carregue um arquivo PPTX primeiro.'), backgroundColor: Colors.amber),
      );
      return;
    }

    if (paraPdf) {
      final confirmar = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(Idiomas.tr('pdf_confirm_titulo'), style: const TextStyle(fontWeight: FontWeight.bold)),
          content: Text(Idiomas.tr('pdf_confirm_msg')),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: Text(Idiomas.tr('recup_btn_cancelar'), style: const TextStyle(color: Colors.red)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0078D7)),
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('OK', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      );
      if (confirmar != true || !mounted) return;
    }

    final ext = paraPdf ? '.pdf' : '.pptx';
    final nomeEscolhido = await _perguntarNomeArquivo(_nomeArquivo ?? 'Apresentacao_Final', ext);
    if (nomeEscolhido == null || !mounted) return;

    setState(() => _processando = true);

    try {
      final bytesProcessados = await ApiService.processarEstilos(
        arquivoBytes: _pptxBytes!,
        nomeArquivo: _nomeArquivo ?? "apresentacao.pptx",
        corTitulo: _colorToHex(_corTitulo),
        corCorpo: _colorToHex(_corCorpo),
        corFundoCard: _colorToHex(_corFundoCard),
        fonteTitulo: _fonteTitulo != "Padrão do Tema" ? _fonteTitulo : null,
        fonteCorpo: _fonteCorpo != "Padrão do Tema" ? _fonteCorpo : null,
        escalaImagem: _habilitarEscalaImg ? _escalaImagem.toInt() : 100,
        escalaTexto: _habilitarEscalaTexto ? _escalaTexto.toInt() : 0,
        exibirBarraLateral: _exibirBarraLateral,
        converterPdf: paraPdf,
        imagemFundoBytes: _fundoBytes,
        nomeImagemFundo: _nomeFundo,
      );

      Directory? pastaDownload = Directory('/storage/emulated/0/Download');
      if (!pastaDownload.existsSync()) {
        pastaDownload = await getExternalStorageDirectory();
      }

      final caminhoFinal = "${pastaDownload?.path ?? ''}/$nomeEscolhido";
      final arquivo = File(caminhoFinal);
      await arquivo.writeAsBytes(bytesProcessados);

      final prefs = await SharedPreferences.getInstance();
      final acao = prefs.getString('vega_pos_geracao') ?? 'sistema';

      setState(() => _processando = false);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Salvo em: $caminhoFinal'), backgroundColor: Colors.green),
      );

      if (acao == 'pasta') {
        await OpenFilex.open(pastaDownload!.path);
      } else {
        await OpenFilex.open(
          caminhoFinal,
          type: paraPdf
              ? 'application/pdf'
              : 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        );
      }
    } catch (e) {
      setState(() => _processando = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      appBar: AppBar(
        title: const Text('🎨 Estilizar Apresentação', style: TextStyle(fontWeight: FontWeight.bold)),
        elevation: 0,
      ),
      body: _processando
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  CircularProgressIndicator(color: Color(0xFF0078D7)),
                  SizedBox(height: 16),
                  Text('Processando estilos no PowerPoint...', style: TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // --- CARREGAR ARQUIVO ---
                  ElevatedButton.icon(
                    onPressed: _selecionarPptx,
                    icon: const Icon(Icons.file_upload),
                    label: Text(_pptxBytes == null ? "1. Carregar Apresentação (.pptx)" : "Trocar Arquivo: $_nomeArquivo"),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      backgroundColor: _pptxBytes == null ? const Color(0xFF0078D7) : const Color(0xFF28A745),
                      foregroundColor: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // --- PREVISÃO AO VIVO (MINI-SLIDE 16:9) ---
                  Center(
                    child: Container(
                      width: 320,
                      height: 180,
                      decoration: BoxDecoration(
                        color: _fundoBytes == null ? Colors.white : null,
                        image: _fundoBytes != null
                            ? DecorationImage(image: MemoryImage(_fundoBytes!), fit: BoxFit.cover)
                            : null,
                        border: Border.all(color: Colors.grey.shade600, width: 2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Stack(
                        children: [
                          // Barra lateral azul Vega
                          if (_exibirBarraLateral)
                            Positioned(
                              left: 0,
                              top: 0,
                              bottom: 0,
                              width: 8,
                              child: Container(
                                decoration: const BoxDecoration(
                                  color: Color(0xFF2B5C8F),
                                  borderRadius: BorderRadius.only(
                                    topLeft: Radius.circular(6),
                                    bottomLeft: Radius.circular(6),
                                  ),
                                ),
                              ),
                            ),
                          // Textos
                          Positioned(
                            left: 16,
                            top: 12,
                            width: 170,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  Idiomas.tr("lbl_preview_text_title"),
                                  style: _obterEstiloComFonte(
                                    _fonteTitulo,
                                    12 + (_habilitarEscalaTexto ? (_escalaTexto * 0.08) : 0),
                                    _corTitulo,
                                    bold: true,
                                  ),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  Idiomas.tr("lbl_preview_text_body").replaceAll("<br>", "\n"),
                                  style: _obterEstiloComFonte(
                                    _fonteCorpo,
                                    9 + (_habilitarEscalaTexto ? (_escalaTexto * 0.06) : 0),
                                    _corCorpo,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          // Card de Imagem / Bloco com escala e texto centralizado
                          Positioned(
                            right: 14,
                            top: 40,
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 150),
                              width: 88 * (_habilitarEscalaImg ? (_escalaImagem / 100.0) : 1.0),
                              height: 88 * (_habilitarEscalaImg ? (_escalaImagem / 100.0) : 1.0),
                              alignment: Alignment.center,
                              decoration: BoxDecoration(
                                color: _corFundoCard,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: Colors.white60, width: 1),
                              ),
                              child: Text(
                                Idiomas.tr("lbl_preview_placeholder_img"),
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 10,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // --- PRESETS ---
                  DropdownButtonFormField<String>(
                    value: _presetAtual,
                    decoration: InputDecoration(labelText: Idiomas.tr("lbl_presets"), border: const OutlineInputBorder()),
                    items: [
                      DropdownMenuItem(value: "Personalizado", child: Text(Idiomas.tr("preset_manual"))),
                      DropdownMenuItem(value: "Corporativo Azul", child: Text(Idiomas.tr("preset_corp"))),
                      DropdownMenuItem(value: "Dark Mode Clássico", child: Text(Idiomas.tr("preset_dark"))),
                      DropdownMenuItem(value: "Minimalista Clean", child: Text(Idiomas.tr("preset_clean"))),
                    ],
                    onChanged: (val) {
                      if (val != null) _aplicarPreset(val);
                    },
                  ),
                  const SizedBox(height: 16),

                  // --- CORES ---
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _abrirSeletorCor("Cor dos Títulos", _corTitulo, (c) => setState(() => _corTitulo = c)),
                          style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Container(width: 16, height: 16, decoration: BoxDecoration(color: _corTitulo, shape: BoxShape.circle)),
                              const SizedBox(width: 8),
                              const Text("Títulos"),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _abrirSeletorCor("Cor do Corpo", _corCorpo, (c) => setState(() => _corCorpo = c)),
                          style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Container(width: 16, height: 16, decoration: BoxDecoration(color: _corCorpo, shape: BoxShape.circle)),
                              const SizedBox(width: 8),
                              const Text("Textos"),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _abrirSeletorCor("Cor dos Cards", _corFundoCard, (c) => setState(() => _corFundoCard = c)),
                          style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Container(width: 16, height: 16, decoration: BoxDecoration(color: _corFundoCard, shape: BoxShape.circle)),
                              const SizedBox(width: 8),
                              const Text("Cards"),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // --- FONTES ---
                  DropdownButtonFormField<String>(
                    value: _fonteTitulo,
                    decoration: const InputDecoration(labelText: "Fonte dos Títulos", border: OutlineInputBorder()),
                    items: _fontesDisponiveis.map((f) => DropdownMenuItem(value: f, child: Text(f))).toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _fonteTitulo = val);
                    },
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _fonteCorpo,
                    decoration: const InputDecoration(labelText: "Fonte dos Textos (Corpo)", border: OutlineInputBorder()),
                    items: _fontesDisponiveis.map((f) => DropdownMenuItem(value: f, child: Text(f))).toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _fonteCorpo = val);
                    },
                  ),
                  const SizedBox(height: 16),

                  // --- IMAGEM DE FUNDO ---
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _selecionarImagemFundo,
                          icon: const Icon(Icons.wallpaper),
                          label: Text(_fundoBytes == null ? "4. Fundo do Slide (Opcional)" : "Fundo: $_nomeFundo"),
                        ),
                      ),
                      if (_fundoBytes != null)
                        IconButton(
                          icon: const Icon(Icons.clear, color: Colors.red),
                          onPressed: () => setState(() {
                            _fundoBytes = null;
                            _nomeFundo = null;
                          }),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // --- SLIDERS GEOMÉTRICOS ---
                  SwitchListTile(
                    title: Text("${Idiomas.tr('chk_scale')} (${_escalaImagem.toInt()}%)"),
                    value: _habilitarEscalaImg,
                    onChanged: (v) => setState(() => _habilitarEscalaImg = v),
                  ),
                  if (_habilitarEscalaImg)
                    Slider(
                      min: 10,
                      max: 200,
                      value: _escalaImagem,
                      divisions: 19,
                      label: "${_escalaImagem.toInt()}%",
                      onChanged: (v) => setState(() => _escalaImagem = v),
                    ),

                  SwitchListTile(
                    title: Text("${Idiomas.tr('chk_text_scale')} (${_escalaTexto.toInt()}%)"),
                    value: _habilitarEscalaTexto,
                    onChanged: (v) => setState(() => _habilitarEscalaTexto = v),
                  ),
                  if (_habilitarEscalaTexto)
                    Slider(
                      min: 1,
                      max: 150,
                      value: _escalaTexto,
                      divisions: 30,
                      label: "${_escalaTexto.toInt()}%",
                      onChanged: (v) => setState(() => _escalaTexto = v),
                    ),

                  CheckboxListTile(
                    title: Text(Idiomas.tr("chk_notes")),
                    value: _inserirNotasApresentador,
                    onChanged: (v) => setState(() => _inserirNotasApresentador = v ?? true),
                  ),

                  CheckboxListTile(
                    title: Text(Idiomas.tr("chk_barra_lateral")),
                    value: _exibirBarraLateral,
                    onChanged: (v) => setState(() => _exibirBarraLateral = v ?? true),
                  ),
                  const SizedBox(height: 20),

                  // --- BOTÃO 6: PROCESSAR E SALVAR (VERMELHO DESTAQUE) ---
                  ElevatedButton(
                    onPressed: _pptxBytes == null ? null : () => _processarESalvar(paraPdf: false),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: const Color(0xFFA8201A),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: Text(
                      Idiomas.tr("btn_save"),
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // --- BOTÃO 7: CONVERTER PARA PDF (CINZA SECUNDÁRIO COM CONFIRMAÇÃO) ---
                  ElevatedButton(
                    onPressed: _pptxBytes == null ? null : () => _processarESalvar(paraPdf: true),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      backgroundColor: const Color(0xFF333333),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: Text(
                      Idiomas.tr("btn_pdf"),
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                  ),
                  const SizedBox(height: 30),
                ],
              ),
            ),
    );
  }
}