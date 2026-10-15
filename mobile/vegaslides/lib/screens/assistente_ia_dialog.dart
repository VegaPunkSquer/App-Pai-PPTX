import 'package:flutter/material.dart';
import '../utils/idiomas.dart';

class AssistenteIADialog extends StatefulWidget {
  const AssistenteIADialog({super.key});

  @override
  State<AssistenteIADialog> createState() => _AssistenteIADialogState();
}

class _AssistenteIADialogState extends State<AssistenteIADialog> {
  int _passoAtual = 0;
  int _qtdSlides = 10;
  final TextEditingController _temaCtrl = TextEditingController();
  String _imgOpcao = "todos";

  @override
  void dispose() {
    _temaCtrl.dispose();
    super.dispose();
  }

  List<DropdownMenuItem<String>> _gerarOpcoesImagens() {
    final List<DropdownMenuItem<String>> itens = [
      DropdownMenuItem(value: "todos", child: Text(Idiomas.tr("ast_p3_opt_todos"))),
    ];
    for (int i = 1; i <= _qtdSlides; i++) {
      itens.add(DropdownMenuItem(value: i.toString(), child: Text("$i slide(s)")));
    }
    itens.add(DropdownMenuItem(value: "0", child: Text(Idiomas.tr("ast_p3_opt_nenhum"))));
    return itens;
  }

  String _obterTextoOpcaoImagem() {
    if (_imgOpcao == "todos") return Idiomas.tr("ast_p3_opt_todos");
    if (_imgOpcao == "0") return Idiomas.tr("ast_p3_opt_nenhum");
    return "$_imgOpcao slide(s)";
  }

  void _avancar() {
    if (_passoAtual == 2 && _temaCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Por favor, digite o tema da apresentação."), backgroundColor: Colors.amber),
      );
      return;
    }

    if (_passoAtual == 1) {
      // Garante que a opção de imagem não fique maior que o número de slides escolhido
      final num? parsed = int.tryParse(_imgOpcao);
      if (parsed != null && parsed > _qtdSlides) {
        _imgOpcao = "todos";
      }
    }

    if (_passoAtual == 4) {
      final tema = _temaCtrl.text.trim();
      String regraImg = "";
      if (_imgOpcao == "0") {
        regraImg = "NÃO inclua sugestões de imagens em nenhum slide.";
      } else if (_imgOpcao == "todos") {
        regraImg = "Inclua sugestões de imagens em TODOS os slides.";
      } else {
        regraImg = "Inclua sugestões de imagens em exatamente $_imgOpcao slides.";
      }

      final promptFinal =
          "Tema Principal: $tema\n\n[Regras do Assistente - STRICT]:\n- Crie exatamente $_qtdSlides slides.\n- $regraImg";
      Navigator.pop(context, promptFinal);
      return;
    }

    setState(() => _passoAtual++);
  }

  void _voltar() {
    if (_passoAtual > 0) {
      setState(() => _passoAtual--);
    }
  }

  Widget _construirCorpoPasso(bool isDark) {
    switch (_passoAtual) {
      case 0:
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              Idiomas.tr("ast_p0_tit"),
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              Idiomas.tr("ast_p0_msg"),
              style: const TextStyle(fontSize: 14),
              textAlign: TextAlign.center,
            ),
          ],
        );

      case 1:
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(Idiomas.tr("ast_p1_tit"), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Text(Idiomas.tr("ast_p1_msg"), style: const TextStyle(fontSize: 14)),
            const SizedBox(height: 16),
            DropdownButtonFormField<int>(
              value: _qtdSlides,
              decoration: const InputDecoration(border: OutlineInputBorder()),
              items: List.generate(20, (i) => i + 1)
                  .map((numSlide) => DropdownMenuItem(value: numSlide, child: Text("$numSlide slides")))
                  .toList(),
              onChanged: (val) {
                if (val != null) setState(() => _qtdSlides = val);
              },
            ),
          ],
        );

      case 2:
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(Idiomas.tr("ast_p2_tit"), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Text(Idiomas.tr("ast_p2_msg"), style: const TextStyle(fontSize: 14)),
            const SizedBox(height: 16),
            TextField(
              controller: _temaCtrl,
              maxLines: 4,
              decoration: const InputDecoration(
                hintText: "...",
                border: OutlineInputBorder(),
              ),
            ),
          ],
        );

      case 3:
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(Idiomas.tr("ast_p3_tit"), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Text(Idiomas.tr("ast_p3_msg"), style: const TextStyle(fontSize: 14)),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _imgOpcao,
              decoration: const InputDecoration(border: OutlineInputBorder()),
              items: _gerarOpcoesImagens(),
              onChanged: (val) {
                if (val != null) setState(() => _imgOpcao = val);
              },
            ),
          ],
        );

      case 4:
        final resumoBruto = Idiomas.tr("ast_p4_resumo")
            .replaceAll("<b>", "")
            .replaceAll("</b>", "")
            .replaceAll("<i>", "")
            .replaceAll("</i>", "");
        final partes = resumoBruto.split("{}");
        String textoMontado = resumoBruto;
        if (partes.length >= 4) {
          textoMontado =
              "${partes[0]}$_qtdSlides${partes[1]}${_temaCtrl.text.trim()}${partes[2]}${_obterTextoOpcaoImagem()}${partes[3]}";
        }

        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              Idiomas.tr("ast_p4_tit"),
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF0078D7).withOpacity(0.12),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF0078D7).withOpacity(0.4)),
              ),
              child: Text(
                textoMontado,
                style: const TextStyle(fontSize: 14),
                textAlign: TextAlign.center,
              ),
            ),
          ],
        );

      default:
        return const SizedBox.shrink();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AlertDialog(
      backgroundColor: isDark ? const Color(0xFF1E1E1E) : Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Text(Idiomas.tr("ast_title"), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
      content: SizedBox(
        width: double.maxFinite,
        child: SingleChildScrollView(
          child: _construirCorpoPasso(isDark),
        ),
      ),
      actionsAlignment: MainAxisAlignment.spaceBetween,
      actions: [
        if (_passoAtual > 0)
          TextButton(
            onPressed: _voltar,
            child: Text(Idiomas.tr("ast_btn_voltar")),
          )
        else
          const SizedBox.shrink(),
        ElevatedButton(
          onPressed: _avancar,
          style: ElevatedButton.styleFrom(
            backgroundColor: _passoAtual == 4 ? const Color(0xFF28A745) : const Color(0xFF0078D7),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
          ),
          child: Text(
            _passoAtual == 4 ? Idiomas.tr("ast_btn_gerar") : Idiomas.tr("ast_btn_avancar"),
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
      ],
    );
  }
}