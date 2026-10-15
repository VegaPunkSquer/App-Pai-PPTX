import 'dart:math' as math;
import 'package:flutter/material.dart';

class ModeloFormaInfo {
  final String rotulo;
  final String codigo;
  final String descricao;
  final bool fixoEmQuatro;

  const ModeloFormaInfo(this.rotulo, this.codigo, this.descricao, this.fixoEmQuatro);
}

class SeletorFormaModal extends StatefulWidget {
  const SeletorFormaModal({super.key});

  @override
  State<SeletorFormaModal> createState() => _SeletorFormaModalState();
}

class _SeletorFormaModalState extends State<SeletorFormaModal> {
  static const Map<String, List<ModeloFormaInfo>> catalogo = {
    "Ciclos e Relações": [
      ModeloFormaInfo("🔄 Ciclo Radial Clássico", "ciclo_radial", "Núcleo central com satélites ao redor conectados por linhas.", false),
      ModeloFormaInfo("🔁 Ciclo com Setas Curvas", "ciclo_setas", "Anel de etapas sequenciais indicando ciclo e feedback contínuo.", false),
      ModeloFormaInfo("💎 Diamante Central", "diamante_central", "Losango central em destaque conectado a 4 satélites diagonais.", true),
      ModeloFormaInfo("🛑 Colmeia Hexagonal", "grid_hexagonos", "Arranjo modular de hexágonos regulares encaixados pelas arestas.", false),
    ],
    "Processos e Fluxos": [
      ModeloFormaInfo("⏩ Processo em Chevron", "processo_chevron", "Setas pontudas encaixadas horizontalmente indicando progressão.", false),
      ModeloFormaInfo("〰️ Linha do Tempo Zig-Zag", "timeline_zigzag", "Eixo horizontal com marcos alternando acima e abaixo da linha.", false),
      ModeloFormaInfo("🌪️ Funil de Conversão", "funil_conversao", "Camadas trapezoidais decrescentes até a etapa final.", false),
      ModeloFormaInfo("📶 Escada de Crescimento", "escada_crescimento", "Degraus ascendentes indicando elevação de nível ou maturidade.", false),
    ],
    "Hierarquia e Pirâmides": [
      ModeloFormaInfo("🔺 Pirâmide Hierárquica", "piramide", "Triângulo no topo com trapézios empilhados em base crescente.", false),
      ModeloFormaInfo("🔻 Pirâmide Invertida", "piramide_invertida", "Base superior larga afunilando para o objetivo central na base.", false),
      ModeloFormaInfo("🌳 Organograma / Árvore", "organograma", "Nó raiz de liderança ramificando para equipes subordinadas.", false),
    ],
    "Matrizes e Comparações": [
      ModeloFormaInfo("🔲 Matriz 2x2 (SWOT/FOFA)", "matriz_2x2", "Quatro quadrantes para análise estratégica com eixos cartesianos.", true),
      ModeloFormaInfo("🎯 Quatro Cantos (Four Corners)", "quatro_cantos", "Objetivo central cercado por 4 pilares fundamentais.", true),
      ModeloFormaInfo("🏛️ Pilares Comparativos", "pilares_comparativos", "Colunas verticais estilizadas para comparar itens lado a lado.", false),
    ],
  };

  late String _categoriaAtual;
  late ModeloFormaInfo _modeloAtual;
  int _qtdItens = 5;

  @override
  void initState() {
    super.initState();
    _categoriaAtual = catalogo.keys.first;
    _modeloAtual = catalogo[_categoriaAtual]!.first;
  }

  void _trocarCategoria(String novaCat) {
    setState(() {
      _categoriaAtual = novaCat;
      _modeloAtual = catalogo[_categoriaAtual]!.first;
      if (_modeloAtual.fixoEmQuatro) {
        _qtdItens = 4;
      }
    });
  }

  void _trocarModelo(ModeloFormaInfo novoMod) {
    setState(() {
      _modeloAtual = novoMod;
      if (_modeloAtual.fixoEmQuatro) {
        _qtdItens = 4;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final listaModelos = catalogo[_categoriaAtual] ?? [];

    return Dialog(
      backgroundColor: isDark ? const Color(0xFF1E1E1E) : Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Catálogo de Formas / SmartArt",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Categoria
            DropdownButtonFormField<String>(
              value: _categoriaAtual,
              isExpanded: true,
              decoration: const InputDecoration(
                labelText: "Categoria de Formas",
                border: OutlineInputBorder(),
              ),
              items: catalogo.keys
                  .map((c) => DropdownMenuItem(value: c, child: Text(c, style: const TextStyle(fontWeight: FontWeight.bold))))
                  .toList(),
              onChanged: (val) {
                if (val != null) _trocarCategoria(val);
              },
            ),
            const SizedBox(height: 14),

            // Modelo Específico
            DropdownButtonFormField<ModeloFormaInfo>(
              value: _modeloAtual,
              isExpanded: true,
              decoration: const InputDecoration(
                labelText: "Modelo Específico",
                border: OutlineInputBorder(),
              ),
              items: listaModelos
                  .map((m) => DropdownMenuItem(value: m, child: Text(m.rotulo)))
                  .toList(),
              onChanged: (val) {
                if (val != null) _trocarModelo(val);
              },
            ),
            const SizedBox(height: 14),

            // Quantidade de Itens
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _modeloAtual.fixoEmQuatro ? "Quantidade de itens (Fixo em 4):" : "Quantidade de itens: $_qtdItens",
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                if (!_modeloAtual.fixoEmQuatro)
                  DropdownButton<int>(
                    value: _qtdItens,
                    items: [3, 4, 5, 6, 7, 8]
                        .map((n) => DropdownMenuItem(value: n, child: Text("$n itens")))
                        .toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _qtdItens = val);
                    },
                  ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              _modeloAtual.descricao,
              style: TextStyle(fontSize: 12, color: isDark ? Colors.white60 : Colors.black54),
            ),
            const SizedBox(height: 16),

            // Canvas de Pré-visualização Gráfica Real
            Container(
              height: 190,
              decoration: BoxDecoration(
                color: const Color(0xFF1A1A1A),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF444444)),
              ),
              child: CustomPaint(
                painter: _PreviewFormaPainter(
                  tipo: _modeloAtual.codigo,
                  qtdItens: _qtdItens,
                ),
              ),
            ),
            const SizedBox(height: 20),

            ElevatedButton(
              onPressed: () {
                final tag = "[FORMA: ${_modeloAtual.codigo} | ITENS: $_qtdItens]";
                Navigator.pop(context, tag);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6F42C1),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: const Text(
                "✔ Inserir Esta Forma no Prompt",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PreviewFormaPainter extends CustomPainter {
  final String tipo;
  final int qtdItens;

  _PreviewFormaPainter({required this.tipo, required this.qtdItens});

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;
    final n = math.max(qtdItens, 1);

    final paintPrimario = Paint()
      ..color = const Color(0xFF0078D7)
      ..style = PaintingStyle.fill;
    final paintSecundario = Paint()
      ..color = const Color(0xFF4A4A4A)
      ..style = PaintingStyle.fill;
    final paintLinha = Paint()
      ..color = const Color(0xFF777777)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    final cx = w / 2;
    final cy = h / 2;

    if (tipo == "ciclo_radial") {
      final raio = math.min(w, h) / 3.1;
      for (int i = 0; i < n; i++) {
        final ang = (2 * math.pi / n) * i - (math.pi / 2);
        final sx = cx + raio * math.cos(ang);
        final sy = cy + raio * math.sin(ang);
        canvas.drawLine(Offset(cx, cy), Offset(sx, sy), paintLinha);
        canvas.drawCircle(Offset(sx, sy), 12, paintSecundario);
      }
      canvas.drawCircle(Offset(cx, cy), 18, paintPrimario);
    } else if (tipo == "ciclo_setas") {
      final raio = math.min(w, h) / 3.1;
      canvas.drawCircle(Offset(cx, cy), raio, paintLinha);
      for (int i = 0; i < n; i++) {
        final ang = (2 * math.pi / n) * i - (math.pi / 2);
        final bx = cx + raio * math.cos(ang);
        final by = cy + raio * math.sin(ang);
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(bx, by), width: 32, height: 22), const Radius.circular(4)),
          i == 0 ? paintPrimario : paintSecundario,
        );
      }
    } else if (tipo == "diamante_central") {
      final path = Path()
        ..moveTo(cx, cy - 24)
        ..lineTo(cx + 24, cy)
        ..lineTo(cx, cy + 24)
        ..lineTo(cx - 24, cy)
        ..close();
      canvas.drawPath(path, paintPrimario);
      final offsets = [
        Offset(cx, cy - 48),
        Offset(cx + 55, cy),
        Offset(cx, cy + 48),
        Offset(cx - 55, cy),
      ];
      for (int i = 0; i < math.min(4, n); i++) {
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromCenter(center: offsets[i], width: 38, height: 20), const Radius.circular(4)),
          paintSecundario,
        );
      }
    } else if (tipo == "grid_hexagonos") {
      final startX = (w - (n * 34)) / 2 + 17;
      for (int i = 0; i < n; i++) {
        final hx = startX + i * 34;
        final hy = (i % 2 == 0) ? cy - 8 : cy + 8;
        canvas.drawCircle(Offset(hx, hy), 15, i % 2 == 0 ? paintPrimario : paintSecundario);
      }
    } else if (tipo == "processo_chevron" || tipo == "processo_linear") {
      final larg = (w - 40) / n;
      for (int i = 0; i < n; i++) {
        final bx = 20 + i * larg;
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(bx + 2, cy - 20, larg - 4, 40), const Radius.circular(4)),
          i == 0 ? paintPrimario : paintSecundario,
        );
      }
    } else if (tipo == "timeline_zigzag") {
      canvas.drawLine(Offset(20, cy), Offset(w - 20, cy), paintLinha);
      final gap = (w - 40) / n;
      for (int i = 0; i < n; i++) {
        final nx = 20 + (i + 0.5) * gap;
        canvas.drawCircle(Offset(nx, cy), 4, paintPrimario);
        final cardY = (i % 2 == 0) ? cy - 32 : cy + 12;
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(nx - 18, cardY, 36, 20), const Radius.circular(4)),
          paintSecundario,
        );
      }
    } else if (tipo == "funil_conversao" || tipo == "piramide_invertida") {
      final topY = 20.0;
      final hTotal = h - 40.0;
      for (int i = 0; i < n; i++) {
        final y = topY + (i / n) * hTotal;
        final alt = (hTotal / n) - 3;
        final larg = (w - 50) * (1.0 - (i / (n * 1.35)));
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(cx - larg / 2, y, larg, alt), const Radius.circular(4)),
          i == 0 ? paintPrimario : paintSecundario,
        );
      }
    } else if (tipo == "escada_crescimento") {
      final larg = (w - 40) / n;
      for (int i = 0; i < n; i++) {
        final alt = 25.0 + (h - 65.0) * ((i + 1) / n);
        final bx = 20 + i * larg;
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(bx + 2, h - 20 - alt, larg - 4, alt), const Radius.circular(4)),
          i == n - 1 ? paintPrimario : paintSecundario,
        );
      }
    } else if (tipo == "piramide") {
      final topY = 20.0;
      final hTotal = h - 40.0;
      for (int i = 0; i < n; i++) {
        final y = topY + (i / n) * hTotal;
        final alt = (hTotal / n) - 3;
        final larg = (w - 50) * ((i + 1) / n);
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(cx - larg / 2, y, larg, alt), const Radius.circular(4)),
          i == 0 ? paintPrimario : paintSecundario,
        );
      }
    } else if (tipo == "organograma") {
      canvas.drawRRect(
        RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(cx, 32), width: 60, height: 24), const Radius.circular(4)),
        paintPrimario,
      );
      final larg = (w - 40) / n;
      for (int i = 0; i < n; i++) {
        final fx = 20 + (i + 0.5) * larg;
        canvas.drawLine(Offset(cx, 44), Offset(fx, 85), paintLinha);
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(fx, 105), width: larg - 8, height: 40), const Radius.circular(4)),
          paintSecundario,
        );
      }
    } else if (tipo == "matriz_2x2" || tipo == "quatro_cantos") {
      final bw = (w - 60) / 2;
      final bh = (h - 50) / 2;
      final coords = [
        Offset(20, 18),
        Offset(35 + bw, 18),
        Offset(20, 28 + bh),
        Offset(35 + bw, 28 + bh),
      ];
      for (int i = 0; i < 4; i++) {
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(coords[i].dx, coords[i].dy, bw, bh), const Radius.circular(4)),
          i == 0 ? paintPrimario : paintSecundario,
        );
      }
      if (tipo == "quatro_cantos") {
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromCenter(center: Offset(cx, cy), width: 54, height: 34), const Radius.circular(6)),
          paintPrimario,
        );
      }
    } else {
      // pilares_comparativos
      final larg = (w - 40) / n;
      for (int i = 0; i < n; i++) {
        final bx = 20 + i * larg;
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(bx + 3, 24, larg - 6, h - 48), const Radius.circular(4)),
          paintSecundario,
        );
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(bx + 3, 24, larg - 6, 16), const Radius.circular(4)),
          paintPrimario,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _PreviewFormaPainter oldDelegate) {
    return oldDelegate.tipo != tipo || oldDelegate.qtdItens != qtdItens;
  }
}