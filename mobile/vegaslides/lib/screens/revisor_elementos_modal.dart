import 'package:flutter/material.dart';
import '../utils/idiomas.dart';

class RevisorElementosModal extends StatefulWidget {
  final List<dynamic> slides;

  const RevisorElementosModal({super.key, required this.slides});

  @override
  State<RevisorElementosModal> createState() => _RevisorElementosModalState();
}

class _RevisorElementosModalState extends State<RevisorElementosModal> {
  late List<Map<String, dynamic>> _elementos;
  int _idxAtual = 0;
  bool _modoLista = false;

  @override
  void initState() {
    super.initState();
    _elementos = _extrairElementos();
  }

  List<Map<String, dynamic>> _extrairElementos() {
    final List<Map<String, dynamic>> lista = [];
    for (int sIdx = 0; sIdx < widget.slides.length; sIdx++) {
      final slide = widget.slides[sIdx] as Map<String, dynamic>;
      if (slide.containsKey('smartart') && slide['smartart'] is Map) {
        lista.add({
          "tipo": "forma",
          "slide_idx": sIdx,
          "sub_idx": 0,
          "slide_ref": slide,
          "dado": slide['smartart'],
        });
      } else if (slide['topicos'] is List && (slide['topicos'] as List).isNotEmpty) {
        final topicos = slide['topicos'] as List;
        final limite = topicos.length > 3 ? 3 : topicos.length;
        for (int tIdx = 0; tIdx < limite; tIdx++) {
          final topico = topicos[tIdx] as Map<String, dynamic>;
          topico['escala_texto'] ??= 0;
          lista.add({
            "tipo": "card",
            "slide_idx": sIdx,
            "sub_idx": tIdx,
            "slide_ref": slide,
            "dado": topico,
          });
        }
      }
    }
    return lista;
  }

  Widget _construirPreviewSlide16x9(Map<String, dynamic> slideDados, int subIdxDestaque) {
    final tituloSlide = (slideDados['titulo'] ?? '').toString().toUpperCase();
    final topicos = (slideDados['topicos'] as List?) ?? [];
    final numCards = topicos.length > 3 ? 3 : topicos.length;

    return AspectRatio(
      aspectRatio: 16 / 9,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFF555555), width: 2),
        ),
        child: Row(
          children: [
            // Barra lateral azul Vega
            Container(width: 8, color: const Color(0xFF2B5C8F)),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      tituloSlide,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Color(0xFF1E3C5A),
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Expanded(
                      child: numCards == 0
                          ? const SizedBox.shrink()
                          : Row(
                              children: List.generate(numCards, (idx) {
                                final t = topicos[idx] as Map<String, dynamic>;
                                final ehFoco = idx == subIdxDestaque;
                                final textoC = (t['texto'] ?? '').toString();
                                final escala = (t['escala_texto'] ?? 0) as int;

                                double baseTam = 8.5;
                                if (textoC.length > 120) {
                                  baseTam = 6.5;
                                } else if (textoC.length > 60) {
                                  baseTam = 7.5;
                                }
                                final double fonteFinal = (baseTam + (escala / 20.0)).clamp(5.5, 13.0);

                                return Expanded(
                                  child: Container(
                                    margin: EdgeInsets.only(right: idx < numCards - 1 ? 6 : 0),
                                    padding: const EdgeInsets.all(6),
                                    decoration: BoxDecoration(
                                      color: ehFoco ? Colors.white : const Color(0xFFF5F7FA),
                                      borderRadius: BorderRadius.circular(6),
                                      border: Border.all(
                                        color: ehFoco ? const Color(0xFF0078D7) : const Color(0xFFCCD5E0),
                                        width: ehFoco ? 2 : 1,
                                      ),
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          "${t['icone'] ?? '📌'} ${t['titulo'] ?? ''}",
                                          maxLines: 2,
                                          overflow: TextOverflow.ellipsis,
                                          textAlign: TextAlign.center,
                                          style: const TextStyle(
                                            color: Color(0xFF2B5C8F),
                                            fontWeight: FontWeight.bold,
                                            fontSize: 8,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Expanded(
                                          child: Text(
                                            textoC,
                                            overflow: TextOverflow.fade,
                                            style: TextStyle(
                                              color: const Color(0xFF444444),
                                              fontSize: fonteFinal,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                );
                              }),
                            ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _construirEditorElemento(Map<String, dynamic> el, {bool exibirMiniatura = false}) {
    final slideDados = el['slide_ref'] as Map<String, dynamic>;
    final sIdx = el['slide_idx'] as int;
    final subIdx = el['sub_idx'] as int;
    final titSlide = (slideDados['titulo'] ?? 'Slide').toString();
    final dado = el['dado'] as Map<String, dynamic>;

    final int escalaAtual = (dado['escala_texto'] ?? 0) as int;
    final String textoAtual = (dado['texto'] ?? '').toString();
    final int limiteSeguro = textoAtual.length > 120 ? 15 : (textoAtual.length > 60 ? 30 : 50);
    final bool transbordo = escalaAtual > limiteSeguro;

    return Card(
      color: const Color(0xFF262626),
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: const BorderSide(color: Color(0xFF444444)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              "Slide ${sIdx + 1}: $titSlide — Card ${subIdx + 1}",
              style: const TextStyle(color: Color(0xFF0078D7), fontWeight: FontWeight.bold, fontSize: 13),
            ),
            const SizedBox(height: 10),
            if (exibirMiniatura) ...[
              _construirPreviewSlide16x9(slideDados, subIdx),
              const SizedBox(height: 12),
            ],
            Text(Idiomas.tr("rev_card_tit_lbl"), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 6),
            TextFormField(
              key: ValueKey("tit_${sIdx}_$subIdx"),
              initialValue: (dado['titulo'] ?? '').toString(),
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                isDense: true,
                filled: true,
                fillColor: Color(0xFF1A1A1A),
                border: OutlineInputBorder(),
              ),
              onChanged: (val) {
                setState(() => dado['titulo'] = val);
              },
            ),
            const SizedBox(height: 12),
            Text(Idiomas.tr("rev_card_corpo_lbl"), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 6),
            TextFormField(
              key: ValueKey("txt_${sIdx}_$subIdx"),
              initialValue: textoAtual,
              maxLines: 3,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                isDense: true,
                filled: true,
                fillColor: Color(0xFF1A1A1A),
                border: OutlineInputBorder(),
              ),
              onChanged: (val) {
                setState(() => dado['texto'] = val);
              },
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Text(Idiomas.tr("rev_card_tam_lbl"), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 13)),
                Expanded(
                  child: Slider(
                    min: -20,
                    max: 50,
                    divisions: 14,
                    value: escalaAtual.toDouble(),
                    activeColor: const Color(0xFF0078D7),
                    onChanged: (v) {
                      setState(() => dado['escala_texto'] = v.toInt());
                    },
                  ),
                ),
                Text(
                  escalaAtual > 0 ? "+$escalaAtual%" : "$escalaAtual%",
                  style: const TextStyle(color: Color(0xFF0078D7), fontWeight: FontWeight.bold),
                ),
              ],
            ),
            if (transbordo)
              Text(
                Idiomas.tr("rev_aviso_transbordo"),
                style: const TextStyle(color: Colors.amber, fontWeight: FontWeight.bold, fontSize: 12),
              ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_elementos.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: Text(Idiomas.tr("rev_titulo"))),
        body: Center(child: Text(Idiomas.tr("rev_vazio"))),
        bottomNavigationBar: Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton(
            onPressed: () => Navigator.pop(context, widget.slides),
            child: Text(Idiomas.tr("rev_btn_concluir")),
          ),
        ),
      );
    }

    final elAtual = _elementos[_idxAtual];

    return Scaffold(
      appBar: AppBar(
        title: Text(Idiomas.tr("rev_titulo"), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          children: [
            // Barra de alternância Foco vs Lista
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => setState(() => _modoLista = false),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: !_modoLista ? const Color(0xFF0078D7) : const Color(0xFF333333),
                      foregroundColor: Colors.white,
                    ),
                    child: Text(Idiomas.tr("rev_modo_foco"), style: const TextStyle(fontSize: 12)),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => setState(() => _modoLista = true),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _modoLista ? const Color(0xFF0078D7) : const Color(0xFF333333),
                      foregroundColor: Colors.white,
                    ),
                    child: Text(Idiomas.tr("rev_modo_lista"), style: const TextStyle(fontSize: 12)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            if (!_modoLista) ...[
              // Navegador Superior Foco Individual
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  OutlinedButton(
                    onPressed: _idxAtual > 0 ? () => setState(() => _idxAtual--) : null,
                    child: Text(Idiomas.tr("rev_btn_anterior")),
                  ),
                  Text(
                    "${_idxAtual + 1} / ${_elementos.length}",
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  OutlinedButton(
                    onPressed: _idxAtual < _elementos.length - 1 ? () => setState(() => _idxAtual++) : null,
                    child: Text(Idiomas.tr("rev_btn_proximo")),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              _construirPreviewSlide16x9(elAtual['slide_ref'], elAtual['sub_idx']),
              const SizedBox(height: 12),
              Expanded(
                child: SingleChildScrollView(
                  child: _construirEditorElemento(elAtual, exibirMiniatura: false),
                ),
              ),
            ] else ...[
              // Modo Lista Completa com miniatura em cada card
              Expanded(
                child: ListView.builder(
                  itemCount: _elementos.length,
                  itemBuilder: (ctx, i) => _construirEditorElemento(_elementos[i], exibirMiniatura: true),
                ),
              ),
            ],
          ],
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: ElevatedButton(
            onPressed: () => Navigator.pop(context, widget.slides),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF28A745),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 15),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            child: Text(
              Idiomas.tr("rev_btn_concluir"),
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ),
        ),
      ),
    );
  }
}